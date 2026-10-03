import pytest
from inertia.test import InertiaTestCase

from apps.legal.documents import LEGAL_DOCUMENTS


@pytest.mark.django_db
def test_documents_view(client):
    response = client.get(
        "/legal/",
        HTTP_ACCEPT="application/json",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["component"] == "Legal"
    assert data["props"]["documents"] == LEGAL_DOCUMENTS


class LegalViewTestCase(InertiaTestCase):
    def test_show_assertions(self):
        self.client.get(
            "/legal/",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertComponentUsed("Legal")
