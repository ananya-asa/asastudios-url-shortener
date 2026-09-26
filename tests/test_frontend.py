def test_homepage_is_served(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "ASA STUDIOS" in response.text