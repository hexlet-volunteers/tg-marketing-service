def test_ai_cabinet_view(client):
    response = client.get("/ai-cabinet/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == "AICabinet"
    # Мок-данные отдаются бэкендом из реестра apps/ai/mock_data.py.
    props = payload["props"]
    assert {"ideas", "insights", "competitors", "heatMapData"}.issubset(props)
    assert len(props["ideas"]) == 3
    assert props["ideas"][0]["title"] == "Обзор новых функций Telegram"
    assert len(props["insights"]) == 4
    assert props["insights"][0]["type"] == "recommendation"
    assert len(props["competitors"]) == 3
    assert "Ср" in props["heatMapData"]
    assert props["heatMapData"]["Ср"]["19"] == 10
