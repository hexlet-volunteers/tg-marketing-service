# Экспорт персональных данных

## Эндпоинт

`GET /auth/me/personal-data/export/` или
`POST /auth/me/personal-data/export/` скачивает JSON-файл с персональными
данными текущего авторизованного пользователя.

Параметры пользователя в URL или теле запроса не принимаются. Сервер всегда
определяет субъекта по аутентифицированной сессии. Ответ нельзя кэшировать.

## Ответ

- `Content-Type: application/json; charset=utf-8`
- `Content-Disposition: attachment; filename="personal-data-<id>-<date>.json"`
- `Cache-Control: no-store`

Корневая схема формата `1.1`:

```json
{
  "format_version": "1.1",
  "exported_at": "2026-09-29T12:00:00+00:00",
  "subject_id": 42,
  "personal_data": {
    "profile": {},
    "owned_groups": [],
    "channel_moderator_assignments": [],
    "ai_insights": [],
    "consents": [],
    "subject_requests": [],
    "partner_profile": {}
  },
  "processing_information": {
    "processing_confirmed": true,
    "purposes": [],
    "legal_basis": [],
    "retention_terms": [],
    "personal_data_fields": {}
  }
}
```

`partner_profile` присутствует только при наличии партнёрского профиля.
Денежное поле `balance` передаётся строкой, чтобы не терять точность. Даты
передаются в ISO 8601, отсутствующие даты — как `null`.

Группы, назначения модератором и AI-инсайты сортируются по возрастанию
внутреннего `id`. `consents` сортируются по `-timestamp`, при одинаковом
времени — по `-id`. `subject_requests` сортируются по `-requested_at`;
порядок запросов с одинаковым временем не гарантирован.

## Журналы

`personal_data.consents` — история согласий текущего пользователя, включая
отозванные. Если записей нет, возвращается `[]`. Поля каждой записи:

- `id` — идентификатор согласия;
- `document_type` — `privacy_policy`, `personal_data` или `cookie_analytics`;
- `version` — версия принятого документа;
- `timestamp` — дата и время получения согласия;
- `ip` — IP-адрес или `null`;
- `user_agent` — User-Agent, пустая строка, если он отсутствовал;
- `source` — `email_registration`, `yandex_oauth` или `cookie_banner`;
- `withdrawn_at` — дата и время отзыва или `null`;
- `withdrawal_request_id` — ID запроса отзыва или `null`.

`personal_data.subject_requests` — журнал запросов текущего пользователя.
Если записей нет, возвращается `[]`. Поля каждой записи:

- `id` — идентификатор запроса;
- `request_type` — `access`, `rectification`, `export`, `deletion` или `withdrawal`;
- `requested_at` — дата и время поступления;
- `due_at` — текущий срок исполнения;
- `original_due_at` — первоначальный срок исполнения;
- `completed_at` — дата и время завершения или `null`;
- `status` — `received`, `processing`, `failed` или `completed`;
- `result` — JSON-объект результата, до фиксации результата — `{}`;
- `extension_reason` — причина продления, без продления — пустая строка.

Файл содержит снимок журнала на момент формирования экспорта. Запрос текущего
экспорта уже включён, но его завершение фиксируется после формирования файла,
поэтому в снимке он имеет статус `received` и `completed_at=null`.

## Версия формата

`1.1` документирует добавленные массивы `consents` и `subject_requests`.
Остальные ключи формата `1.0` сохранены. Значение `format_version` задаётся
сервером в `apps/users/personal_data_export.py`.

Экспорт содержит только группы, назначения модератором и AI-инсайты текущего
пользователя. Профили авторов каналов и записи других модераторов в файл не
включаются. Каждый успешный экспорт фиксируется в журнале запросов субъектов.
