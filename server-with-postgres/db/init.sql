CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT false
);

INSERT INTO tasks (id, title, completed)
SELECT * FROM (VALUES
    (1, 'Learn FastAPI', false),
    (2, 'Build CRUD API', false),
    (3, 'Connect Postgres DB', false)
) AS seed(id, title, completed)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
