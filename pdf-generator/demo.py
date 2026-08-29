"""
demo.py
-------
End-to-end demo of the pipeline, no HTTP server needed:

    python demo.py

1. Initializes + seeds the SQLite DB.
2. Enqueues a sales report job ("on demand").
3. Polls job status until it's done (simulating what a client/API
   consumer would do).
4. Prints the stored file path (the "link" to the artifact).
"""

import time
from app.db import init_db
from app import jobs


def main():
    print("Initializing database...")
    init_db(seed=True)

    print("Enqueuing sales report job (on demand)...")
    handle = jobs.enqueue_sales_report("2026-01-01", "2026-03-31")
    print(f"  -> job id: {handle.id}  status: {handle.status}")

    print("Polling job status...")
    while True:
        row = jobs.get_job(handle.id)
        print(f"  -> status: {row['status']}")
        if row["status"] in ("done", "failed"):
            break
        time.sleep(0.3)

    if row["status"] == "done":
        print(f"\nReport ready -> {row['file_path']}")
        print("(Only this path was ever passed around -- not the PDF bytes.)")
    else:
        print(f"\nJob failed:\n{row['error']}")


if __name__ == "__main__":
    main()
