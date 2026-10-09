from __future__ import annotations

from typing import Any

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.db import transaction
from django.http import HttpRequest

from apps.users.consents import (
    peek_yandex_oauth_consent,
    pop_yandex_oauth_consent,
    record_consent,
)


class MarketingSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: Any,
    ) -> bool:
        is_yandex_signup = self._is_yandex_signup(sociallogin)
        if is_yandex_signup and not peek_yandex_oauth_consent(request):
            return False
        return super().is_open_for_signup(request, sociallogin)

    def save_user(
        self,
        request: HttpRequest,
        sociallogin: Any,
        form: Any = None,
    ):
        with transaction.atomic():
            user = super().save_user(request, sociallogin, form=form)
            if self._is_yandex_signup(sociallogin):
                pending_consent = pop_yandex_oauth_consent(request)
                if pending_consent is not None:
                    record_consent(
                        user=user,
                        document_type=pending_consent["document_type"],
                        version=pending_consent["version"],
                        source=pending_consent["source"],
                        request=request,
                    )
        return user

    def pre_social_login(self, request: HttpRequest, sociallogin: Any) -> None:
        if self._is_yandex_signup(sociallogin) and sociallogin.is_existing:
            pop_yandex_oauth_consent(request)
        return super().pre_social_login(request, sociallogin)

    def _is_yandex_signup(self, sociallogin: Any) -> bool:
        account = getattr(sociallogin, "account", None)
        return getattr(account, "provider", None) == "yandex"
