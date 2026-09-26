def test_homepage_is_served(client):
    response = client.get("/")
    stylesheet = client.get("/static/styles.css")
    script = client.get("/static/app.js")

    assert response.status_code == 200
    assert "ASA STUDIOS" in response.text
    assert 'id="long-url"' in response.text
    assert 'id="generate-button"' in response.text
    assert 'id="short-result"' in response.text
    assert stylesheet.status_code == 200
    assert script.status_code == 200