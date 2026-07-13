# mini-backend

The smallest possible backend: a Node.js server (no dependencies) with two JSON endpoints.

## Endpoints

- `GET /api/hello` → `{"message":"Hello, world!"}`
- `GET /api/time` → `{"time":"<current ISO timestamp>"}`
- Any other path → `404` with `{"error":"Not found"}`

## Run it

```bash
node server.js
```

Server starts at `http://localhost:3000`.

## Test it

**Browser:** open `http://localhost:3000/api/hello` and `http://localhost:3000/api/time` — you'll see raw JSON.

**curl:**
```bash
curl http://localhost:3000/api/hello
curl http://localhost:3000/api/time
```