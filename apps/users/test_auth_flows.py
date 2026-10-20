import json
import re
from datetime import datetime, timedelta
from typing import Any, cast
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import SESSION_KEY, get_user
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.http import HttpResponse, HttpResponseBase
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.users.consents import get_current_document_version
from apps.users.models import Consent, PartnerProfile, User

PASSWORD = "AuthFlow-Strong-Password-42!"  # noqa: S105
NEW_PASSWORD = "AuthFlow-New-Password-73!"  # noqa: S105


class InertiaAuthTestCase(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="auth-user",
            email="auth@example.com",
            password=PASSWORD,
            first_name="Ada",
            last_name="Lovelace",
            avatar_image="https://example.com/avatar.png",
            role="user",
        )

    def setUp(self) -> None:
        self.client = Client(HTTP_X_INERTIA="true")

    def assert_page(
        self, response: HttpResponseBase, component: str
    ) -> dict[str, Any]:
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Inertia"], "true")
        payload = json.loads(cast(HttpResponse, response).content)
        self.assertEqual(payload["component"], component)
        return payload["props"]


class EmailLoginFlowTest(InertiaAuthTestCase):
    def test_get_login_returns_empty_form_and_anonymous_auth(self) -> None:
        props = self.assert_page(
            self.client.get(reverse("users:login")), "Auth"
        )
        self.assertEqual(
            props["form"],
            {"data": {"email": "", "password": ""}, "errors": {}},
        )
        self.assertIsNone(props["auth"])
        self.assertEqual(props["role"], "guest")
        self.assertFalse(props["is_admin"])
        self.assertTrue(props["csrfToken"])

    def test_email_login_authenticates_and_opens_dashboard(self) -> None:
        response = self.client.post(
            reverse("users:login"),
            {"email": " AUTH@EXAMPLE.COM ", "password": PASSWORD},
        )
        self.assertRedirects(
            response,
            reverse("homepage:dashboard"),
            fetch_redirect_response=False,
        )
        self.assertEqual(get_user(self.client).pk, self.user.pk)
        props = self.assert_page(
            self.client.get(response["Location"]), "Dashboard"
        )
        self.assertEqual(props["auth"]["id"], self.user.pk)
        self.assertEqual(props["role"], "user")
        self.assertIn("success", props["flash"])

    def test_login_rejects_invalid_credentials_and_preserves_only_email(
        self,
    ) -> None:
        for email, password in (
            (self.user.email, "incorrect"),
            ("missing@example.com", PASSWORD),
            (self.user.username, PASSWORD),
            ("", ""),
        ):
            with self.subTest(email=email, password=password):
                props = self.assert_page(
                    self.client.post(
                        reverse("users:login"),
                        {"email": email, "password": password},
                    ),
                    "Auth",
                )
                self.assertTrue(props["form"]["errors"])
                self.assertEqual(props["form"]["data"]["email"], email)
                self.assertEqual(props["form"]["data"]["password"], "")
                self.assertIsNone(props["auth"])
                self.assertFalse(get_user(self.client).is_authenticated)

    def test_inactive_user_cannot_log_in(self) -> None:
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        props = self.assert_page(
            self.client.post(
                reverse("users:login"),
                {"email": self.user.email, "password": PASSWORD},
            ),
            "Auth",
        )
        self.assertTrue(props["form"]["errors"])
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_login_rotates_session_key(self) -> None:
        session = self.client.session
        session["pre_login"] = True
        session.save()
        old_key = session.session_key
        self.client.post(
            reverse("users:login"),
            {"email": self.user.email, "password": PASSWORD},
        )
        self.assertEqual(get_user(self.client).pk, self.user.pk)
        self.assertNotEqual(self.client.session.session_key, old_key)


class RegistrationFlowTest(InertiaAuthTestCase):
    def registration_data(self, **overrides: str) -> dict[str, str]:
        data = {
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": "grace@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
            "terms": "on",
        }
        data.update(overrides)
        return data

    def test_get_registration_returns_component_and_empty_form(self) -> None:
        props = self.assert_page(
            self.client.get(reverse("users:user_create")),
            "FormRegistration",
        )
        self.assertEqual(props["form"]["errors"], {})
        for field in ("email", "password1", "password2", "terms"):
            self.assertEqual(props["form"]["data"][field], "")
        self.assertIsNone(props["auth"])

    def test_registration_logs_in_new_user_and_renders_dashboard(self) -> None:
        response = self.client.post(
            reverse("users:user_create"), self.registration_data()
        )
        self.assertRedirects(
            response,
            reverse("homepage:dashboard"),
            fetch_redirect_response=False,
        )
        user = User.objects.get(email="grace@example.com")
        self.assertTrue(user.check_password(PASSWORD))
        self.assertEqual(get_user(self.client).pk, user.pk)
        self.assertEqual(user.role, "user")
        props = self.assert_page(
            self.client.get(response["Location"]), "Dashboard"
        )
        self.assertEqual(props["auth"]["id"], user.pk)
        self.assertEqual(props["auth"]["role"], "user")
        self.assertIn("success", props["flash"])
        self.assertIsNone(
            self.assert_page(self.client.get(reverse("users:login")), "Auth")[
                "flash"
            ]
        )
        consent = Consent.objects.get(user=user)
        self.assertEqual(consent.source, Consent.Source.EMAIL_REGISTRATION)
        self.assertEqual(
            consent.version,
            get_current_document_version(Consent.DocumentType.PERSONAL_DATA),
        )

    def test_invalid_registration_does_not_create_or_authenticate_user(
        self,
    ) -> None:
        cases = (
            ({"email": "AUTH@EXAMPLE.COM"}, "email"),
            ({"email": "not-an-email"}, "email"),
            ({"password2": "different"}, "password2"),
            ({"password1": "short", "password2": "short"}, "password2"),
            ({"terms": ""}, "terms"),
        )
        count = User.objects.count()
        for overrides, error_field in cases:
            with self.subTest(overrides=overrides):
                data = self.registration_data(**overrides)
                props = self.assert_page(
                    self.client.post(reverse("users:user_create"), data),
                    "FormRegistration",
                )
                self.assertIn(error_field, props["form"]["errors"])
                self.assertEqual(props["form"]["data"]["email"], data["email"])
                self.assertEqual(props["form"]["data"]["password1"], "")
                self.assertEqual(props["form"]["data"]["password2"], "")
                self.assertEqual(User.objects.count(), count)
                self.assertFalse(Consent.objects.exists())
                self.assertFalse(get_user(self.client).is_authenticated)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    PASSWORD_RESET_TIMEOUT=3600,
)
class PasswordResetFlowTest(InertiaAuthTestCase):
    def reset_url(
        self, token: str | None = None, uid: str | None = None
    ) -> str:
        return reverse(
            "users:restore_password",
            kwargs={
                "uidb64": uid
                or urlsafe_base64_encode(force_bytes(self.user.pk)),
                "token": token or default_token_generator.make_token(self.user),
            },
        )

    def test_get_reset_request_returns_empty_email(self) -> None:
        props = self.assert_page(
            self.client.get(reverse("users:restore_password_request")),
            "RestorePasswordRequest",
        )
        self.assertEqual(props["email"], "")
        self.assertIsNone(props["auth"])

    def test_reset_request_sends_usable_link_and_success_flash(self) -> None:
        response = self.client.post(
            reverse("users:restore_password_request"),
            {"email": self.user.email},
        )
        self.assertRedirects(
            response, reverse("users:login"), fetch_redirect_response=False
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        links = re.findall(r"https?://[^\s<>\"]+", str(mail.outbox[0].body))
        reset_links = sorted(
            {
                urlparse(link).path
                for link in links
                if "restore-password/" in link
            }
        )
        self.assertEqual(len(reset_links), 1)
        self.assertIn(
            "success",
            self.assert_page(self.client.get(response["Location"]), "Auth")[
                "flash"
            ],
        )
        props = self.assert_page(
            self.client.get(reset_links[0]), "RestorePassword"
        )
        self.assertEqual(props["new_password1"], "")
        self.assertEqual(props["new_password2"], "")

    def test_unknown_inactive_and_social_only_accounts_do_not_receive_email(
        self,
    ) -> None:
        inactive = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password=PASSWORD,
            is_active=False,
        )
        social = User.objects.create_user(
            username="social-only",
            email="social-only@example.com",
        )
        for email in ("unknown@example.com", inactive.email, social.email):
            with self.subTest(email=email):
                response = self.client.post(
                    reverse("users:restore_password_request"), {"email": email}
                )
                self.assertRedirects(
                    response,
                    reverse("users:login"),
                    fetch_redirect_response=False,
                )
                self.assertEqual(len(mail.outbox), 0)
                self.assertIn("success", self.client.session["flash"])

    def test_invalid_email_returns_reset_request_errors(self) -> None:
        props = self.assert_page(
            self.client.post(
                reverse("users:restore_password_request"),
                {"email": "invalid"},
            ),
            "RestorePasswordRequest",
        )
        self.assertEqual(props["email"], "invalid")
        self.assertIn("email", props["errors"])
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_token_changes_password_and_invalidates_all_old_sessions(
        self,
    ) -> None:
        browsers = [Client(HTTP_X_INERTIA="true") for _ in range(2)]
        for browser in browsers:
            browser.force_login(self.user)
        url = self.reset_url()
        response = self.client.post(
            url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD}
        )
        self.assertRedirects(
            response, reverse("users:login"), fetch_redirect_response=False
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))
        self.assertFalse(self.user.check_password(PASSWORD))
        for browser in browsers:
            props = self.assert_page(
                browser.get(reverse("users:login")), "Auth"
            )
            self.assertIsNone(props["auth"])
            self.assertNotIn(SESSION_KEY, browser.session)
            self.assertRedirects(
                browser.get(reverse("users:user_cabinet")),
                reverse("users:login"),
                fetch_redirect_response=False,
            )
        self.assertFalse(get_user(self.client).is_authenticated)
        self.client.post(
            reverse("users:login"),
            {"email": self.user.email, "password": NEW_PASSWORD},
        )
        self.assertEqual(get_user(self.client).pk, self.user.pk)

    def test_used_token_is_rejected_for_get_and_post(self) -> None:
        url = self.reset_url()
        self.client.post(
            url, {"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD}
        )
        for method in (self.client.get, self.client.post):
            response = method(
                url, {"new_password1": PASSWORD, "new_password2": PASSWORD}
            )
            self.assertRedirects(
                response, reverse("users:login"), fetch_redirect_response=False
            )
            self.assertIn("error", self.client.session["flash"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))

    def test_token_timeout_boundary_and_expired_token_rejection(self) -> None:
        issued_at = datetime(2026, 1, 15, 12)
        with patch.object(
            default_token_generator, "_now", return_value=issued_at
        ):
            url = self.reset_url()
        with patch.object(
            default_token_generator,
            "_now",
            return_value=issued_at + timedelta(seconds=3600),
        ):
            self.assert_page(self.client.get(url), "RestorePassword")
        with patch.object(
            default_token_generator,
            "_now",
            return_value=issued_at + timedelta(seconds=3601),
        ):
            for method in (self.client.get, self.client.post):
                response = method(
                    url,
                    {
                        "new_password1": NEW_PASSWORD,
                        "new_password2": NEW_PASSWORD,
                    },
                )
                self.assertRedirects(
                    response,
                    reverse("users:login"),
                    fetch_redirect_response=False,
                )
                self.assertIn("error", self.client.session["flash"])
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))

    def test_invalid_tokens_and_malformed_user_ids_are_rejected(self) -> None:
        urls = [
            self.reset_url(token="invalid-token"),
            self.reset_url(uid=urlsafe_base64_encode(b"not-a-number")),
            self.reset_url(uid=urlsafe_base64_encode(b"\xff")),
            self.reset_url(uid=urlsafe_base64_encode(b"999999999")),
        ]
        for url in urls:
            for method in (self.client.get, self.client.post):
                with self.subTest(url=url, method=method.__name__):
                    response = method(url)
                    self.assertRedirects(
                        response,
                        reverse("users:login"),
                        fetch_redirect_response=False,
                    )
                    self.assertIn("error", self.client.session["flash"])

    def test_password_validation_does_not_echo_passwords_or_consume_token(
        self,
    ) -> None:
        url = self.reset_url()
        for password1, password2 in (
            (NEW_PASSWORD, "mismatch"),
            ("short", "short"),
        ):
            with self.subTest(password1=password1):
                props = self.assert_page(
                    self.client.post(
                        url,
                        {
                            "new_password1": password1,
                            "new_password2": password2,
                        },
                    ),
                    "RestorePassword",
                )
                self.assertTrue(props["errors"])
                self.assertEqual(props["new_password1"], "")
                self.assertEqual(props["new_password2"], "")
                self.assert_page(self.client.get(url), "RestorePassword")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))


class SharedAuthAndLogoutTest(InertiaAuthTestCase):
    def test_authenticated_shared_auth_contains_only_public_fields(
        self,
    ) -> None:
        self.client.force_login(self.user)
        props = self.assert_page(
            self.client.get(reverse("users:login")), "Auth"
        )
        self.assertEqual(
            props["auth"],
            {
                "id": self.user.pk,
                "name": "Ada Lovelace",
                "email": self.user.email,
                "avatar_url": self.user.avatar_image,
                "role": "user",
            },
        )
        self.assertEqual(props["role"], "user")
        self.assertFalse(props["is_admin"])

    def test_shared_roles_and_admin_flag(self) -> None:
        for role, is_staff, expected_role, is_admin in (
            ("partner", False, "partner", False),
            ("channel_moderator", False, "channel_moderator", False),
            ("admin", False, "admin", True),
            ("user", True, "user", True),
            ("unknown", False, "user", False),
        ):
            with self.subTest(role=role, is_staff=is_staff):
                self.user.role, self.user.is_staff = role, is_staff
                self.user.save(update_fields=["role", "is_staff"])
                self.client.force_login(self.user)
                props = self.assert_page(
                    self.client.get(reverse("users:login")), "Auth"
                )
                self.assertEqual(props["role"], expected_role)
                self.assertEqual(props["auth"]["role"], expected_role)
                self.assertEqual(props["is_admin"], is_admin)

    def test_post_logout_clears_session_and_shared_auth(self) -> None:
        self.client.force_login(self.user)
        session = self.client.session
        session["private_data"] = "private"
        session.save()
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(
            response, reverse("main_index"), fetch_redirect_response=False
        )
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertNotIn("private_data", self.client.session)
        props = self.assert_page(
            self.client.get(reverse("users:login")), "Auth"
        )
        self.assertIsNone(props["auth"])
        self.assertEqual(props["role"], "guest")
        self.assertFalse(props["is_admin"])
        self.assertRedirects(
            self.client.get(reverse("users:user_cabinet")),
            reverse("users:login"),
            fetch_redirect_response=False,
        )

    def test_get_logout_does_not_change_authentication(self) -> None:
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(
            response, reverse("main_index"), fetch_redirect_response=False
        )
        self.assertEqual(get_user(self.client).pk, self.user.pk)

    def test_logout_requires_csrf_and_authenticated_owner(self) -> None:
        browser = Client(enforce_csrf_checks=True)
        browser.force_login(self.user)
        self.assertEqual(browser.post(reverse("users:logout")).status_code, 403)
        self.assertEqual(get_user(browser).pk, self.user.pk)
        self.assertRedirects(
            self.client.post(reverse("users:logout")),
            reverse("users:login"),
            fetch_redirect_response=False,
        )


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "yandex": {"APP": {"client_id": "test-client", "secret": "test-secret"}}
    },
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class YandexOAuthFlowTest(InertiaAuthTestCase):
    def oauth_callback(self, consent: bool = True) -> HttpResponseBase:
        response = self.client.post(
            reverse("yandex_login"), {"terms": "on"} if consent else {}
        )
        self.assertEqual(response.status_code, 302)
        state = parse_qs(urlparse(response["Location"]).query)["state"][0]
        token_response = Mock(
            status_code=200, headers={"content-type": "application/json"}
        )
        token_response.json.return_value = {
            "access_token": "test-access-token",
            "token_type": "bearer",
        }
        profile_response = Mock(status_code=200)
        profile_response.json.return_value = {
            "id": "yandex-test-id",
            "default_email": "yandex@example.com",
            "display_name": "yandex-user",
            "first_name": "Yandex",
            "last_name": "Tester",
        }
        with patch(
            "requests.sessions.Session.request",
            side_effect=[token_response, profile_response],
        ) as provider_request:
            response = self.client.get(
                reverse("yandex_callback"),
                {"state": state, "code": "test-code"},
            )
        self.assertEqual(provider_request.call_count, 2)
        return response

    def test_yandex_signup_creates_user_consent_role_and_session(self) -> None:
        response = self.oauth_callback()
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(email="yandex@example.com")
        self.assertEqual(get_user(self.client).pk, user.pk)
        self.assertEqual(user.role, "user")
        self.assertEqual(user.first_name, "Yandex")
        self.assertFalse(user.has_usable_password())
        self.assertTrue(
            SocialAccount.objects.filter(
                user=user, provider="yandex", uid="yandex-test-id"
            ).exists()
        )
        consent = Consent.objects.get(user=user)
        self.assertEqual(consent.source, Consent.Source.YANDEX_OAUTH)
        self.assertEqual(
            consent.version,
            get_current_document_version(Consent.DocumentType.PERSONAL_DATA),
        )
        props = self.assert_page(
            self.client.get(reverse("users:login")), "Auth"
        )
        self.assertEqual(props["auth"]["id"], user.pk)

    def test_yandex_signup_without_consent_does_not_create_user(self) -> None:
        count = User.objects.count()
        self.oauth_callback(consent=False)
        self.assertEqual(User.objects.count(), count)
        self.assertFalse(SocialAccount.objects.exists())
        self.assertFalse(Consent.objects.exists())
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_existing_yandex_account_logs_in_without_duplicate_user_or_consent(
        self,
    ) -> None:
        self.oauth_callback()
        count, consents = User.objects.count(), Consent.objects.count()
        user_id = get_user(self.client).pk
        self.client.post(reverse("users:logout"))
        response = self.oauth_callback(consent=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user(self.client).pk, user_id)
        self.assertEqual(User.objects.count(), count)
        self.assertEqual(Consent.objects.count(), consents)

    def test_invalid_oauth_state_does_not_contact_provider_or_log_in(
        self,
    ) -> None:
        with patch("requests.sessions.Session.request") as provider_request:
            response = self.client.get(
                reverse("yandex_callback"),
                {"state": "invalid", "code": "test-code"},
            )
        self.assertEqual(response.status_code, 401)
        provider_request.assert_not_called()
        self.assertFalse(get_user(self.client).is_authenticated)
        self.assertFalse(SocialAccount.objects.exists())


class RoleAssignmentSignalTest(InertiaAuthTestCase):
    def test_new_user_gets_default_role_from_signal(self) -> None:
        user = User.objects.create_user(
            username="default-role", email="default-role@example.com"
        )
        user.refresh_from_db()
        self.assertEqual(user.role, "user")

    def test_explicit_admin_role_is_not_overwritten(self) -> None:
        user = User.objects.create_user(
            username="explicit-admin", email="admin@example.com", role="admin"
        )
        user.refresh_from_db()
        self.assertEqual(user.role, "admin")

    def test_partner_activation_assigns_role_visible_in_shared_auth(
        self,
    ) -> None:
        profile = PartnerProfile.objects.create(user=self.user)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "user")
        profile.status = "active"
        profile.save(update_fields=["status"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "partner")
        self.client.force_login(self.user)
        props = self.assert_page(
            self.client.get(reverse("users:login")), "Auth"
        )
        self.assertEqual(props["auth"]["role"], "partner")
        self.assertEqual(props["role"], "partner")
