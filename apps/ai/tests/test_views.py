def test_ai_cabinet_view(client):
    response = client.get("/ai-cabinet/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    assert response.json()["component"] == "AICabinet"
