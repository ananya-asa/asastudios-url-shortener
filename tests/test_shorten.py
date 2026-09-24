def test_shorten_new_url(client):
    response = client.post("/shorten", json={"long_url": "https://example.com"})

    assert response.status_code == 201
    data = response.json()
    assert "short_url" in data
    assert "expires_at" in data

