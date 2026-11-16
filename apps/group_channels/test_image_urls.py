from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from apps.group_channels.forms import CreateGroupForm, UpdateGroupForm
from apps.group_channels.models import Group
from apps.users.models import User
from apps.users.test_url_validator import INVALID_IMAGE_URLS, VALID_IMAGE_URLS


class GroupImageURLTest(TestCase):
    user: User
    group: Group

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="group-url-owner",
            email="group-url@example.com",
            role="user",
        )
        cls.group = Group.objects.create(
            owner=cls.user,
            name="Original collection",
            image_url="https://example.com/original.jpg",
        )

    def setUp(self) -> None:
        self.client = Client(HTTP_X_INERTIA="true")
        self.client.force_login(self.user)

    def test_group_forms_reject_invalid_urls(self) -> None:
        for form_class in (CreateGroupForm, UpdateGroupForm):
            for url in INVALID_IMAGE_URLS:
                with self.subTest(form=form_class.__name__, url=url):
                    form = form_class(
                        data={"name": "New collection", "image_url": url}
                    )
                    self.assertFalse(form.is_valid())
                    self.assertIn("image_url", form.errors)

    def test_group_forms_accept_http_urls_and_empty_values(self) -> None:
        for form_class in (CreateGroupForm, UpdateGroupForm):
            for url in (*VALID_IMAGE_URLS, ""):
                with self.subTest(form=form_class.__name__, url=url):
                    form = form_class(
                        data={"name": "New collection", "image_url": url}
                    )
                    self.assertTrue(form.is_valid(), form.errors)

    def test_model_validation_rejects_invalid_image_urls(self) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                self.group.image_url = url
                with self.assertRaises(ValidationError) as raised:
                    self.group.full_clean()
                self.assertIn("image_url", raised.exception.message_dict)

    def test_model_validation_accepts_http_urls_and_empty_values(self) -> None:
        for url in (*VALID_IMAGE_URLS, ""):
            with self.subTest(url=url):
                self.group.image_url = url
                self.group.full_clean()

    def test_create_endpoint_returns_errors_without_creating_group(
        self,
    ) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                response = self.client.post(
                    reverse("group_channels:group_create"),
                    {"name": "New collection", "image_url": url},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("image_url", response.json()["props"]["errors"])
                self.assertFalse(
                    Group.objects.filter(name="New collection").exists()
                )

    def test_update_endpoint_returns_errors_without_saving_invalid_url(
        self,
    ) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                response = self.client.post(
                    reverse(
                        "group_channels:group_update",
                        kwargs={"slug": self.group.slug},
                    ),
                    {"name": "Changed collection", "image_url": url},
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("image_url", response.json()["props"]["errors"])
                self.group.refresh_from_db()
                self.assertEqual(self.group.name, "Original collection")
                self.assertEqual(
                    self.group.image_url, "https://example.com/original.jpg"
                )

    def test_create_and_update_endpoints_save_http_urls(self) -> None:
        for index, url in enumerate(VALID_IMAGE_URLS):
            with self.subTest(url=url):
                response = self.client.post(
                    reverse("group_channels:group_create"),
                    {"name": f"New collection {index}", "image_url": url},
                )
                self.assertEqual(response.status_code, 200)
                created = Group.objects.get(name=f"New collection {index}")
                self.assertEqual(created.image_url, url)
                response = self.client.post(
                    reverse(
                        "group_channels:group_update",
                        kwargs={"slug": self.group.slug},
                    ),
                    {"name": self.group.name, "image_url": url},
                )
                self.assertEqual(response.status_code, 200)
                self.group.refresh_from_db()
                self.assertEqual(self.group.image_url, url)
