import pytest


@pytest.mark.parametrize("pk", [1, 999])
def test_collection_detail_renders_mock_page(client, pk):
    response = client.get(f"/collections/{pk}/", HTTP_X_INERTIA="true")

    assert response.status_code == 200
    assert response.json()["component"] == "Collection"
