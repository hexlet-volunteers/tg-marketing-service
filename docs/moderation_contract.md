# Контракт модерации

## GET `/admin/moderation/`

Endpoint доступен только администраторам через `AdminRequiredMixin`.

Успешный ответ содержит Inertia-payload:

```json
{
  "component": "AdminModeration",
  "props": {
    "pendingRequests": [],
    "pendingCount": 0,
    "pagination": {
      "page": 1,
      "perPage": 10,
      "pages": 0,
      "hasNext": false,
      "hasPrevious": false
    }
  },
  "url": "/admin/moderation/"
}
```

Общие Inertia props (`auth`, `role`, `is_admin`, `csrfToken`, `flash`)
передаются middleware. Их контракт описан в
[`inertia-shared-props.md`](./inertia-shared-props.md).

### Query-параметры

- `page` — номер страницы, по умолчанию `1`.
- Размер страницы — `10` заявок.
- Некорректный номер страницы нормализуется Django `Paginator`.

### `pendingRequests`

Массив pending-заявок в порядке `created_at`, затем `id`:

```json
{
  "id": 1,
  "submitted_by": {
    "id": 10,
    "username": "user"
  },
  "channel_identifier": "@example",
  "channel": {
    "id": 20,
    "username": "example",
    "title": "Example channel"
  },
  "category": "technology",
  "country": "RU",
  "language": "ru",
  "status": "pending",
  "reject_reason": null,
  "created_at": "2026-08-13T10:00:00+00:00",
  "resolved_at": null
}
```

`submitted_by` и `channel` могут быть `null`.

`pendingCount` содержит общее количество заявок со статусом `pending`, а
не количество заявок на текущей странице.

## POST `/admin/moderation/`

POST обрабатывается тем же endpoint. Обязательные поля для обоих действий:

- `action` — `approve` или `reject`;
- `request_id` — идентификатор заявки.

После обработки endpoint делает redirect to get.
Результат операции передаётся через session flash
для следующего GET-запроса.

### Approve

Поля запроса:

- `action=approve`;
- `request_id`;
- `category` — обязательная непустая категория длиной не более 255 символов;
- `is_verified` — значение `true` включает проверку канала, остальные значения
  трактуются как `false`.

При успешном approve канал публикуется, получает категорию и значение
`is_verified`, а заявка получает статус `approved`, модератора и время обработки.

Если найден другой канал с тем же username без учёта регистра, заявка
получает статус `duplicate`, модератор и время обработки.

### Reject

Поля запроса:

- `action=reject`;
- `request_id`;
- `reason` — обязательная непустая причина отклонения.

При успешном reject заявка получает статус `rejected`, причину, модератора и
время обработки.

Ошибки валидации и попытка повторно обработать заявку передаются через
`flash.error`; успешные операции — через `flash.success`. Некорректный
`request_id` и неизвестный `action` возвращают `400 Bad Request`.
