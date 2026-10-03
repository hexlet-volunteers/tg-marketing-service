from __future__ import annotations

import ipaddress
from datetime import UTC, datetime, timedelta
from typing import Any

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from apps.legal.documents import get_consent_document_version
from apps.users.models import Consent, User

SOCIAL_CONSENT_SESSION_KEY = "pending_yandex_oauth_consent"
SOCIAL_CONSENT_TTL = timedelta(minutes=15)
TRUTHY_CONSENT_VALUES = {"1", "true", "on", "yes"}


def get_current_document_version(document_type: str) -> str:
    return get_consent_document_version(document_type)


def has_consent_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in TRUTHY_CONSENT_VALUES


def request_has_consent(request: HttpRequest) -> bool:
    return any(
        has_consent_value(value)
        for value in (
            request.POST.get("terms"),
            request.POST.get("consent"),
            request.GET.get("terms"),
            request.GET.get("consent"),
        )
    )


def _safe_ip(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.split(",", 1)[0].strip()
    try:
        ipaddress.ip_address(candidate)
    except ValueError:
        return None
    return candidate


def _is_trusted_proxy(ip: str | None) -> bool:
    if ip is None:
        return False
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False

    for proxy in getattr(settings, "TRUSTED_PROXY_IPS", ()):
        try:
            if address in ipaddress.ip_network(proxy, strict=False):
                return True
        except ValueError:
            continue
    return False


def get_client_ip(request: HttpRequest) -> str | None:
    remote_addr = _safe_ip(request.META.get("REMOTE_ADDR"))
    if _is_trusted_proxy(remote_addr):
        return _safe_ip(request.META.get("HTTP_X_FORWARDED_FOR")) or remote_addr
    return remote_addr


def get_user_agent(request: HttpRequest) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


def record_consent(
    *,
    user: User | None,
    document_type: str,
    source: str,
    request: HttpRequest,
    version: str | None = None,
) -> Consent:
    return Consent.objects.create(
        user=user,
        document_type=document_type,
        version=version or get_current_document_version(document_type),
        ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        source=source,
    )


def stash_yandex_oauth_consent(request: HttpRequest) -> None:
    request.session[SOCIAL_CONSENT_SESSION_KEY] = {
        "document_type": Consent.DocumentType.PERSONAL_DATA,
        "version": get_current_document_version(
            Consent.DocumentType.PERSONAL_DATA
        ),
        "source": Consent.Source.YANDEX_OAUTH,
        "issued_at": timezone.now().isoformat(),
    }


def pop_yandex_oauth_consent(request: HttpRequest) -> dict[str, str] | None:
    consent = request.session.pop(SOCIAL_CONSENT_SESSION_KEY, None)
    if not isinstance(consent, dict):
        return None

    issued_at = consent.get("issued_at")
    if not isinstance(issued_at, str):
        return None
    try:
        issued_at_dt = datetime.fromisoformat(issued_at)
    except ValueError:
        return None
    if timezone.is_naive(issued_at_dt):
        issued_at_dt = issued_at_dt.replace(tzinfo=UTC)
    if timezone.now() - issued_at_dt > SOCIAL_CONSENT_TTL:
        return None

    document_type = consent.get("document_type")
    version = consent.get("version")
    source = consent.get("source")
    if not isinstance(document_type, str):
        return None
    if not isinstance(version, str):
        return None
    if not isinstance(source, str):
        return None
    return {
        "document_type": document_type,
        "version": version,
        "source": source,
    }


def peek_yandex_oauth_consent(request: HttpRequest) -> bool:
    consent = pop_yandex_oauth_consent(request)
    if consent is None:
        return False
    request.session[SOCIAL_CONSENT_SESSION_KEY] = {
        **consent,
        "issued_at": timezone.now().isoformat(),
    }
    return True


def serialize_consent(consent: Consent) -> dict[str, Any]:
    return {
        "id": consent.pk,
        "document_type": consent.document_type,
        "version": consent.version,
        "timestamp": consent.timestamp.isoformat(),
        "ip": consent.ip,
        "user_agent": consent.user_agent,
        "source": consent.source,
    }


def serialize_user_consent_history(user: User) -> list[dict[str, Any]]:
    return [
        serialize_consent(consent)
        for consent in user.consents.all().order_by("-timestamp", "-id")
    ]
