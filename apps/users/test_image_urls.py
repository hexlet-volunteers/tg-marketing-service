from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from apps.users.forms import AvatarChange, UserRegForm, UserUpdateForm
from apps.users.models import User
from apps.users.test_url_validator import INVALID_IMAGE_URLS, VALID_IMAGE_URLS


class AvatarURLTest(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="url-owner",
            email="url-owner@example.com",
            first_name="URL",
            last_name="Owner",
            role="user",
            avatar_image="https://example.com/original.jpg",
        )

    def setUp(self) -> None:
        self.client = Client(HTTP_X_INERTIA="true")
        self.client.force_login(self.user)

    def test_all_avatar_forms_reject_invalid_urls(self) -> None:
        for form_class in (UserRegForm, UserUpdateForm, AvatarChange):
            for url in INVALID_IMAGE_URLS:
                with self.subTest(form=form_class.__name__, url=url):
                    field = form_class().fields["avatar_image"]
                    with self.assertRaises(ValidationError):
                        field.clean(url)

    def test_all_avatar_forms_accept_http_urls_and_empty_values(self) -> None:
        for form_class in (UserRegForm, UserUpdateForm, AvatarChange):
            for url in (*VALID_IMAGE_URLS, ""):
                with self.subTest(form=form_class.__name__, url=url):
                    field = form_class().fields["avatar_image"]
                    self.assertEqual(field.clean(url), url)

    def test_model_validation_rejects_invalid_avatar_urls(self) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                self.user.avatar_image = url
                with self.assertRaises(ValidationError) as raised:
                    self.user.full_clean()
                self.assertIn("avatar_image", raised.exception.message_dict)

    def test_model_validation_accepts_http_urls_empty_and_null(self) -> None:
        for url in (*VALID_IMAGE_URLS, "", None):
            with self.subTest(url=url):
                self.user.avatar_image = url
                self.user.full_clean()

    def test_profile_endpoints_return_errors_without_saving_invalid_url(
        self,
    ) -> None:
        for endpoint in (
            reverse("users:user_cabinet"),
            reverse(
                "users:user_update", kwargs={"username": self.user.username}
            ),
        ):
            for url in INVALID_IMAGE_URLS:
                with self.subTest(endpoint=endpoint, url=url):
                    response = self.client.post(
                        endpoint,
                        {
                            "first_name": "Changed",
                            "last_name": "Owner",
                            "email": self.user.email,
                            "avatar_image": url,
                        },
                    )
                    self.assertEqual(response.status_code, 200)
                    errors = response.json()["props"]["errors"]
                    self.assertIn("avatar_image", errors)
                    self.user.refresh_from_db()
                    self.assertEqual(
                        self.user.avatar_image,
                        "https://example.com/original.jpg",
                    )
                    self.assertEqual(self.user.first_name, "URL")

    def test_avatar_endpoint_rejects_invalid_urls_with_error_flash(
        self,
    ) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                response = self.client.post(
                    reverse(
                        "users:avatar_update",
                        kwargs={"username": self.user.username},
                    ),
                    {"avatar_image": url},
                    follow=True,
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn("error", response.json()["props"]["flash"])
                self.user.refresh_from_db()
                self.assertEqual(
                    self.user.avatar_image, "https://example.com/original.jpg"
                )

    def test_registration_rejects_invalid_avatar_without_creating_user(
        self,
    ) -> None:
        for url in INVALID_IMAGE_URLS:
            with self.subTest(url=url):
                response = self.client.post(
                    reverse("users:user_create"),
                    {
                        "email": "new-url-user@example.com",
                        "password1": "URL-Strong-Password-123!",
                        "password2": "URL-Strong-Password-123!",
                        "terms": "on",
                        "avatar_image": url,
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    "avatar_image", response.json()["props"]["form"]["errors"]
                )
                self.assertFalse(
                    User.objects.filter(
                        email="new-url-user@example.com"
                    ).exists()
                )

    def test_profile_saves_http_and_https_urls(self) -> None:
        for url in VALID_IMAGE_URLS:
            with self.subTest(url=url):
                response = self.client.post(
                    reverse("users:user_cabinet"),
                    {
                        "first_name": "URL",
                        "last_name": "Owner",
                        "email": self.user.email,
                        "avatar_image": url,
                    },
                )
                self.assertEqual(response.status_code, 302)
                self.user.refresh_from_db()
                self.assertEqual(self.user.avatar_image, url)
