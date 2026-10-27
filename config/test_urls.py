def test_unknown_url_renders_not_found_page(client):
    response = client.get("/no-such-page/", HTTP_X_INERTIA="true")

    assert response.status_code == 404
    assert response.json()["component"] == "NotFound"


def test_unknown_url_without_slash_redirects(client):
    response = client.get("/no-such-page")

    assert response.status_code == 301
    assert response["Location"] == "/no-such-page/"
