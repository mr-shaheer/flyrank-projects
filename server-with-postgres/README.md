# A2 Task API — Postgres + Docker

## Architecture

```
main.py (routes)
   -> service.py (business logic)
        -> repository.py (interface)
             -> postgres_repository.py (Postgres implementation)
                  -> Postgres (Docker container, data on a named volume)
```

`service.py` and `main.py` depend only on the `TaskRepository` interface
defined in `repository.py`. The concrete implementation
(`postgres_repository.py`) is wired in with a single line in `main.py`:

```python
repo = PostgresTaskRepository(DATABASE_URL)
```

**Confirmed: swapping storage only required creating `postgres_repository.py`
and changing that one line in `main.py`. `service.py` and every route in
`main.py` were not touched.** `memory_repository.py` is kept in the repo as
the original in-memory implementation, for comparison — it implements the
exact same `TaskRepository` interface.

## Running the stack

```bash
docker compose up --build
```

This starts both the FastAPI app (port 8000) and Postgres (port 5432)
together. On first boot, Postgres runs `db/init.sql` automatically, creating
the `tasks` table and seeding 3 rows.

Visit `http://localhost:8000/docs` for interactive API docs.

## Configuration

Connection string is read from `DATABASE_URL` in `.env` (gitignored).
`.env.example` is committed as a template — copy it to `.env` before running
if you don't already have one:

```bash
cp .env.example .env
```

## Persistence proof

Steps taken to verify data survives a restart:

1. Ran `docker compose up --build`.
2. Created a new task:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"id": 4, "title": "Prove persistence", "completed": false}'
   ```
3. Confirmed it via `curl http://localhost:8000/tasks` — 4 tasks returned
   (3 seeded + 1 new).
4. Restarted both the app and the database container:
   ```bash
   docker compose restart
   ```
5. Ran `curl http://localhost:8000/tasks` again — all 4 tasks, including
   `id: 4`, were still present.

This confirms data is written to the `pgdata` named volume, not to the
container's writable layer, so it survives container restarts.

(Note: `docker compose down -v` would delete the volume and wipe data —
only plain `docker compose down` / `restart` were used for this test.)

## Stretch goals

Not implemented in this submission:
- Redis service in compose
- Index + `EXPLAIN ANALYZE` before/after comparison
