"""Quick end-to-end smoke test. Run with: python test_smoke.py
Exercises: auth -> resume -> scrape (offline fallback) -> LLM scoring
(offline fallback) -> matches -> PDF report -> application tracking.
No API keys or internet access required to pass.
"""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_smoke.db")

from fastapi.testclient import TestClient
from app.main import app


def main():
    with TestClient(app) as client:
        _run_checks(client)


def _run_checks(client):
        # 1. Register + login
        r = client.post("/auth/register", json={"email": "intern@example.com", "password": "hunter2"})
        assert r.status_code == 201, r.text
        print("✓ register")

        r = client.post("/auth/login", data={"username": "intern@example.com", "password": "hunter2"})
        assert r.status_code == 200, r.text
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ login")

        # 2. Upload resume
        resume_text = (
            "Backend engineer experienced in Python, FastAPI, REST APIs, Postgres, "
            "background jobs, and integrating LLMs into production systems."
        )
        r = client.post("/resumes", json={"content_text": resume_text}, headers=headers)
        assert r.status_code == 201, r.text
        print("✓ resume uploaded")

        # 3. Scrape jobs (will use offline fallback sample since no network in this sandbox)
        r = client.post("/jobs/scrape", headers=headers)
        assert r.status_code == 200, r.text
        print(f"✓ scrape: {r.json()}")

        r = client.get("/jobs", headers=headers)
        assert r.status_code == 200
        jobs = r.json()
        assert len(jobs) > 0
        print(f"✓ {len(jobs)} jobs listed (cached read-through)")

        # 4. Run matching (LLM fallback scorer since no ANTHROPIC_API_KEY in this test env)
        r = client.post("/matches/run", headers=headers)
        assert r.status_code == 200, r.text
        print(f"✓ matching run: {r.json()}")

        r = client.get("/matches/me", headers=headers)
        assert r.status_code == 200
        matches = r.json()
        assert len(matches) > 0
        print(f"✓ {len(matches)} matches, top score = {max(m['score'] for m in matches)}")

        # 5. Generate + download PDF report
        r = client.get("/reports/me", headers=headers)
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert len(r.content) > 500
        print(f"✓ PDF report generated ({len(r.content)} bytes)")

        # 6. Email report (will skip gracefully — no SMTP configured in test env)
        r = client.post("/reports/email-me", headers=headers)
        assert r.status_code == 200, r.text
        print(f"✓ email endpoint: {r.json()}")

        # 7. Track an application
        job_id = jobs[0]["id"]
        r = client.post("/applications", json={"job_id": job_id, "status": "applied"}, headers=headers)
        assert r.status_code == 201, r.text
        app_id = r.json()["id"]
        print("✓ application created")

        r = client.patch(f"/applications/{app_id}", json={"status": "interviewing"}, headers=headers)
        assert r.status_code == 200
        assert r.json()["status"] == "interviewing"
        print("✓ application updated")

        print("\nALL CHECKS PASSED ✅")


if __name__ == "__main__":
    main()
