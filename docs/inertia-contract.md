# Inertia-контракт

Единый источник правды о том, **что возвращает backend** и **что ожидает frontend**
для каждого Inertia-экрана и каждой модалки.

Документ описывает **целевое состояние после слияния задач**:

- [#194](https://github.com/hexlet-volunteers/tg-marketing-service/issues/194) —
  glob-резолвер `import.meta.glob("./pages/**/*.tsx")` и единая директория
  `frontend/src/pages/`;
- [#198](https://github.com/hexlet-volunteers/tg-marketing-service/issues/198) —
  Inertia-маршруты и канонические имена компонентов для всех 14 экранов.

> ⚠️ Ни одна ветка сейчас не содержит обе задачи одновременно. Пока #194 и #198
> не влиты в `main`, часть экранов резолвится только через SPA-роутер
> (`frontend/src/app/routes/routes.tsx`), а не через `inertia_render`.

Связанные документы:

- [`inertia-shared-props.md`](./inertia-shared-props.md) — контракт общих props;
- [`dto_convention.md`](./dto_convention.md) — конвенция DTO и хелпер рендера;
- [`moderation_contract.md`](./moderation_contract.md) — детальный контракт
  `/admin/moderation/`;
- [`collections_catalog_contract.md`](./collections_catalog_contract.md) —
  детальный контракт `/collections/`;
- [`registration_contract.md`](./registration_contract.md) — детальный контракт
  регистрации.

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
redirect.

`component` обязан совпадать с именем файла страницы
`frontend/src/pages/<Name>.tsx`, иначе клиент падает с
`Page <name> not found`.

## Общие props

Каждый ответ дополнительно содержит общие props `auth`, `role`, `is_admin`,
`csrfToken`, `flash`. Они формируются один раз в
`config.middleware.SharedInertiaPropsMiddleware` и **не переопределяются** во
views. Контракт — [`inertia-shared-props.md`](./inertia-shared-props.md).

В примерах ниже ключи `auth`, `role`, `is_admin`, `csrfToken`, `flash` не
дублируются: они подразумеваются в любом ответе.

## Резолвер и именование (#194)

Резолвер (`frontend/src/main.tsx`) построен на `import.meta.glob` и
поддерживает **любое** имя, для которого существует файл страницы:

```tsx
const pages = import.meta.glob("./pages/**/*.tsx");
// resolve(name) -> pages[`./pages/${name}.tsx`]
```

**Правило одного имени.** Строка `component` в `inertia_render` / DTO-view,
имя файла `frontend/src/pages/<Name>.tsx` и колонка `component` в этом
документе обязаны совпадать символ в символ.

Если файла `frontend/src/pages/<Name>.tsx` нет — клиент падает с
`Page <name> not found`. Поэтому контракт фиксирует не только строку
`component`, но и наличие соответствующего файла страницы.

### Состояние веток

- `issue/194` — уже содержит glob-резолвер и **канонические** имена страниц в
  `frontend/src/pages/`: `Landing`, `Post`, `Compare`, `AICabinet`, `Admin`,
  `Blog`, `BlogPost`, `Collection`, `Collections`, `Legal`, `NotFound`,
  `Profile`, `Auth`, `Channels`, `Dashboard`. Переименование старых имён
  (`Home`, `ComparePages`, `MassParsing`, `…Page`) выполнено там же (коммит
  `3da2a9f`), отдельная миграция имён не требуется.
- `issue/198` — backend отдаёт канонические `component` для всех 14 экранов.
- `main` — пока использует старые имена (`Home`, `UserProfilePage`,
  `AdminModeration`, `PostPage`, `BlogArticle`); они исчезнут после слияния
  #198.

Компоненты, которые backend отдаёт (#198), но страницы `pages/<Name>.tsx` ещё
нет, — для них нужен файл страницы (в рамках #194/#198):
`FormRegistration.tsx`, `GroupDetail.tsx`, `ChannelAnalytics.tsx`,
`UpdateUserProfile.tsx`, `RestorePasswordRequest.tsx`, `RestorePassword.tsx`.

## Состояние интеграции

Обозначения столбца `pages/<Name>.tsx`: `✅` — файл уже есть (#194);
`🆕` — файла нет. Обозначения столбца `props`: `✅` — реальные, `🔸` —
мок/пустые.

| Экран | `component` | URL | Django view | `pages/<Name>.tsx` | props |
|-------|-------------|-----|-------------|--------------------|-------|
| Landing | `Landing` | `/` | `IndexView` | ✅ `Landing.tsx` | ✅ |
| Channels | `Channels` | `/channels/` | `ChannelCatalogView` | ✅ `Channels.tsx` | 🔸 |
| Dashboard | `Dashboard` | `/dashboard/` | `DashboardView` | ✅ `Dashboard.tsx` | ✅ |
| Post | `Post` | `/post/`, `/parser/post/…` | `PostPageView`, `PostDetailView`, `PostAIAnalysisView` | ✅ `Post.tsx` | ✅/🔸 |
| Compare | `Compare` | `/compare/` | `CompareView` | ✅ `Compare.tsx` | 🔸 |
| AICabinet | `AICabinet` | `/ai-cabinet/` | `AICabinetView` | ✅ `AICabinet.tsx` | 🔸 |
| Collections | `Collections` | `/collections/` | `CollectionsCatalogView` | ✅ `Collections.tsx` | ✅ |
| Collection | `Collection` | `/collections/<pk>/` | `CollectionDetailView` | ✅ `Collection.tsx` | 🔸 |
| Profile | `Profile` | `/auth/profile/` | `UserCabinetView` | ✅ `Profile.tsx` | ✅ |
| Blog | `Blog` | `/blog/` | `BlogListView` | ✅ `Blog.tsx` | ✅ |
| BlogPost | `BlogPost` | `/blog/<slug>/` | `BlogArticleDetailView` | ✅ `BlogPost.tsx` | ✅ |
| Legal | `Legal` | `/legal/` | `LegalView` | ✅ `Legal.tsx` | ✅ |
| NotFound | `NotFound` | `/<path>/` | `NotFoundView` | ✅ `NotFound.tsx` | 🔸 |
| Admin | `Admin` | `/admin/moderation/` | `ModerationRequestListView` | ✅ `Admin.tsx` | ✅ |

Вспомогательные страницы, не входящие в 14 экранов, но используемые модалками
и групповыми формами:

| Компонент | URL | Django view | `pages/<Name>.tsx` | props |
|-----------|-----|-------------|--------------------|-------|
| `Auth` | `/auth/login/` | `LoginView` | ✅ `Auth.tsx` | ✅ |
| `FormRegistration` | `/auth/create/` | `UserRegister` | 🆕 `FormRegistration.tsx` | ✅ |
| `GroupDetail` | `/group/<slug>/` | `GroupDetailView`, `AddChannelsView` | 🆕 `GroupDetail.tsx` | ✅ |
| `ChannelAnalytics` | `/parser/list` | `ParserListView` | 🆕 `ChannelAnalytics.tsx` | ✅ |
| `UpdateUserProfile` | `/auth/<username>/update/` | `UserUpdate` | 🆕 `UpdateUserProfile.tsx` | ✅ |
| `RestorePasswordRequest` | `/auth/restore-password/` | `RestorePasswordRequestView` | 🆕 `RestorePasswordRequest.tsx` | ✅ |
| `RestorePassword` | `/auth/restore-password/<uidb64>/<token>/` | `RestorePasswordView` | 🆕 `RestorePassword.tsx` | ✅ |

`FormRegistration` сейчас существует только как компонент
`frontend/src/components/ui/FormRegistration.tsx`; для glob-резолвера нужен файл
страницы `frontend/src/pages/FormRegistration.tsx`, иначе невалидный POST
`/auth/create/` упадёт с `Page FormRegistration not found`.

`PasswordRecovery` — не самостоятельная страница, а модалка
(`frontend/src/components/modals/PasswordRecovery.tsx`), открывается из
`Auth`/`FormRegistration`.

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

| prop | тип | обяз. | источник |
|------|-----|-------|----------|
| `components` | `list[Component]` | да | активные (`is_active=True`), сортировка `order` |
| `components[].component` | `str` | да | `HomePageComponent.component_type` |
| `components[].props.id` | `int` | да | PK модели |
| `components[].props.title` | `str` | да | поле модели |
| `components[].props.order` | `int` | да | поле модели |
| `components[].props.*` | `Any` | нет | распаковка `content` |
| `components[].props.type` | `str` | да | `component_type` (дубль `component`) |
| `components[].url` | `str` | да | `request.path` (слот блока, не Inertia-компонент) |

Успешный логин (`LoginView.post`) также рендерит `Landing` с
`flash.success` и `user: {username}` — см. [модалку «Логин»](#логин).

## Channels — `/channels/`

Каталог каналов. Данные карточек пока **моковые** — на стороне frontend.

```json
{ "component": "Channels", "props": {}, "url": "/channels/" }
```

Планируемая форма (FE, `types/channel.ts`):

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

Этот же компонент отдаётся на успешное создание группы
(`POST /group/create/`, см. [«Создание группы»](#создание-группы)).

## Dashboard — `/dashboard/`

Защищённый экран: неавторизованные редиректятся на `/`.
Props описаны DTO `apps/homepage/dto/dashboard_dto.py` (`DashboardDTO`).

```json
{
  "component": "Dashboard",
  "props": {
    "stats": { "channels": 47, "posts": 2347, "ai_suggestions": 89, "days_left": 23 },
    "channels": [
      { "name": "Tech News RU", "subscribers": 45200, "posts": 24, "views": 156000, "engagement": 78.5, "growth": 12.3, "is_verified": false }
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

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `stats.channels` | `int` | да | |
| `stats.posts` | `int` | да | |
| `stats.ai_suggestions` | `int` | да | |
| `stats.days_left` | `int` | да | дней до конца подписки |
| `channels[].name` | `str` | да | первые 5 каналов |
| `channels[].subscribers` | `int` | да | `>= 0` |
| `channels[].posts` | `int` | да | `>= 0` |
| `channels[].views` | `int` | да | `>= 0` |
| `channels[].engagement` | `float` | да | `views / subscribers * 100`, `0..100` |
| `channels[].growth` | `float` | да | % роста |
| `channels[].is_verified` | `bool` | да | по умолчанию `false` |
| `ai_insights[].text` | `str` | да | до 5 непрочитанных |
| `ai_insights[].type` | `str` | да | |
| `ai_insights[].id` | `int \| null` | да | может быть `null` |
| `collections[].name` | `str` | да | |
| `collections[].channels_count` | `int` | да | |
| `collections[].slug` | `str` | да | |
| `collections[].description` | `str \| null` | да | |
| `collections[].is_auto` | `bool` | да | признак автоколлекции |
| `quick_actions` | `list[str]` | да | |

## Post — детальный разбор поста

Компонент `Post` отдают три маршрута:

| URL | View | props |
|-----|------|-------|
| `/parser/post/<channel_id>/<telegram_message_id>/` | `PostDetailView` | `post` + `channel` |
| `/parser/ai/channels/<channel_id>/posts/<post_id>/analysis` | `PostAIAnalysisView` | только `post` (`channel` = `null`) |
| `/post/` | `PostPageView` | **мок**, `props: {}` |

Props — DTO `apps/parser/dto/post_analysis_dto.py` (`PostPagePropsDTO`).

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
        "similar_posts": [],
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
      "language": null
    }
  },
  "url": "/parser/post/2/100500/"
}
```

Примечания:

- `post_analysis.status` — `"processing"` (анализ запущен фоном) или
  `"completed"`;
- `er` — engagement rate поста; `reactions` = `{total, details}`;
- `channel` — `dict | null`: на маршруте AI-анализа равен `null`;
- `csrfToken` — общий prop (см. [«Общие props»](#общие-props)), в props экрана
  `Post` не дублируется. `PostDetailView` пока передаёт его через
  `PostPagePropsDTO` — известное расхождение, см. ниже.

## Compare — `/compare/`

Сравнение каналов. **Мок** (данные на frontend).

```json
{ "component": "Compare", "props": {}, "url": "/compare/" }
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
{ "component": "AICabinet", "props": {}, "url": "/ai-cabinet/" }
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
Props описаны DTO `apps/group_channels/dto/collections_dto.py`
(`CollectionsCatalogDTO`).

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
    "collections": [],
    "sections": [
      { "title": "Технологии", "collections": [], "count": 0 }
    ],
    "filters": {
      "q": null,
      "country": null,
      "category": null,
      "country_options": [],
      "category_options": []
    }
  },
  "url": "/collections/"
}
```

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `featured` | `list[Collection]` | да | до 3 подборок |
| `collections` | `list[Collection]` | да | полный список |
| `sections` | `list[Section]` | да | группировка по категориям |
| `sections[].title` | `str` | да | |
| `sections[].collections` | `list[Collection]` | да | |
| `sections[].count` | `int` | да | `>= 0` |
| `filters.q` | `str \| null` | да | |
| `filters.country` | `str \| null` | да | |
| `filters.category` | `str \| null` | да | |
| `filters.country_options` | `list[str]` | да | |
| `filters.category_options` | `list[str]` | да | |

`Collection`: `id:int`, `name:str`, `slug:str`, `description:str|null`,
`is_editorial:bool`, `curator:str|null`, `channel_count:int`,
`cover:str`, `gradient_key:str` (формируется как `collection-<id>`).

## Collection — `/collections/<pk>/`

Детальная страница подборки. Содержимое **мок** (`CollectionDetailView`
рендерит без props, существование подборки не проверяется).

```json
{ "component": "Collection", "props": {}, "url": "/collections/1/" }
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
      "plan": "free",
      "period": "monthly",
      "price": "0.00",
      "current_period_end": null,
      "limits": { "channels": 3, "ai_requests": 10 },
      "days_left": 0,
      "channels_used": 0,
      "ai_requests_used": 0
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

| prop | тип | обяз. | источник |
|------|-----|-------|----------|
| `user` | `User` | да | поля модели `User` |
| `subscription` | `SubscriptionStateDTO` | да | `serialize_subscription(get_subscription(user))` |
| `notifications` | `null` | да | пока всегда `null` |
| `usage_stats` | `UsageStats` | да | вычисляется из `date_joined` / `last_login` |
| `user_role` | `str` | да | `request.role` |

`SubscriptionStateDTO` (`apps/billing/dto/subscription_dto.py`):
`plan:str`, `period:str`, `price:Decimal`, `current_period_end:datetime|null`,
`limits:{channels:int, ai_requests:int}`, `days_left:int`,
`channels_used:int`, `ai_requests_used:int`.

Примечания:

- подписка — реальная (лениво создаётся Free через `get_subscription`), не
  захардкожена;
- `POST` валидный — redirect на `/auth/profile/`, изменения отдаются только
  после перезагрузки;
- `POST` невалидный — повторный рендер `Profile` c `errors` и `values`
  (`first_name`, `last_name`, `email`, `bio`, `avatar_image`);
- `user_role` в props и `user.role` повторяют общий prop `role` — известное
  расхождение, см. [«Известные расхождения»](#известные-расхождения).

## Blog — `/blog/`

Публичный список статей. Props — `BlogListDTO`
(`apps/blog/dto/blog_dto.py`).

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

- только `is_published=True`;
- `featured` — последняя `is_featured=True`, может быть `null`;
- `articles` — остальные, `published_at desc`.

`ArticleCardDTO`: `id:int`, `slug:str`, `title:str`, `excerpt:str`,
`cover_image:str`, `category:str`, `tags:list[str]`, `read_time:int`,
`published_at:datetime|null`, `views_count:int`, `author_name:str|null`.

## BlogPost — `/blog/<slug>/`

Публичная детальная страница статьи. Props — `ArticleDetailDTO`.

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

- `body` — Markdown, HTML собирает frontend;
- `cta` — дескриптор CTA-кнопки (`{label:str, url:str}`);
- `related` — не более 3 статей (`ArticleCardDTO`);
- `views_count` растёт только при полной загрузке (не Inertia-навигации);
- неопубликованная/отсутствующая статья — 404.

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

## NotFound — `/<path>/`

Catch-all для несопоставленных URL. Ответ всегда имеет статус 404.

```json
{
  "component": "NotFound",
  "props": {},
  "url": "/no-such-page/"
}
```

```python
response = inertia_render(request, "NotFound")
response.status_code = 404
```

Catch-all регистрируется только для URL с завершающим слэшем
(`<path:missing>/`), чтобы работал `APPEND_SLASH`-редирект.

## Admin — `/admin/moderation/`

Модерация заявок. Только для администраторов (`AdminRequiredMixin`).
Детальный контракт — [`moderation_contract.md`](./moderation_contract.md).
Props — `ModerationDTO` (`apps/admin/moderation/dto/moderation_dto.py`).

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
- `pendingCount` — общее число `pending`-заявок, не размер страницы;
- `submitted_by` и `channel` могут быть `null`.

## ChannelAnalytics — `/parser/list`

Список публичных каналов. Props — `ChannelListDTO`
(`apps/parser/dto/channel_dto.py`).

```json
{
  "component": "ChannelAnalytics",
  "props": {
    "channels": [
      {
        "id": 1,
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
      }
    ]
  },
  "url": "/parser/list"
}
```

`ChannelDTO`: `username`/`description`/`parsed_at`/`creation_date`/`category`/
`country`/`language` — nullable; `pinned_messages:[{text:str, id:int|null}]`;
`last_messages:[{post_id:int, post_text:str|null, post_views:int|null}]`.

## GroupDetail — `/group/<slug>/`

Детальная страница группы; используется групповыми формами. Защищённый экран.

```json
{
  "component": "GroupDetail",
  "props": {
    "group": {
      "id": 1,
      "name": "Название",
      "slug": "nazvanie",
      "description": "...",
      "owner": "ivan",
      "is_editorial": false,
      "order": 1,
      "image_url": "https://...",
      "created_at": "2026-08-13T10:00:00+00:00"
    },
    "channels": [],
    "auto_category": null,
    "add_form": null,
    "is_owner": true
  },
  "url": "/group/nazvanie/"
}
```

- `auto_category` — `str | null`, заполняется для автоколлекций;
- `add_form` — форма (только владельцу и только для ручной группы), иначе
  `null`;
- `is_owner` — признак владельца.

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

- Модалка/форма: `Auth`.
- POST-эндпоинт: `POST /auth/login/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Landing`, общий `flash.success` + `user: {username}` |
| невалидный | рендер `Auth`, props `{"form": {"data": {email, password:""}, "errors"}}` |

## Регистрация

- Модалка/форма: `FormRegistration` (встроена в `Auth`).
- POST-эндпоинт: `POST /auth/create/`.
- Детали — [`registration_contract.md`](./registration_contract.md).

| Сценарий | Ответ |
|----------|-------|
| валидный | redirect `/dashboard/` (`homepage:dashboard`), `flash.success` в сессии |
| невалидный | рендер `FormRegistration`, props `form` с пустыми паролями |

## PasswordRecovery (запрос восстановления)

- Модалка: `PasswordRecovery` (`frontend/src/components/modals/PasswordRecovery.tsx`),
  открывается из `FormRegistration`.
- POST-эндпоинт: `POST /auth/restore-password/`.
- Тип props: `{email: str, errors?: dict}`; GET — `{email: ""}`.

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

Отдельная форма `UpdateUserProfile` (`/auth/<username>/update/`) отдаёт
`{"form": {first_name, last_name, username, password1, password2, email, bio,
avatar_image}, "errors": {}}`.

## Смена аватара

- POST-эндпоинт: `POST /auth/<username>/avatar-change/`.
- Ответ без рендера: redirect `/auth/profile/` + `flash`.

## Создание группы

- POST-эндпоинт: `POST /group/create/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Channels`, общий `flash.success` + `group: {name}` |
| невалидный | рендер `Profile`, props `{"form": {name, description, image_url}, "errors"}` |

## Редактирование группы

- POST-эндпоинт: `POST /group/<slug>/update/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `Profile`, общий `flash.success` |
| невалидный | рендер `Profile`, props `{"form": {name, description, image_url}, "errors"}` |

## Удаление группы

- POST-эндпоинт: `POST /group/<slug>/delete/`.
- Ответ: рендер `Profile`, общий `flash.success`.

## Добавление каналов

- POST-эндпоинт: `POST /group/<slug>/add-channels/`.

| Сценарий | Ответ |
|----------|-------|
| валидный | рендер `GroupDetail`, общий `flash.success` |
| невалидный | рендер `GroupDetail`, props `{"form": {"errors", "values"}}` |

## Модерация: approve / reject

- POST-эндпоинт: `POST /admin/moderation/` (поля `action`, `request_id`, см.
  [`moderation_contract.md`](./moderation_contract.md)).
- Ответ всегда redirect + `flash.success`/`flash.error`.

---

# Правило DTO

Props каждого экрана описываются Pydantic-DTO, а не словарями. Конвенция —
[`dto_convention.md`](./dto_convention.md), хелпер —
`config.renderers.render_inertia_from_dto(request, component, props=dto)`.

- DTO размещаются в `apps/<app>/dto/`;
- view сериализует DTO через `model_dump(mode="json")` (делает хелпер);
- ORM-модели и сырые `dict` в props не передаются.

Эталонный пример — `ParserListView` (`ChannelAnalytics` → `ChannelListDTO`).

Экраны на DTO: `Dashboard` (`DashboardDTO`), `Collections`
(`CollectionsCatalogDTO`), `ChannelAnalytics` (`ChannelListDTO`), `Post`
(`PostPagePropsDTO`), `Blog` (`BlogListDTO`), `BlogPost`
(`ArticleDetailDTO`), `Admin` (`ModerationDTO`).

Ещё собирают props словарями (кандидаты на перевод на DTO в рамках #197):
`apps/users/views.py` (`LoginView`, `UserRegister`, `UserCabinetView`,
`UserUpdate`, `RestorePassword*`), `apps/group_channels/views.py`
(`GroupDetailView`, групповые формы), `apps/legal/views.py`,
`config/views.py` (`IndexView`), `apps/homepage/views.py`
(`DashboardView` вызывает `dto.model_dump` напрямую, а не через хелпер).

---

# Расхождения и чек-лист выравнивания

## Известные расхождения

| Где | Реальность | Конвенция |
|-----|-----------|-----------|
| `apps/users/views.py` `UserCabinetView` docstring | `component: UserProfilePage` | `Profile` (устраняется #198) |
| `apps/blog/dto/blog_dto.py` docstring | `BlogArticle` | `BlogPost` (устраняется #198) |
| `apps/parser/views.py` `PostDetailView` docstring | `/post/...` | `/parser/post/...` |
| `apps/group_channels/views.py` `GroupDetailView` docstring | старый набор ключей `get_data()` | текущий набор |
| `apps/parser/views.py` `PostDetailView` | дублирует общий prop `csrfToken` в `PostPagePropsDTO` | брать из общего middleware (`inertia-shared-props.md`) |
| `apps/users/views.py` `UserCabinetView` | props `user_role` и `user.role` повторяют общий `role` | брать `role` из общего middleware |
| `main` | старые `component` (`Home`, `UserProfilePage`, `AdminModeration`, `PostPage`, `BlogArticle`) | канонические имена #198 |

## Чек-лист

1. Дождаться слияния #194 (glob-резолвер + канонические страницы) и #198
   (канонические `component` в backend).
2. Создать отсутствующие страницы `FormRegistration.tsx`, `GroupDetail.tsx`,
   `ChannelAnalytics.tsx`, `UpdateUserProfile.tsx`,
   `RestorePasswordRequest.tsx`, `RestorePassword.tsx`.
3. Убрать дублирование общих props: `csrfToken` из `PostPagePropsDTO` /
   `PostDetailView`, `role` из `UserCabinetView` (`user_role`, `user.role`).
4. Заменить мок-пропсы (`Channels`, `Compare`, `AICabinet`, `Collection`,
   `NotFound`) на реальные по планируемым формам — либо оставить мок
   согласованно.
5. Перевести словарные view на DTO из `dto_convention.md` (#197).
6. Обновить docstring-и из таблицы расхождений.
7. Обновлять контракт при каждом изменении формы props, маршрута или
   имени компонента.

## Согласование

Критерий приёмки — документ просмотрен одним frontend- и одним
backend-разработчиком. Отметки о ревью:

| Роль | Статус | Ревьюер |
|------|--------|---------|
| Frontend | ⏳ ожидает | — |
| Backend | ⏳ ожидает | — |
