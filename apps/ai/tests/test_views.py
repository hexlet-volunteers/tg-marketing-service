def test_ai_cabinet_view(client):
    response = client.get("/ai-cabinet/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == "AICabinet"
    # Плейсхолдер-DTO создается пустым: page-props минимальны.
    assert {"ideas", "insights", "competitors", "heatMapData"}.isdisjoint(
        payload["props"]
    )
