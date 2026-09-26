from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core import limiter
from app.db.session import create_db_and_tables
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # any shutdown/cleanup code would go here, after yield

app = FastAPI(lifespan=lifespan)
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(frontend_dir / "index.html")

@app.get("/health")
def health_check():
    return {"status": "ok"}


def render_error_page(title: str, message: str, detail: str, status_code: int) -> HTMLResponse:
    return HTMLResponse(
        f"""
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{title}</title>
          <link rel="stylesheet" href="/static/styles.css">
        </head>
        <body>
          <header class="site-header">
            <a class="wordmark" href="/">ASA STUDIOS</a>
          </header>
          <main class="page-main">
            <h1>{title}</h1>
            <p>{message}</p>
            <p id="form-feedback">{detail}</p>
          </main>
          <footer class="site-footer">ASA STUDIOS</footer>
        </body>
        </html>
        """,
        status_code=status_code,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return render_error_page(
            "Link not found",
            "This short link doesn’t exist yet.",
            "Maybe it never did — head back to the studio and generate a new one.",
            status_code=404,
        )
    if exc.status_code == 410:
        return render_error_page(
            "Link expired",
            "This short link had a good run, but it’s expired now.",
            "The destination is no longer available for redirects.",
            status_code=410,
        )
    return HTMLResponse(status_code=exc.status_code, content=exc.detail)


app.include_router(router)
