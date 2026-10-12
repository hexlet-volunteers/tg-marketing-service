# Inertia-контракт

Единый источник правды о том, **что возвращает backend** и **что ожидает frontend**
для каждого Inertia-экрана и каждой модалки.

Пишется параллельно FE и BE: изменения формы `props` здесь — это сигнал
обязательного согласования обеими сторонами. Если контракт не обновлён, экран
считается незавершённым.

Связанные документы:

- [`inertia-shared-props.md`](./inertia-shared-props.md) — контракт общих props;
- [`moderation_contract.md`](./moderation_contract.md) — детальный контракт `/admin/moderation/`;
- [`collections_catalog_contract.md`](./collections_catalog_contract.md) — детальный контракт `/collections/`;
- [`registration_contract.md`](./registration_contract.md) — детальный контракт регистрации.

## Конверт ответа

Каждый Inertia-ответ имеет форму:

```json
{
  "component": "<ИмяКомпонента>",
  "props": { "...": "..." },
  "url": "<request.path>"
}
```

`url` всегда равен текущему `request.path` (совпадает с адресом в браузере).
Переопределить его на стороне backend нельзя — для смены URL используется
redirect. `component` обязан совпадать с именем файла страницы
`frontend/src/pages/<Name>.tsx`, иначе клиент падает с `Page <name> not found`
(резолвер — glob, см. [Именование](#именование)).

## Общие props

Каждый ответ дополнительно содержит общие props `auth`, `role`, `is_admin`,
`csrfToken`, `flash`. Они формируются один раз в
`config.middleware.SharedInertiaPropsMiddleware` и **не переопределяются** во
views. Контракт — [`inertia-shared-props.md`](./inertia-shared-props.md).

Использовать в docstring-примерах ниже ключи `auth`, `role`, `is_admin`,
`csrfToken`, `flash` не требуется: они подразумеваются в любом ответе.

## Именование

Действующие имена компонентов — файл
`frontend/src/pages/<Name>.tsx` с `export default function <Name>`.

Резолвер (`frontend/src/main.tsx:11-21`) построен на `import.meta.glob` и
поддерживает **любое** имя, для которого существует файл страницы:

```tsx
const pages = import.meta.glob<ComponentType>("./pages/**/*.tsx");
// resolve(name) -> pages[`./pages/${name}.tsx`]
```

Если файла `frontend/src/pages/<Name>.tsx` нет — клиент падает с
`Page <name> not found`. Поэтому контракт фиксирует не только строку
`component`, но и наличие соответствующего файла страницы.

## Состояние интеграции

Легенда: `✅` — есть, `❌` — нет, `🔸` — мок/заглушка.

| Компонент | URL | Django view | Страница `pages/<Name>.tsx` | Props |
|-----------|-----|-------------|-----------------------------|-------|
| `Landing` | `/` | ✅ `IndexView` | ✅ `Landing.tsx` | ✅ реальные |
| `Auth` | `/auth/login/` | ✅ `LoginView` | ✅ `Auth.tsx` | ✅ реальные |
| `Channels` | `/channels/` | ✅ `ChannelCatalogView` | ✅ `Channels.tsx` | 🔸 мок |
| `Dashboard` | `/dashboard/` | ✅ `DashboardView` | ✅ `Dashboard.tsx` | ✅ реальные |
| `Post` | см. Post | ✅ 3 views | ✅ `Post.tsx` | ✅/🔸 |
| `Compare` | `/compare/` | ✅ `CompareView` | ✅ `Compare.tsx` | 🔸 мок |
| `AICabinet` | `/ai-cabinet/` | ✅ `AICabinetView` | ✅ `AICabinet.tsx` | 🔸 мок |
| `Collections` | `/collections/` | ✅ `CollectionsCatalogView` | ✅ `Collections.tsx` | ✅ реальные |
| `Collection` | `/collections/<pk>/` | ✅ `CollectionDetailView` | ✅ `Collection.tsx` | 🔸 мок |
| `Profile` (account) | `/auth/profile/` | ✅ `UserCabinetView` | ✅ `Profile.tsx` | ✅ реальные |
| `Blog` | `/blog/` | ✅ `BlogListView` | ✅ `Blog.tsx` | ✅ реальные |
| `BlogPost` | `/blog/<slug>/` | ✅ `BlogArticleDetailView` | ✅ `BlogPost.tsx` | ✅ реальные |
| `Legal` | `/legal/` | ✅ `LegalView` | ✅ `Legal.tsx` | ✅ реальные |
| `Admin` | `/admin/moderation/` | ✅ `ModerationRequestListView` | ✅ `Admin.tsx` | ✅ реальные |
| `NotFound` | `/<path>/` | ✅ `NotFoundView` | ✅ `NotFound.tsx` | ✅ пустые |

15 файлов страниц в `frontend/src/pages/` покрывают все 14 экранов + `Auth`.

Осталось добавить — компоненты, которые backend отдаёт, но страницы
`pages/<Name>.tsx` пока нет (эти маршруты **сейчас не отдаются** и упадут):

| Компонент | URL | Django view | Статус |
|-----------|-----|-------------|--------|
| `FormRegistration` | `/auth/create/` | ✅ `UserRegister` | ❌ нет `pages/FormRegistration.tsx` |
| `GroupDetail` | `/group/<slug>/` (GET), `/group/<slug>/add-channels/` (POST) | ✅ `GroupDetailView`, `AddChannelsView` | ❌ нет страницы |
| `ChannelAnalytics` | `/parser/list` | ✅ `ParserListView` | ❌ нет страницы |
| `UpdateUserProfile` | `/auth/<username>/update/` | ✅ `UserUpdate` | ❌ нет страницы |
| `RestorePasswordRequest` | `/auth/restore-password/` | ✅ `RestorePasswordRequestView` | ❌ нет страницы |
| `RestorePassword` | `/auth/restore-password/<uidb64>/<token>/` | ✅ `RestorePasswordView` | ❌ нет страницы |

`PasswordRecovery` — не страница, а модалка
(`frontend/src/components/modals/PasswordRecovery.tsx`), открывается из
`Auth`/`FormRegistration`.

> ⚠️ Часть backend-маршрутов ещё **не закоммичена** (working tree):
> `config/urls.py` (`/collections/<pk>/`, `/channels/`, `/compare/`, `/post/`,
> `/ai-cabinet/`, catch-all `NotFound`), `apps/ai/urls.py` и изменения
> `apps/ai/views.py`, `apps/parser/views.py`, `config/views.py`,
> `apps/group_channels/views.py`. Строки `component` в этих views уже
> канонические.

---

# Экраны

## Landing — `/`

Публичная страница. Авторизованные пользователи редиректятся на
`/dashboard/` (`config/views.py`).

```json
{
  "component": "Landing",
  "props": {
    "components": [
      {
        "component": "<HomePageComponent.component_type>",
        "props": {
          "id": 1,
          "title": "Заголовок блока",
          "type": "hero",
          "order": 1,
          "...content": "распакованное JSON-содержимое HomePageComponent.content"
        },
        "url": "/"
      }
    ]
  },
  "url": "/"
}
```

Примечания:

- `components` — активные (`is_active=True`) компоненты, отсортированы по `order`;
- `props` собирается из базовых полей модели `HomePageComponent` + распаковки
  `content`;
- `component`/`url` внутри элемента — слоты отдельных блоков страницы, не
  Inertia-компоненты.

## Auth — `/auth/login/`

```json
{
  "component": "Auth",
  "props": {
    "form": {
      "data": { "email": "", "password": "" },
      "errors": {}
    }
  },
  "url": "/auth/login/"
}
```

- `GET` — пустая форма (`password` всегда пустой);
- `POST` невалидный — повторный рендер `Auth` с `form.errors` и сохранённым `email`
  (пароль сбрасывается);
- `POST` валидный — рендер `Landing` с `flash.success` и
  `user: {username}` (см. [модалку «Логин»](#логин)).

## Channels — `/channels/`

Каталог каналов. Данные карточек пока **моковые** — на стороне frontend
(`ChannelCatalogView` рендерит без props).

```json
{
  "component": "Channels",
  "props": {},
  "url": "/channels/"
}
```

Планируемая форма (ожидания FE, `types/channel.ts`):

```json
{
  "component": "Channels",
  "props": {
    "channels": [
      {
        "id": 1,
        "name": "Tech News RU",
        "username": "technews",
        "type": "channel",
        "subscribers": 45200,
        "category": "technology",
        "verified": true,
        "country": "ru",
        "imageUrl": "https://...",
        "er": 3.2,
        "growth30d": 12.3
      }
    ]
  },
  "url": "/channels/"
}
```

## Dashboard — `/dashboard/`

Защищённый экран: неавторизованные редиректятся на `/`.

```json
{
  "component": "Dashboard",
  "props": {
    "stats": {
      "channels": 47,
      "posts": 2347,
      "ai_suggestions": 89,
      "days_left": 23
    },
    "channels": [
      { "name": "Tech News RU", "subscribers": 45200, "posts": 24, "views": 156000, "engagement": 78.5, "growth": 12.3 }
    ],
    "ai_insights": [
      { "text": "Тренд: посты о новых ИИ инструментах набирают +45% просмотров", "type": "trend", "id": 1 }
    ],
    "collections": [
      { "name": "IT & Технологии", "channels_count": 23, "slug": "it-tech", "description": "Каналы про IT и технологии", "is_auto": false }
    ],
    "quick_actions": ["Добавить канал", "Экспорт данных", "Настройки"]
  },
  "url": "/dashboard/"
}
```

Примечания:

- `channels` — первые 5 каналов;
- `ai_insights` — до 5 непрочитанных;
- `engagement` = `views / subscribers * 100` (0..100), `growth` — % роста;
- `days_left` — дней до конца подписки;
- `is_auto` — признак автоколлекции.

## Post — детальный разбор поста

Компонент `Post` отдают три маршрута:

| URL | View | props |
|-----|------|-------|
| `/parser/post/<channel_id>/<telegram_message_id>/` | `PostDetailView` | `post` + `channel` + `csrfToken` |
| `/parser/ai/channels/<channel_id>/posts/<post_id>/analysis` | `PostAIAnalysisView` | только `post` (`channel`, `csrfToken` = `null`) |
| `/post/` | `PostPageView` | **мок**, `props: {}` |

```json
{
  "component": "Post",
  "props": {
    "post": {
      "id": 1,
      "telegram_message_id": 100500,
      "channel_id": 2,
      "text": "Текст поста",
      "hashtags": ["#tech", "#ai"],
      "published_at": "2026-09-01T10:00:00+00:00",
      "views": 15200,
      "forwards": 340,
      "comments_count": 18,
      "is_pinned": false,
      "media_type": "photo",
      "permalink": "https://t.me/example/100500",
      "er": 3.4,
      "reactions": { "total": 120, "details": {} },
      "post_analysis": {
        "status": "completed",
        "why_worked": ["Причина успеха"],
        "how_to_improve": ["Как улучшить"],
        "similar_posts": [
          {
            "id": 5,
            "telegram_message_id": 3,
            "text": "Похожий пост",
            "published_at": "2026-08-30T12:00:00+00:00",
            "permalink": "https://t.me/example/3",
            "views": 8000,
            "forwards": 100,
            "comments_count": 5,
            "total_reactions": 60
          }
        ],
        "model_version": "claude-3-5"
      }
    },
    "channel": {
      "id": 2,
      "username": "example",
      "title": "Example channel",
      "description": "...",
      "participants_count": 1000,
      "parsed_at": null,
      "pinned_messages": [],
      "creation_date": null,
      "last_messages": [],
      "average_views": 5000,
      "category": null,
      "country": null,
      "language": null,
      "is_verified": false,
      "verified_at": null
    },
    "csrfToken": "<token>"
  },
  "url": "/parser/post/2/100500/"
}
```

Примечания:

- `post_analysis.status` — `"processing"` (анализ запущен фоном) или
  `"completed"`;
- `er` — engagement rate поста;
- `reactions` = `{total, details}`;
- `channel` и `csrfToken` могут отсутствовать (равны `null`) на маршруте
  AI-анализа;
- docstring `PostDetailView` указывает URL `/post/...` — фактический
  `/parser/post/...`.

## Compare — `/compare/`

Сравнение каналов. **Мок** (`CompareView` рендерит без props, данные на
frontend).

```json
{
  "component": "Compare",
  "props": {},
  "url": "/compare/"
}
```

Планируемая форма (FE, `types/channel.ts`):

```json
{
  "component": "Compare",
  "props": {
    "metrics": [{ "key": "subscribers", "label": "Подписчики" }],
    "channels": []
  },
  "url": "/compare/"
}
```

## AICabinet — `/ai-cabinet/`

AI-кабинет автора. **Мок** (`AICabinetView` рендерит без props).

```json
{
  "component": "AICabinet",
  "props": {},
  "url": "/ai-cabinet/"
}
```

Планируемая форма (FE, `types/aiCabinet.ts`):

```json
{
  "component": "AICabinet",
  "props": {
    "ideas": [],
    "insights": [],
    "competitors": [],
    "heatMapData": {}
  },
  "url": "/ai-cabinet/"
}
```

## Collections — `/collections/`

Публичный каталог подборок. Детальный контракт —
[`collections_catalog_contract.md`](./collections_catalog_contract.md).

```json
{
  "component": "Collections",
  "props": {
    "featured": [
      {
        "id": 1,
        "name": "Новости",
        "slug": "novosti",
        "description": "Новостные каналы",
        "is_editorial": true,
        "curator": "curator",
        "channel_count": 12,
        "cover": "https://example.com/cover.jpg",
        "gradient_key": "collection-1"
      }
    ],
    "collections": []
  },
  "url": "/collections/"
}
```

Примечания:

- `featured` — до 3 подборок (`is_editorial DESC → order ASC → id ASC`);
- `collections` — полный список, сортировка `order ASC → name ASC → id ASC`;
- `gradient_key` формируется как `collection-<id>`.

## Collection — `/collections/<pk>/`

Детальная страница подборки. Содержимое **мок** (`CollectionDetailView`
рендерит без props, существование подборки не проверяется).

```json
{
  "component": "Collection",
  "props": {},
  "url": "/collections/1/"
}
```

Планируемая форма (FE, `types/channel.ts`):

```json
{
  "component": "Collection",
  "props": {
    "channels": [
      { "name": "Tech News RU", "username": "technews", "subscribers": 45200, "er": 3.2, "growth30d": 12.3, "color": "blue" }
    ]
  },
  "url": "/collections/1/"
}
```

## Profile — account, `/auth/profile/`

Личный кабинет. Защищённый экран.

```json
{
  "component": "Profile",
  "props": {
    "user": {
      "id": 1,
      "first_name": "Иван",
      "last_name": "Петров",
      "username": "ivan",
      "email": "ivan@example.com",
      "avatar": "https://...",
      "role": "user",
      "bio": "Описание"
    },
    "subscription": {
      "plan": "pro",
      "period": "month",
      "price": "990.00",
      "current_period_end": "2026-11-01T00:00:00+00:00",
      "limits": { "channels": 50, "ai_requests": 100 },
      "days_left": 21,
      "channels_used": 12,
      "ai_requests_used": 21
    },
    "notifications": null,
    "usage_stats": {
      "registration_date": "01.01.2026",
      "last_visit": "10.10.2026",
      "total_time": "123 часов"
    },
    "user_role": "user"
  },
  "url": "/auth/profile/"
}
```

Примечания:

- docstring `UserCabinetView` называет компонент `UserProfilePage`,
  фактический — `Profile`;
- `POST` валидный — redirect на `/auth/profile/` (`users:user_cabinet`), изменения
  отдаются только после перезагрузки;
- `POST` невалидный — повторный рендер `Profile` c `errors` и `values`
  (`first_name`, `last_name`, `email`, `bio`, `avatar_image`);
- `notifications` пока всегда `null`.

## Blog — `/blog/`

Публичный список статей.

```json
{
  "component": "Blog",
  "props": {
    "featured": {
      "id": 1,
      "slug": "kak-rabotaet-ai",
      "title": "Как работает ИИ",
      "excerpt": "Краткое описание",
      "cover_image": "",
      "category": "Технологии",
      "tags": ["ai"],
      "read_time": 5,
      "published_at": "2026-09-01T10:00:00+00:00",
      "views_count": 1200,
      "author_name": "Автор"
    },
    "articles": []
  },
  "url": "/blog/"
}
```

Примечания:

- только `is_published=True`;
- `featured` — последняя `is_featured=True`, может быть `null`;
- `articles` — остальные, `published_at desc`.

## BlogPost — `/blog/<slug>/`

Публичная детальная страница статьи.

```json
{
  "component": "BlogPost",
  "props": {
    "id": 1,
    "slug": "kak-rabotaet-ai",
    "title": "Как работает ИИ",
    "excerpt": "Краткое описание",
    "cover_image": "",
    "category": "Технологии",
    "tags": ["ai"],
    "read_time": 5,
    "published_at": "2026-09-01T10:00:00+00:00",
    "views_count": 1200,
    "author_name": "Автор",
    "body": "# Markdown",
    "cta": { "label": "Читать ещё", "url": "/blog/" },
    "related": []
  },
  "url": "/blog/kak-rabotaet-ai/"
}
```

Примечания:

- `body` — Markdown;
- `cta` — дескриптор CTA-кнопки;
- `related` — не более 3 статей;
- `views_count` растёт только при полной загрузке (не Inertia-навигации);
- docstring DTO называет страницу `BlogArticle` — фактический компонент
  `BlogPost`.

## Legal — `/legal/`

Публичная страница правовых документов. Отдаёт только метаданные.

```json
{
  "component": "Legal",
  "props": {
    "documents": {
      "privacy": { "title": "Политика конфиденциальности", "updated_at": "2026-07-01" },
      "agreement": { "title": "Пользовательское соглашение", "updated_at": "2026-07-01" },
      "offer": { "title": "Публичная оферта", "updated_at": "2026-07-01" }
    }
  },
  "url": "/legal/"
}
```

## Admin — `/admin/moderation/`

Модерация заявок. Только для администраторов (`AdminRequiredMixin`).
Детальный контракт — [`moderation_contract.md`](./moderation_contract.md).

```json
{
  "component": "Admin",
  "props": {
    "pendingRequests": [
      {
        "id": 1,
        "submitted_by": { "id": 10, "username": "user" },
        "channel_identifier": "@example",
        "channel": { "id": 20, "username": "example", "title": "Example channel" },
        "category": "technology",
        "country": "RU",
        "language": "ru",
        "status": "pending",
        "reject_reason": null,
        "created_at": "2026-08-13T10:00:00+00:00",
        "resolved_at": null
      }
    ],
    "pendingCount": 15,
    "pagination": {
      "page": 1,
      "perPage": 10,
      "pages": 2,
      "hasNext": true,
      "hasPrevious": false
    }
  },
  "url": "/admin/moderation/?page=1"
}
```

Примечания:

- `GET` поддерживает query-параметр `page` (по умолчанию 1, размер 10);
- `pendingCount` — общее число `pending`-заявок, не размер текущей страницы;
- `submitted_by` и `channel` могут быть `null`.

## NotFound — `/<path>/`

Catch-all для несопоставленных URL. Ответ всегда имеет статус 404.

```json
{
  "component": "NotFound",
  "props": {},
  "url": "/no-such-page/"
}
```

---

# Модалки

Формат ошибок валидации единый для всех форм:

```json
{
  "form": {
    "data": { "<field>": "<value>", "password1": "", "password2": "" },
    "errors": { "<field>": [{ "message": "Текст ошибки", "code": "invalid" }] }
  }
}
```

Пароли после невалидного POST в `form.data` всегда пустые.

## Логин

- Модалка/форма: `Auth` → `FormRegistration` (внутри `Auth.tsx`).
- POST-эндпоинт: `POST /auth/login/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Landing`, props `{"flash": {"success": "Вы залогинены"}, "user": {"username": ...}}` |
| невалидный | рендер `Auth`, props `{"form": {"data": {email, password:""}, "errors"}}` |

## Регистрация

- Модалка/форма: `FormRegistration` (`components/ui/FormRegistration.tsx`,
  встроена в страницу `Auth`).
- POST-эндпоинт: `POST /auth/create/`.
- Детали — [`registration_contract.md`](./registration_contract.md).

> ⚠️ `UserRegister` рендерит `component: "FormRegistration"`, но страницы
> `pages/FormRegistration.tsx` нет — невалидный POST упадёт. Нужно вынести
> регистрацию в `pages/Auth.tsx` или создать страницу.

| Сценарий | Ответ |
|----------|-------|
| валидный | redirect `/dashboard/` (`homepage:dashboard`), `flash.success` в сессии |
| невалидный | рендер `FormRegistration`, props `form` с пустыми паролями |

## PasswordRecovery (запрос восстановления)

- Модалка: `PasswordRecovery` (`frontend/src/components/modals/PasswordRecovery.tsx`),
  открывается из `FormRegistration`.
- POST-эндпоинт: `POST /auth/restore-password/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | redirect `/auth/login/` (`users:login`), `flash.success` |
| невалидный | рендер `RestorePasswordRequest`, props `{"email": "...", "errors"}` |

## Восстановление пароля

- Форма: `RestorePassword`.
- POST-эндпоинт: `POST /auth/restore-password/<uidb64>/<token>/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | redirect `/auth/login/`, `flash.success` |
| невалидный | рендер `RestorePassword`, props `{"new_password1", "new_password2", "uid", "token", "errors"}` |
| неверный uid/token | redirect `/auth/login/`, `flash.error` |

## Обновление профиля

- Форма: `ProfileForm` (`features/userProfile`) внутри `Profile`
  (`/auth/profile/`).
- POST-эндпоинт: `POST /auth/profile/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | redirect `/auth/profile/`, `flash.success` |
| невалидный | рендер `Profile`, props базовых + `errors` + `values` |

## Смена аватара

- POST-эндпоинт: `POST /auth/<username>/avatar-change/`.
- Ответ без рендера: redirect `/auth/profile/` + `flash`.

## Создание группы

- POST-эндпоинт: `POST /group/create/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Channels`, props `{"flash": {"success": "Группа успешно создана"}, "group": {"name": ...}}` |
| невалидный | рендер `Profile`, props `{"form": {name, description, image_url}, "errors"}` |

## Редактирование группы

- POST-эндпоинт: `POST /group/<slug>/update/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Profile`, props `{"flash": {"success": "Группа успешно изменена"}}` |
| невалидный | рендер `Profile`, props `{"form": {name, description, image_url}, "errors"}` |

## Удаление группы

- POST-эндпоинт: `POST /group/<slug>/delete/`.
- Ответ: рендер `Profile`, props `{"flash": {"success": "Группа успешно удалена"}}`.

## Добавление каналов

- POST-эндпоинт: `POST /group/<slug>/add-channels/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `GroupDetail`, props `{"flash": {"success": "Каналы добавлены"}}` |
| невалидный | рендер `GroupDetail`, props `{"form": {"errors", "values"}}` |

## Модерация: approve / reject

- POST-эндпоинт: `POST /admin/moderation/` (поля `action`, `request_id`, см.
  [`moderation_contract.md`](./moderation_contract.md)).
- Ответ всегда redirect + `flash.success`/`flash.error`.

---

# Расхождения и чек-лист выравнивания

## Расхождения компонентных имён и URL

| Где | Реальность | Конвенция/предложение |
|-----|-----------|-----------------------|
| `apps/blog/dto/blog_dto.py` docstring | `BlogArticle` | `BlogPost` |
| `apps/users/views.py` `UserCabinetView` docstring | `UserProfilePage` | `Profile` |
| `PostDetailView` docstring | `/post/...` | фактический `/parser/post/...` |
| `GroupDetailView` docstring | старый набор ключей `get_data()` | сейчас + `cover`, `curator`, `channel_count`, `saves_count`, `views_count` |
| `UserRegister` рендерит `FormRegistration` | нет `pages/FormRegistration.tsx` | вынести регистрацию в `pages/Auth.tsx` либо создать страницу |

Резолвер и имена страниц приведены к конвенции в коммите
`3da2a9f feat: add glob resolver, remove react router` — расхождение
`Home`/`MassParsing`/`ComparePages` устранено.

## Чек-лист

1. ✅ Резолвер переведён на glob (`frontend/src/main.tsx`), страницы
   переименованы в канонические имена (`3da2a9f`) — выполнено.
2. Создать недостающие страницы `frontend/src/pages/<Name>.tsx` для
   `FormRegistration`, `GroupDetail`, `ChannelAnalytics`, `UpdateUserProfile`,
   `RestorePasswordRequest`, `RestorePassword`.
3. Заменить мок-пропсы (`Channels`, `Compare`, `AICabinet`, `Collection`) на
   реальные по планируемым формам выше — либо пометить их как готовые только
   после согласования контракта.
4. Закоммитить backend-маршруты из working tree (`config/urls.py`,
   `apps/ai/urls.py` и связанные views).
5. Обновить docstring-и, перечисленные в таблице расхождений.
6. Обновить таблицу состояний при изменении страниц/views.