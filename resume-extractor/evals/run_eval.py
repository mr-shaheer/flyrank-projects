import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

ENDPOINT = "http://localhost:8000/extract-skills"
CASES_PATH = Path(__file__).parent / "cases.json"


def run():
    cases = json.loads(CASES_PATH.read_text())
    correct = 0
    failures = []

    with httpx.Client(timeout=60) as client:
        for case in cases:
            resp = client.post(ENDPOINT, json={"resume_text": case["resume_text"]})
            if resp.status_code != 200:
                failures.append((case["id"], f"HTTP {resp.status_code}"))
                continue

            body = resp.json()
            expected = case["expected"]
            match = all(body.get(k) == v for k, v in expected.items())

            if match:
                correct += 1
            else:
                failures.append((case["id"], f"got {body}, expected {expected}"))

    total = len(cases)
    print(f"Score: {correct}/{total} ({datetime.now(timezone.utc).date()})")
    if failures:
        print("Failed cases:")
        for case_id, reason in failures:
            print(f"  #{case_id}: {reason}")


if __name__ == "__main__":
    run()