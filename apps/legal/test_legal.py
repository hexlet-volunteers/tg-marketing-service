import pytest
from django.test import Client, TestCase

from apps.legal.documents import LEGAL_DOCUMENTS


@pytest.mark.django_db
def test_documents_view(client: Client) -> None:
    response = client.get(
        "/legal/",
        HTTP_ACCEPT="application/json",
        HTTP_X_INERTIA="true",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["component"] == "Legal"
    assert data["props"]["documents"] == LEGAL_DOCUMENTS


class LegalViewTestCase(TestCase):
    def test_show_assertions(self) -> None:
        response = self.client.get(
            "/legal/",
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["component"], "Legal")
