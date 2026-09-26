from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

app.include_router(router)
