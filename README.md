# ASA Studios URL Shortener

A small URL-shortening service with a vanilla HTML/CSS/JavaScript interface, a FastAPI API, and SQLite or PostgreSQL storage. New links expire after 30 days.

## Run locally

Requirements: Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

Open <http://127.0.0.1:8010>. Local development uses `sqlite:///./url_shortener.db` by default. Set `DATABASE_URL` to use another database, and set `PUBLIC_BASE_URL` when the generated short links should use a different public address. For example, in PowerShell:

```powershell
$env:PUBLIC_BASE_URL = "http://127.0.0.1:8010"
```

FastAPI's interactive API documentation is available at <http://127.0.0.1:8010/docs>.

## Run with Docker Compose

Requirements: Docker Engine with the Compose plugin.

```sh
docker compose up --build
```

Open <http://127.0.0.1:8000>. Compose starts PostgreSQL, waits for its health check, and then starts the API. PostgreSQL data is kept in a named volume. Compose uses `http://127.0.0.1:8000` for generated links by default. To use another public address, set `PUBLIC_BASE_URL` before starting Compose:

```powershell
$env:PUBLIC_BASE_URL = "https://short.example.com"
docker compose up --build
```

## API

| Method | Path | Behavior |
| --- | --- | --- |
| `POST` | `/shorten` | Creates or reuses a short link. Send `{"long_url":"https://example.com"}`. New links return `201`; duplicates return `200`. |
| `GET` | `/{short_code}` | Records a click and redirects to the destination. |
| `GET` | `/{short_code}/stats` | Returns total clicks and daily click counts. |
| `GET` | `/health` | Returns the service health status. |

Short links expire after 30 days. Invalid input returns `422`; unknown links return `404`; expired links return `410`. Rate limits are 5 link-creation requests, 100 redirects, and 15 stats requests per minute per client address; limited requests return `429`.

## Tests

```sh
python -m pytest -q
```

The test client uses an isolated in-memory SQLite database. The application uses PostgreSQL in Docker Compose and in the GitHub Actions test workflow.
