# Контракт админки статей блога

## Общее

- Базовый URL — `/admin/blog/`.
- Доступ — только роль `admin` (`AdminRequiredMixin`). Гость и остальные роли
  получают `403`.
- Inertia-компонент — `AdminBlog`. Файл страницы
  `frontend/src/pages/AdminBlog.tsx` пока отсутствует — это отдельная
  frontend-задача.
- Общие props (`auth`, `role`, `is_admin`, `csrfToken`, `flash`) передаются
  middleware. Их контракт описан в
  [`inertia-shared-props.md`](./inertia-shared-props.md).

## GET `/admin/blog/`

Возвращает все статьи, включая черновики, от новых к старым
(`created_at desc`).

```json
{
  "component": "AdminBlog",
  "props": {
    "articles": [
      {
        "id": 1,
        "title": "Как вести Telegram-канал",
        "slug": "kak-vesti-telegram-kanal",
        "excerpt": "Короткий анонс статьи.",
        "cover_image": "https://example.com/cover.jpg",
        "body": "## Текст статьи",
        "category": "marketing",
        "tags": ["telegram", "маркетинг"],
        "is_featured": false,
        "is_published": true,
        "published_at": "2026-11-04T10:00:00Z",
        "read_time": 7,
        "views_count": 0,
        "author_name": "Админ",
        "created_at": "2026-11-01T09:00:00Z",
        "updated_at": "2026-11-04T10:00:00Z"
      }
    ],
    "categories": [
      { "value": "marketing", "label": "Маркетинг" }
    ],
    "errors": {}
  },
  "url": "/admin/blog/"
}
```

### `articles`

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `id` | `int` | да | PK статьи |
| `title` | `str` | да | заголовок |
| `slug` | `str` | да | уникальный слаг |
| `excerpt` | `str` | да | анонс |
| `cover_image` | `str` | да | URL обложки или `""` |
| `body` | `str` | да | тело статьи (Markdown) |
| `category` | `str` | да | значение из `categories[]` |
| `tags` | `str[]` | да | список тегов, по умолчанию `[]` |
| `is_featured` | `bool` | да | «в избранном» |
| `is_published` | `bool` | да | `false` — черновик |
| `published_at` | `str \| null` | да | `null`, пока статья не публиковалась |
| `read_time` | `int` | да | время чтения, минут |
| `views_count` | `int` | да | просмотры, меняются публичной страницей |
| `author_name` | `str \| null` | да | полное имя автора или username |
| `created_at` | `str` | да | ISO 8601 |
| `updated_at` | `str` | да | ISO 8601 |

### `categories`

Варианты из `BlogArticle.CATEGORY_CHOICES` в порядке модели:

```json
[{ "value": "marketing", "label": "Маркетинг" }]
```

### `errors`

Всегда присутствует: `{}` на успешном ответе, ошибки полей формы — при
неуспешной валидации.

## POST `/admin/blog/`

Создаёт статью. Автор проставляется автоматически — текущий администратор,
поле `author` из запроса игнорируется.

Тело запроса — JSON или данные формы. Поля (все, кроме отмеченных, обяз.):
`title`, `slug`, `excerpt`, `cover_image`, `body`, `category`, `tags`,
`is_featured`, `is_published`, `read_time`.

| поле | тип | обяз. | примечание |
|------|-----|-------|------------|
| `title` | `str` | да | до 200 символов |
| `slug` | `str` | да | уникальный, до 220 символов |
| `excerpt` | `str` | да | |
| `cover_image` | `str` | нет | валидный URL или `""` |
| `body` | `str` | да | |
| `category` | `str` | да | одно из `categories[].value` |
| `tags` | `str[]` | нет | JSON-массив строк |
| `is_featured` | `bool` | нет | по умолчанию `false` |
| `is_published` | `bool` | нет | по умолчанию `false` (черновик) |
| `read_time` | `int` | нет | по умолчанию `5` |

`tags` передаётся JSON-массивом. В form-encoded запросе допускается
JSON-строка: `tags=["python", "ai"]`.

Ответы:

- успех — `302` redirect на `/admin/blog/`, в сессии
  `flash = {"success": "Статья создана"}`;
- ошибка валидации — `200` и props `errors` (действующее соглашение проекта);
- не-админ — `403`.

## PATCH `/admin/blog/<pk>/`

Частичное обновление: меняются только переданные поля, остальные берутся из
текущей статьи. Тело запроса — JSON.

Ответы:

- успех — redirect на `/admin/blog/`; для Inertia middleware приводит `302`
  к `303`, `flash = {"success": "Статья обновлена"}`;
- ошибка валидации — `200` и props `errors`, данные не сохраняются;
- неизвестный `pk` — `404`;
- не-админ — `403`.

## DELETE `/admin/blog/<pk>/`

Удаляет статью. Тело запроса не требуется.

Ответы:

- успех — redirect на `/admin/blog/` (`303` для Inertia),
  `flash = {"success": "Статья удалена"}`;
- неизвестный `pk` — `404`;
- не-админ — `403`.

## Ошибки валидации

Формат элемента ошибки — результат `form.errors.get_json_data()`:

```json
{
  "component": "AdminBlog",
  "props": {
    "articles": [],
    "categories": [],
    "errors": {
      "slug": [
        {
          "message": "Статья с таким Слаг уже существует.",
          "code": "unique"
        }
      ]
    }
  },
  "url": "/admin/blog/"
}
```

Ключи `articles` и `categories` в ответе с ошибкой также заполняются сервисом;
в примере сокращены до пустых массивов.

## draft vs published

- `is_published = false` — черновик: публичный `/blog/` его не показывает.
- При первой публикации модель `BlogArticle.save()` сама проставляет
  `published_at`.
- Снятие с публикации оставляет `published_at` без изменений — это дата
  первой публикации.
