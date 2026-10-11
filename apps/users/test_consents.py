from types import SimpleNamespace
from unittest.mock import patch

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.http import HttpRequest
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from apps.users.adapters import MarketingSocialAccountAdapter
from apps.users.consents import (
    SOCIAL_CONSENT_SESSION_KEY,
    get_client_ip,
    get_current_document_version,
    stash_yandex_oauth_consent,
)
from apps.users.models import Consent, User


class ConsentHistoryTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
            role="user",
        )
        self.url = reverse("users:consent_history")

    def test_authenticated_user_receives_own_consent_history(self) -> None:
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
            role="user",
        )
        consent = Consent.objects.create(
            user=self.user,
            document_type=Consent.DocumentType.PERSONAL_DATA,
            version="2026-07-01",
            ip="203.0.113.10",
            user_agent="ConsentHistoryTest/1.0",
            source=Consent.Source.EMAIL_REGISTRATION,
        )
        Consent.objects.create(
            user=other_user,
            document_type=Consent.DocumentType.PERSONAL_DATA,
            version="2026-07-01",
            source=Consent.Source.EMAIL_REGISTRATION,
        )
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["consents"]), 1)
        self.assertEqual(payload["consents"][0]["id"], consent.pk)
        self.assertEqual(payload["consents"][0]["ip"], "203.0.113.10")

    def test_consent_record_is_immutable(self) -> None:
        consent = Consent.objects.create(
            user=self.user,
            document_type=Consent.DocumentType.PERSONAL_DATA,
            version="2026-07-01",
            source=Consent.Source.EMAIL_REGISTRATION,
        )

        consent.version = "2026-08-01"

        with self.assertRaises(ValueError):
            consent.save()

        with self.assertRaises(ValueError):
            Consent.objects.filter(pk=consent.pk).update(version="2026-08-01")


class ConsentClientIPTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_x_forwarded_for_is_ignored_without_trusted_proxy(self) -> None:
        request = self.factory.post(
            "/auth/create/",
            REMOTE_ADDR="198.51.100.10",
            HTTP_X_FORWARDED_FOR="203.0.113.55",
        )

        self.assertEqual(get_client_ip(request), "198.51.100.10")

    @override_settings(TRUSTED_PROXY_IPS=["198.51.100.10"])
    def test_x_forwarded_for_is_used_from_trusted_proxy(self) -> None:
        request = self.factory.post(
            "/auth/create/",
            REMOTE_ADDR="198.51.100.10",
            HTTP_X_FORWARDED_FOR="203.0.113.55, 198.51.100.10",
        )

        self.assertEqual(get_client_ip(request), "203.0.113.55")


class YandexOAuthConsentTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.adapter = MarketingSocialAccountAdapter()
        self.sociallogin = SimpleNamespace(
            account=SimpleNamespace(provider="yandex"),
            is_existing=False,
        )

    def _request(self) -> HttpRequest:
        request = self.factory.get(
            "/accounts/yandex/login/callback/",
            REMOTE_ADDR="203.0.113.20",
            HTTP_USER_AGENT="YandexOAuthTest/1.0",
        )
        request.session = SessionStore()
        return request

    def test_yandex_signup_is_closed_without_consent(self) -> None:
        request = self._request()

        self.assertFalse(
            self.adapter.is_open_for_signup(request, self.sociallogin)
        )

    def test_yandex_signup_records_stashed_consent_after_save(
        self,
    ) -> None:
        request = self._request()
        stash_yandex_oauth_consent(request)
        user = User.objects.create_user(
            username="yandex-user",
            email="yandex@example.com",
            password="StrongPass123!",
            role="user",
        )

        with patch.object(
            DefaultSocialAccountAdapter,
            "save_user",
            return_value=user,
        ):
            saved_user = self.adapter.save_user(
                request,
                self.sociallogin,
                form=None,
            )

        self.assertEqual(saved_user, user)
        consent = Consent.objects.get(user=user)
        self.assertEqual(
            consent.document_type,
            Consent.DocumentType.PERSONAL_DATA,
        )
        self.assertEqual(
            consent.version,
            get_current_document_version(Consent.DocumentType.PERSONAL_DATA),
        )
        self.assertEqual(consent.source, Consent.Source.YANDEX_OAUTH)
        self.assertEqual(consent.ip, "203.0.113.20")
        self.assertEqual(consent.user_agent, "YandexOAuthTest/1.0")
        self.assertNotIn(SOCIAL_CONSENT_SESSION_KEY, request.session)
