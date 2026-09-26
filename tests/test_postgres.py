import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

from app.main import app


DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    DATABASE_URL is None or not DATABASE_URL.startswith("postgresql"),
    reason="Set DATABASE_URL to run PostgreSQL integration tests",
)


def test_postgres_can_create_and_redirect_url():
    assert DATABASE_URL is not None
    assert make_url(DATABASE_URL).database == "url_shortener_test", (
        "PostgreSQL integration tests may only use the url_shortener_test database"
    )

    long_url = f"https://example.com/{uuid4().hex}"

    with TestClient(app) as client:
        create_response = client.post("/shorten", json={"long_url": long_url})
        assert create_response.status_code == 201

        short_code = create_response.json()["short_url"].rstrip("/").split("/")[-1]
        redirect_response = client.get(f"/{short_code}", follow_redirects=False)

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == long_url