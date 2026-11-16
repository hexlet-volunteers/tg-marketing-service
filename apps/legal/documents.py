LEGAL_DOCUMENTS = {
    "privacy": {
        "title": "Политика конфиденциальности",
        "updated_at": "2026-07-01",
        "text": (
            "Мы собираем и обрабатываем персональные данные пользователей "
            "исключительно для целей предоставления сервиса аналитики "
            "Telegram-каналов. Мы не передаём данные третьим лицам без явного "
            "согласия пользователя."
        ),
    },
    "agreement": {
        "title": "Пользовательское соглашение",
        "updated_at": "2026-07-01",
        "text": (
            "Используя сервис TG Pulse, вы соглашаетесь с данными условиями. "
            "Сервис предоставляет инструменты аналитики Telegram-каналов "
            "«как есть» без гарантий точности данных."
        ),
    },
    "offer": {
        "title": "Публичная оферта",
        "updated_at": "2026-07-01",
        "text": (
            "Настоящая оферта адресована физическим и юридическим лицам "
            "и определяет условия предоставления платных услуг сервиса "
            "TG Pulse на условиях подписки."
        ),
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
