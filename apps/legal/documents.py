LEGAL_DOCUMENTS = {
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

CONSENT_DOCUMENTS = {
    "privacy_policy": LEGAL_DOCUMENTS["privacy"],
    "personal_data": {
        "title": "Personal data processing consent",
        "updated_at": "2026-07-01",
    },
    "cookie_analytics": {
        "title": "Cookie analytics consent",
        "updated_at": "2026-07-01",
    },
}


def get_consent_document_version(document_type: str) -> str:
    return CONSENT_DOCUMENTS[document_type]["updated_at"]
