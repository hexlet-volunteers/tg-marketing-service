import pytest


@pytest.mark.parametrize("pk", [1, 999])
def test_collection_detail_renders_mock_page(client, pk):
    response = client.get(f"/collections/{pk}/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    payload = response.json()
    assert payload["component"] == "Collection"
    # Мок-данные отдаются бэкендом из реестра
    # apps/group_channels/mock_data.py.
    props = payload["props"]
    assert props["title"] == "Топ IT-каналов"
    assert props["channel_count"] == 3
    assert len(props["channels"]) == 3
    assert props["channels"][0]["name"] == "Product Radar"
    assert props["channels"][0]["color"]
