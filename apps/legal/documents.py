LEGAL_DOCUMENTS = {
    "privacy": {
        "title": (
            "\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430 "
            "\u043a\u043e\u043d\u0444\u0438\u0434\u0435\u043d"
            "\u0446\u0438\u0430\u043b\u044c\u043d\u043e\u0441"
            "\u0442\u0438"
        ),
        "updated_at": "2026-07-01",
    },
    "agreement": {
        "title": (
            "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430"
            "\u0442\u0435\u043b\u044c\u0441\u043a\u043e\u0435 "
            "\u0441\u043e\u0433\u043b\u0430\u0448\u0435"
            "\u043d\u0438\u0435"
        ),
        "updated_at": "2026-07-01",
    },
    "offer": {
        "title": (
            "\u041f\u0443\u0431\u043b\u0438\u0447\u043d\u0430\u044f "
            "\u043e\u0444\u0435\u0440\u0442\u0430"
        ),
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
