from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    # any shutdown/cleanup code would go here, after yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}