# Books Scraper

A small Python scraper for [books.toscrape.com](https://books.toscrape.com/) that walks the catalogue, visits each book's detail page, validates the extracted data with Pydantic, and writes the results to `output/` as JSON.

## Features

- Crawls up to 3 catalogue pages and discovers all book detail-page URLs
- Fetches each detail page and parses title, price, availability, rating, and description
- Validates every record against a `Book` schema before saving
- Caches every fetched page to disk (`cache/`) so re-runs don't re-hit the network
- Retries once on timeout or 5xx responses
- Writes a run report summarizing pages crawled, cache hits, requests made, and record counts

## Requirements

- Python 3.10+ (uses `str | None` union syntax)
- Dependencies listed in `requirements.txt`:
  - `requests`
  - `beautifulsoup4`
  - `pydantic`

## Setup

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

On first run, the scraper fetches pages from the live site and caches them under `cache/`. On subsequent runs, it reuses the cache instead of making new requests, so if you want a fresh scrape, clear `cache/` first:

```bash
rm -rf cache/*
python src/main.py
```

## Output

Each run writes three files to `output/`:

| File | Description |
|---|---|
| `books.json` | Validated book records (title, price, availability, rating, description, source page, timestamp) |
| `errors.json` | Records that failed parsing or validation, with the URL and reason |
| `run-report.json` | Run stats: duration, catalogue pages crawled, URLs discovered, cache hits, requests made, valid/invalid record counts, failed pages |

`output/` and `cache/` are both generated data and are excluded from version control via `.gitignore`.

## Project Structure

```
scraper/
├── src/
│   └── main.py          # Scraper entry point
├── cache/                # Cached HTML pages (gitignored)
├── output/               # Scrape results (gitignored)
├── requirements.txt
└── README.md
```

## Notes

- The scraper identifies itself via a custom `User-Agent` header and checks `robots.txt` before crawling.
- Requests are polite by default — a 1-second delay is added between live (non-cached) requests.
- This project is for educational/demo purposes; books.toscrape.com is a sandbox site built for scraping practice.