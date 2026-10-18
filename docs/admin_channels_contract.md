# Контракт админки для каналов

## GET `/admin/channels/`

Страница доступна только администраторам.

Успешный ответ содержит Inertia payload с компонентом `AdminChannels` и props, сформированными через `AdminChannelsDTO`.

Пример props:

```json
{
  "channels": [
    {
      "channelId": 12345,
      "username": "example",
      "title": "Example channel",
      "category": "Технологии",
      "isVerified": true,
      "subscribers": 15000
    }
  ],
  "categories": [
    "Новости и СМИ",
    "Технологии",
    "Образование"
  ]
}
```

Пример иллюстративный. Реальные каналы и категории зависят от данных приложения.

### `channels`

Список каналов, связанных хотя бы с одной заявкой со статусом `approved`. Повторяющиеся каналы исключаются. Сортировка выполняется по названию, затем по ID канала.

Каждый элемент содержит:

- `channelId` (`int`) — ID канала в Telegram;
- `username` (`string`) — username канала или пустую строку;
- `title` (`string`) — название канала;
- `category` (`string`) — категория или пустую строку;
- `isVerified` (`bool`) — признак верификации;
- `subscribers` (`int`) — количество участников.

### `categories`

Список допустимых категорий из `ChannelParseForm`. Служебные варианты «Выберите категорию...» и «Все категории» исключены.

## POST `/admin/moderation/channels/category/`

Изменяет категорию канала. Доступно только администраторам.

Поля формы:

- `channel_id` — ID канала;
- `category` — одно из значений `categories`.

При успехе выполняется redirect на `/admin/channels/`. Некорректный ID, недопустимая категория или отсутствующий канал приводят к `400 Bad Request`.

## POST `/admin/moderation/channels/verified/`

Переключает значение `isVerified` для канала. Доступно только администраторам.

Поле формы:

- `channel_id` — ID канала.

При включении верификации `verified_at` устанавливается в текущее время; при отключении очищается. При успехе выполняется redirect на `/admin/channels/`. Некорректный ID или отсутствующий канал приводят к `400 Bad Request`.

## POST `/admin/moderation/channels/add/`
Добавляет канал напрямую в одобренные. Доступно только администраторам.

Поля формы:

- `identifier` — username или ссылка на канал;
- `category` — допустимая категория из `categories`.

Бэкенд получает данные канала из Telegram. Канал должен иметь публичный username. Если канал с таким username или ID уже существует, добавление отклоняется. При успешном добавлении создаются запись канала и заявка со статусом `approved`.

При успехе выполняется redirect на `/admin/channels/`. Ошибки валидации и получения данных канала приводят к `400 Bad Request`.

## Общие Inertia props

Общие props (`auth`, `role`, `is_admin`, `csrfToken`, `flash`) передаются middleware. Их контракт описан в [`inertia-shared-props.md`](./inertia-shared-props.md).
