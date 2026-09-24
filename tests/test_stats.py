def test_short_url_stats(client):
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

    stats_response = client.get(f"/{short_code}/stats")

    assert stats_response.status_code == 200

    stats = stats_response.json()
    assert stats["total_clicks"] == 1
    assert len(stats["clicks_per_day"]) == 1
    assert stats["clicks_per_day"][0]["count"] == 1