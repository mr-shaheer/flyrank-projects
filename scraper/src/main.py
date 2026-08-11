import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, HttpUrl, ValidationError
import time
import json
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/your-user/your-repo)"}

Path("cache").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

stats = {"cache_hits": 0, "requests_made": 0}


class Book(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: str

def fetch_page(url):
    """Return (html, from_cache). Caches to disk; retries once on timeout/5xx only."""
    cache_file = Path("cache/" + url.replace(BASE_URL, "").replace("/", "_") + ".html")

    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")
        print(f"CACHE HIT: {url} ({len(html)} bytes)")
        stats["cache_hits"] += 1
        return html, True

    for attempt in range(2):
        try:
            print("Fetching:", url)
            stats["requests_made"] += 1
            response = requests.get(url, headers=HEADERS, timeout=5)

            if response.status_code >= 500 and attempt == 0:
                time.sleep(1)
                continue
            if response.status_code != 200:
                return None, False

            print(f"FETCH: {url} -> 200 ({len(response.text)} bytes)")
            cache_file.write_text(response.text, encoding="utf-8")
            return response.text, False

        except requests.Timeout:
            if attempt == 0:
                time.sleep(1)
                continue
            return None, False
        except requests.RequestException:
            return None, False

    return None, False


def extract_book(book_html, product_url, source_page):
    """Parse one book detail page into a raw dict, scoped to the main product block."""
    soup = BeautifulSoup(book_html, "html.parser")
    main = soup.select_one("div.product_main")
    if main is None:
        return None

    title_tag = main.find("h1")
    price_tag = main.find("p", class_="price_color")
    rating_tag = main.find("p", class_="star-rating")
    availability_tag = main.find("p", class_="instock")
    description_tag = soup.select_one("#product_description + p")

    if not title_tag or not price_tag or not rating_tag:
        return {"_error": "Missing required data"}

    rating_classes = rating_tag.get("class", [])
    price_text = price_tag.get_text(strip=True)

    try:
        price_gbp = float(price_text.replace("£", "").replace("Â", ""))
    except ValueError:
        return {"_error": "Invalid price"}

    return {
        "title": title_tag.get_text(strip=True),
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_tag.get_text(" ", strip=True) if availability_tag else "",
        "rating_text": rating_classes[1] if len(rating_classes) > 1 else "",
        "description": description_tag.get_text(strip=True) if description_tag else None,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    start = datetime.now(timezone.utc)
    all_books, errors, failed_pages = [], [], []

    try:
        robots = requests.get(urljoin(BASE_URL, "robots.txt"), headers=HEADERS, timeout=5)
        print("robots.txt:", robots.status_code)
    except requests.RequestException:
        print("robots.txt check failed")

    catalogue_url = BASE_URL
    catalogue_pages = 0
    book_urls = {}

    while catalogue_url and catalogue_pages < 3:
        html, cached = fetch_page(catalogue_url)
        if html is None:
            failed_pages.append(catalogue_url)
            break

        catalogue_pages += 1
        soup = BeautifulSoup(html, "html.parser")

        for book in soup.find_all("article", class_="product_pod"):
            a_tag = book.find("a")
            if a_tag:
                full_link = urljoin(catalogue_url, a_tag.get("href"))
                book_urls.setdefault(full_link, catalogue_url)  # first-seen page wins

        next_tag = soup.find("li", class_="next")
        catalogue_url = urljoin(catalogue_url, next_tag.find("a").get("href")) if next_tag else None

        if not cached:
            time.sleep(1)

    print(f"catalogue_pages={catalogue_pages} discovered={len(book_urls)} unique_urls={len(book_urls)}")

    for product_url, source_page in book_urls.items():
        book_html, cached = fetch_page(product_url)
        if book_html is None:
            failed_pages.append(product_url)
            continue

        raw = extract_book(book_html, product_url, source_page)
        if raw is None or "_error" in raw:
            errors.append({"url": product_url, "reason": raw["_error"] if raw else "No product block found"})
        else:
            try:
                all_books.append(Book.model_validate(raw).model_dump(mode="json"))
            except ValidationError as e:
                errors.append({"url": product_url, "reason": str(e)})

        if not cached:
            time.sleep(1)

    print(f"detail_pages={len(book_urls)}")

    all_books = list({b["product_url"]: b for b in all_books}.values())

    Path("output/books.json").write_text(json.dumps(all_books, indent=4, ensure_ascii=False), encoding="utf-8")
    Path("output/errors.json").write_text(json.dumps(errors, indent=4), encoding="utf-8")

    duration = (datetime.now(timezone.utc) - start).total_seconds()
    report = {
        "start_time": start.isoformat(),
        "duration_seconds": round(duration, 2),
        "catalogue_pages": catalogue_pages,
        "discovered_urls": len(book_urls),
        "cache_hits": stats["cache_hits"],
        "requests_made": stats["requests_made"],
        "valid_records": len(all_books),
        "invalid_records": len(errors),
        "failed_pages": len(failed_pages),
    }
    Path("output/run-report.json").write_text(json.dumps(report, indent=4), encoding="utf-8")

    print("\nScraper finished")
    print("Books:", len(all_books), "| Errors:", len(errors), "| Failed pages:", len(failed_pages))
    print("Saved to output/")


if __name__ == "__main__":
    main()