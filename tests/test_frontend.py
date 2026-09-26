def test_homepage_is_served(client):
    response = client.get("/")
    stylesheet = client.get("/static/styles.css")

    assert response.status_code == 200
    assert "ASA STUDIOS" in response.text
    assert stylesheet.status_code == 200