# mini-backend

The smallest possible backend: a dependency-free Node.js server with two JSON endpoints.

## Features

- 🪶 Zero dependencies — just Node's built-in `http` module
- ⚡ Two endpoints, instant startup
- 🧪 Easy to test from a browser or the command line

## Endpoints

| Method | Path          | Response                                |
|--------|---------------|-------------------------------------------|
| `GET`  | `/api/hello`  | `{"message":"Hello, world!"}`             |
| `GET`  | `/api/time`   | `{"time":"<current ISO timestamp>"}`      |
| `GET`  | *anything else* | `404` — `{"error":"Not found"}`         |

## Getting started

### Prerequisites

- [Node.js](https://nodejs.org/) (any recent version — no packages to install)

### Run it

```bash
node server.js
```

The server starts at **http://localhost:3000**.

## Testing the endpoints

**In a browser**, just open:
- http://localhost:3000/api/hello
- http://localhost:3000/api/time

**With curl:**

```bash
curl http://localhost:3000/api/hello
# {"message":"Hello, world!"}

curl http://localhost:3000/api/time
# {"time":"2026-07-15T12:34:56.789Z"}
```

## Project structure

```
mini-backend/
├── server.js   # the server
└── README.md
```
