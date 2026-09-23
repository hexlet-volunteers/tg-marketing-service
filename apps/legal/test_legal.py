import pytest
from inertia.test import InertiaTestCase

DOCUMENTS_FIXTURE = {
    "privacy": {
        "title": "Политика конфиденциальности",
        "updated_at": "2026-07-01",
    },
    "agreement": {
        "title": "Пользовательское соглашение",
        "updated_at": "2026-07-01",
    },
    "offer": {
        "title": "Публичная оферта",
        "updated_at": "2026-07-01",
    },
}


@pytest.mark.django_db
def test_documents_view(client):
    # GET-запрос
    response = client.get(
        "/legal/",
        HTTP_ACCEPT="application/json",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["component"] == "Legal"
    assert data["props"]["documents"] == DOCUMENTS_FIXTURE


class LegalViewTestCase(InertiaTestCase):
    def test_show_assertions(self):
        self.client.get(
            "/legal/",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertComponentUsed("Legal")
