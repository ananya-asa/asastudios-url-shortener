from datetime import datetime, timedelta

import pytest
from sqlmodel import Session, select

from app.main import app
from app.models.url import URL


def test_shorten_new_url(client):
    response = client.post("/shorten", json={"long_url": "https://example.com"})

    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert "expires_at" in data


def test_shorten_duplicate_url(client):
    url = {"long_url": "https://example.com"}

    first_response = client.post("/shorten", json=url)
    second_response = client.post("/shorten", json=url)

    assert first_response.status_code == 201
    assert second_response.status_code == 200

    first_data = first_response.json()
    second_data = second_response.json()

    assert second_data["short_url"] == first_data["short_url"]
    assert "expires_at" in second_data


def test_shorten_rejects_invalid_url(client):
    response = client.post("/shorten", json={"long_url": "not-a-url"})
    assert response.status_code == 422


def test_shorten_rate_limit_returns_429(client):
    for request_number in range(5):
        response = client.post(
            "/shorten",
            json={"long_url": f"https://example.com/{request_number}"},
        )
        assert response.status_code == 201

    limited_response = client.post(
        "/shorten",
        json={"long_url": "https://example.com/limited"},
    )
    assert limited_response.status_code == 429



def test_redirect_records_click_and_returns_302(client):
    create_response = client.post(
        "/shorten",
        json={"long_url": "https://example.com"},
    )
    assert create_response.status_code == 201

    short_url = create_response.json()["short_url"]
    short_code = short_url.rstrip("/").split("/")[-1]

    redirect_response = client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"].rstrip("/") == "https://example.com"    


def test_redirect_unknown_short_code_returns_404(client):
    response = client.get("/does-not-exist", follow_redirects=False)
    assert response.status_code == 404


def test_redirect_expired_short_code_returns_410(client):
    create_response = client.post(
        "/shorten",
        json={"long_url": "https://example.com"},
    )
    assert create_response.status_code == 201

    short_code = create_response.json()["short_url"].rstrip("/").split("/")[-1]

    with Session(app.state.test_engine) as session:
        row = session.exec(
            select(URL).where(URL.short_code == short_code)
        ).first()
        assert row is not None
        row.expires_at = datetime.utcnow() - timedelta(days=1)
        session.add(row)
        session.commit()

    response = client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 410
