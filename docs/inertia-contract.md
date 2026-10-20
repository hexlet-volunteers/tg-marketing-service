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
`🆕` — файла нет. Обозначения столбца `props`: `✅` — реальные и совпадают с
FE, `✅ мок BE` — контракт совпадает с FE, но данные моковые и отдаются
бэкендом из реестров `apps/*/mock_data.py`, `🔸` — мок/пустые,
`⚠️` — backend и frontend используют **разные наборы
props** (целевая структура — FE, см. раздел экрана).

| Экран | `component` | URL | Django view | `pages/<Name>.tsx` | props |
|-------|-------------|-----|-------------|--------------------|-------|
| Landing | `Landing` | `/` | `IndexView` | ✅ `Landing.tsx` | ✅ |
| Channels | `Channels` | `/channels/` | `ChannelCatalogView` | ✅ `Channels.tsx` | ✅ мок BE |
| Dashboard | `Dashboard` | `/dashboard/` | `DashboardView` | ✅ `Dashboard.tsx` | ⚠️ BE≠FE |
| Post | `Post` | `/post/`, `/parser/post/…` | `PostPageView`, `PostDetailView`, `PostAIAnalysisView` | ✅ `Post.tsx` | ⚠️ BE≠FE |
| Compare | `Compare` | `/compare/` | `CompareView` | ✅ `Compare.tsx` | ✅ мок BE |
| AICabinet | `AICabinet` | `/ai-cabinet/` | `AICabinetView` | ✅ `AICabinet.tsx` | ✅ мок BE |
| Collections | `Collections` | `/collections/` | `CollectionsCatalogView` | ✅ `Collections.tsx` | ✅ |
| Collection | `Collection` | `/collections/<pk>/` | `CollectionDetailView` | ✅ `Collection.tsx` | ✅ мок BE |
| Profile | `Profile` | `/auth/profile/` | `UserCabinetView` | ✅ `Profile.tsx` | ✅ |
| Blog | `Blog` | `/blog/` | `BlogListView` | ✅ `Blog.tsx` | ✅ |
| BlogPost | `BlogPost` | `/blog/<slug>/` | `BlogArticleDetailView` | ✅ `BlogPost.tsx` | ✅ |
| Legal | `Legal` | `/legal/` | `LegalView` | ✅ `Legal.tsx` | ✅ |
| NotFound | `NotFound` | `/<path>/` | `NotFoundView` | ✅ `NotFound.tsx` | 🔸 |
| Admin | `Admin` | `/admin/moderation/` | `ModerationRequestListView` | ✅ `Admin.tsx` | ⚠️ BE≠FE |

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
    ],
    "tariffs": [
      {
        "id": 1,
        "name": "Free",
        "description": "Для тех, кто начинает изучать Telegram-аналитику",
        "price": "0 ₽",
        "period": "навсегда",
        "monthlyPrice": 0,
        "features": [{ "id": 1, "text": "Базовая статистика" }],
        "button": { "label": "Начать бесплатно", "variant": "default" }
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
| `tariffs` | `list[Tariff]` | да | `MOCK_TARIFFS` (`apps/homepage/mock_data.py`); рендерит `TariffsBlock` |

`TariffsBlock` (тип `Tariff` — `frontend/src/widgets/TariffsBlock/model/types.ts`)
получает тарифы через проп. Прочие блоки лендинга (шаги, FAQ, AI-демо)
отдаются через `components[]` (БД пока пуста).

Успешный логин (`LoginView.post`) также рендерит `Landing` с
`flash.success` и `user: {username}` — см. [модалку «Логин»](#логин).

## Channels — `/channels/`

Каталог каналов. Мок-данные карточек отдаются бэкендом из реестра
`apps/parser/mock_data.py` (`MOCK_CHANNELS`); до подключения БД фронтенд
не рендерит своих моков.

```json
{
  "component": "Channels",
  "props": {
    "channels": [
      {
        "id": 1,
        "name": "Tech News RU",
        "username": "@technewsru",
        "type": "channel",
        "subscribers": 125000,
        "category": "Технологии",
        "verified": true,
        "country": "Россия",
        "imageUrl": "",
        "er": 8.3,
        "growth30d": 3.2
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

Props страницы отдаются бэкендом в двух частях:

1. реальный `DashboardDTO` (`stats`/`channels`/`ai_insights`/`collections`/
   `quick_actions`) — из `DashboardService`;
2. FE-структура страницы из мок-реестра
   `apps/homepage/mock_data.py` — `channel`/`kpis`/`growthData`/`posts`
   (перенесены сюда из бывших `frontend/src/shared/mocks/`:
   `channelKpis`, `channelsCollection`, `posts`). До подключения БД фронтенд
   не рендерит своих моков.

### Целевые props (FE)

Типы — `frontend/src/types/dashboard.ts` (`DashboardPageProps`),
`frontend/src/types/channel.ts` (`Channel`, `Kpi`,
`GrowthSubscribersData`), `frontend/src/types/post.ts` (`Post`).

```json
{
  "component": "Dashboard",
  "props": {
    "channel": {
      "id": 1, "name": "Tech News RU", "username": "@technewsru",
      "type": "channel", "subscribers": 125000, "category": "Технологии",
      "verified": true, "country": "Россия", "imageUrl": "", "er": 8.3,
      "growth30d": 3.2
    },
    "kpis": [
      { "label": "Посты", "value": 2347, "delta": 120, "percentDelta": 5.4, "positive": true }
    ],
    "growthData": [
      { "date": "2026-09-01", "подписчики": 45200 }
    ],
    "posts": [
      { "title": "Заголовок поста", "views": 15200, "reactions": 120, "forwards": 340, "er": 3.4 }
    ],
    "ai_insights": [
      { "text": "Тренд: посты о новых ИИ инструментах набирают +45% просмотров", "type": "trend", "id": 1 }
    ]
  },
  "url": "/dashboard/"
}
```

| prop | тип | обяз. | источник |
|------|-----|-------|----------|
| `channel` | `Channel` | да | `MOCK_CHANNEL` (`apps/homepage/mock_data.py`) |
| `kpis[]` | `Kpi[]` | да | `MOCK_KPIS` (`apps/homepage/mock_data.py`) |
| `kpis[].label` | `str` | да | подпись KPI |
| `kpis[].value` | `int` | да | |
| `kpis[].delta` | `int` | нет | абсолютный прирост |
| `kpis[].percentDelta` | `int` | нет | % прироста |
| `kpis[].positive` | `bool` | да | направление дельты |
| `growthData[]` | `GrowthSubscribersData[]` | да | `MOCK_GROWTH_DATA`; временной ряд `{date, подписчики}` |
| `posts[]` | `Post[]` | да | `MOCK_POSTS`; топ постов |
| `posts[].title` | `str` | да | |
| `posts[].views` | `int` | да | |
| `posts[].reactions` | `int` | да | сумма реакций |
| `posts[].forwards` | `int` | да | |
| `posts[].er` | `float` | да | engagement rate |
| `ai_insights[]` | `Insight[]` | да | до 5 непрочитанных из БД или сгенерированных fallback (`DashboardService`) |

### Текущий backend

Помимо FE-структуры выше отдаётся реальный `DashboardDTO`
(`apps/homepage/dto/dashboard_dto.py`), сериализуется через
`model_dump(mode="json")` в `apps/homepage/views.py`. Эта часть FE пока
**не потребляется** и сохранена для будущего подключения БД.

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

### Маппинг BE → целевую структуру

| Целевой prop (FE) | Источник (BE) | Статус |
|-------------------|---------------|--------|
| `channel` | `MOCK_CHANNEL` | перенесён с FE-мока `channelsCollection[0]` |
| `kpis[]`, `growthData[]`, `posts[]` | `MOCK_KPIS`, `MOCK_GROWTH_DATA`, `MOCK_POSTS` | перенесены с FE-моков в реестр |
| `ai_insights[]` | `AIInsight` / fallback `DashboardService` | FE рендерит карточки из этих данных |
| — | `stats`, `channels`, `collections`, `quick_actions` | передаётся BE, **FE не потребляет** (сохранено для БД) |


## Post — детальный разбор поста

Компонент `Post` отдают три маршрута:

| URL | View | props |
|-----|------|-------|
| `/parser/post/<channel_id>/<telegram_message_id>/` | `PostDetailView` | `post` + `channel` |
| `/parser/ai/channels/<channel_id>/posts/<post_id>/analysis` | `PostAIAnalysisView` | только `post` (`channel` = `null`) |
| `/post/` | `PostPageView` | **мок** `analysis` + `reactions` из `apps/parser/mock_data.py` |

⚠️ **Расхождение BE/FE.** Backend отправляет `post`/`channel` (DTO
`apps/parser/dto/post_analysis_dto.py`, `PostPagePropsDTO`), а страница
`pages/Post.tsx` (`PostPageProps` из
`frontend/src/types/post.ts`) потребляет только `analysis` и `reactions`;
сам `post`/`channel` FE **не использует** (текст и метрики поста
захардкожены в JSX). Мок-демо `/post/` отдаёт `analysis`/`reactions`
с бэкенда; на реальных маршрутах FE при отсутствии этих props показывает
пустые списки. **Целевая структура — FE** (ниже).

### Целевые props (FE)

Типы — `frontend/src/types/post.ts` (`PostAnalysis`, `PostReaction`,
`PostPageProps`).

```json
{
  "component": "Post",
  "props": {
    "analysis": {
      "status": "completed",
      "why_worked": ["Причина успеха"],
      "how_to_improve": ["Как улучшить"],
      "similar_posts": [
        {
          "id": 2,
          "telegram_message_id": 100499,
          "text": "Текст похожего поста",
          "published_at": "2026-08-30T10:00:00+00:00",
          "views": 9800,
          "forwards": 210,
          "comments_count": 12,
          "permalink": "https://t.me/example/100499"
        }
      ],
      "model_version": "claude-3-5"
    },
    "reactions": [
      { "emoji": "🔥", "label": "Огонь", "percent": 40, "count": 48 }
    ]
  },
  "url": "/parser/post/2/100500/"
}
```

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `analysis` | `PostAnalysis \| null` | нет | top-level; статус `processing`/`completed`; FE стартует с `null` («Анализ не проведен») |
| `analysis.why_worked` | `list[str]` | да | |
| `analysis.how_to_improve` | `list[str]` | да | |
| `analysis.similar_posts[]` | `list[SimilarPost]` | да | |
| `analysis.model_version` | `str \| null` | да | |
| `reactions` | `list[PostReaction]` | нет | плоский список, FE-форма |
| `reactions[].emoji` | `str` | да | `🔥 ❤️ 👍 🤯` |
| `reactions[].label` | `str` | да | `Огонь/Сердце/Лайк/Восторг` |
| `reactions[].percent` | `float` | да | доля реакции |
| `reactions[].count` | `int` | да | абсолютное число |

### Текущий backend

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

### Маппинг BE → целевую структуру

| Целевой prop (FE) | Источник (BE) | Статус |
|-------------------|---------------|--------|
| `analysis` | `post.post_analysis` | поднять с top-level `post` на top-level props |
| `analysis.similar_posts[]` | `post.post_analysis.similar_posts` | формы совпадают (`{id, telegram_message_id, text, published_at, views, forwards, comments_count, permalink}`) |
| `reactions[]` | `post.reactions.details` | **формы различаются**: BE `{total, details: {emoji: count}}` vs FE `[{emoji, label, percent, count}]`; `label` — таблица соответствий на FE/BE |
| — | `post` (без `post_analysis`) | передаётся BE, **FE не потребляет** (контент поста захардкожен) |
| — | `channel` | передаётся BE, **FE не потребляет** |
| — | `csrfToken` в `PostPagePropsDTO` | дубль общего middleware, убрать (см. [«Известные расхождения»](#известные-расхождения)) |

## Compare — `/compare/`

Сравнение каналов. Мок-данные отдаются бэкендом из реестра
`apps/parser/mock_data.py` (`MOCK_COMPARE_METRICS`, первые 3 канала из
`MOCK_CHANNELS`); форматирование значений метрик и вычисление
`avgReach`/`reachPerSub` остаются на фронтенде.

```json
{
  "component": "Compare",
  "props": {
    "metrics": [
      { "key": "subscribers", "label": "Подписчики" },
      { "key": "er", "label": "ER" },
      { "key": "growth30d", "label": "Прирост 30д" },
      { "key": "avgReach", "label": "Средний охват" },
      { "key": "reachPerSub", "label": "Охват/подписчик" }
    ],
    "channels": []
  },
  "url": "/compare/"
}
```

## AICabinet — `/ai-cabinet/`

AI-кабинет автора. Мок-данные отдаются бэкендом из реестра
`apps/ai/mock_data.py`; иконки/цвета инсайтов FE выводит по полю `type`
(`frontend/src/utils/makeIdeasAndInsights.ts`).

```json
{
  "component": "AICabinet",
  "props": {
    "ideas": [
      {
        "title": "Обзор новых функций Telegram",
        "reason": "Актуальная тема, растущий интерес",
        "scope": 48222,
        "date": "чт 19:30"
      }
    ],
    "insights": [
      { "type": "recommendation", "text": "Публикуйте посты в среду в 19:00 — пик активности" }
    ],
    "competitors": [{ "name": "@techreview", "er": 9.2, "delta": 1.1 }],
    "heatMapData": { "Ср": { "19": 10 } }
  },
  "url": "/ai-cabinet/"
}
```

## Collections — `/collections/`

Публичный каталог подборок. Детальный контракт —
[`collections_catalog_contract.md`](./collections_catalog_contract.md).
Props описаны DTO `apps/group_channels/dto/collections_dto.py`
(`CollectionsCatalogDTO`).

До подключения БД данные отдаются из мок-реестра
`apps/group_channels/mock_data.py` (`build_mock_catalog`) с применением
фильтров `q`/`country`/`category` на стороне бэкенда; реальная выборка из
`Group` сохранена в `CollectionsCatalogService` и используется при
подключении БД.

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

Фронтенд (`pages/Collections.tsx`) потребляет `collections` и маппит
поля под карточку: `name→title`, `curator→author`, `channel_count→channels`,
`is_editorial→editorial`; цвет/градант карточки выводится по индексу
из локальной палитры (не зависит от `gradient_key`).

## Collection — `/collections/<pk>/`

Детальная страница подборки. Мок-данные отдаются бэкендом из реестра
`apps/group_channels/mock_data.py` (существование подборки с данным pk
не проверяется).

```json
{
  "component": "Collection",
  "props": {
    "title": "Топ IT-каналов",
    "description": "Технологии, разработка и цифровые продукты",
    "channel_count": 3,
    "channels": [
      {
        "name": "Product Radar",
        "username": "@product_radar",
        "subscribers": 142000,
        "er": 26.9,
        "growth30d": 2480,
        "color": "var(--mantine-color-tgblue-5)"
      }
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
    "notifications": {
      "weekly_reports": true,
      "trend_notifications": true,
      "limit_exceeded": false,
      "new_features": true
    },
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
| `notifications` | `UserNotificationSettings` | да | `NotificationSettings` (`get_or_create` для юзера) |
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
- настройки уведомлений: `POST` c `action=notifications`
  (`weekly_reports`, `trend_notifications`, `new_features` строками
  `'true'`/`'false'`) → `NotificationSettingsForm` → redirect; тело
  **form-data**, не JSON (Inertia: `forceFormData: true`); `limit_exceeded`
  — служебный, всегда `false`, в форме не участвует, переключатель
  заблокирован;
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

- контент всегда моковый (реестр `apps/blog/mock_data.py`), БД
  не используется (DB-логика оставлена в вьюхе/сервисе для
  prod-переключения позже);
- `featured` — статья с `is_featured=True` (всегда заполнена);
- `articles` — остальные моковые статьи, `published_at desc`.

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

- контент всегда моковый (реестр `apps/blog/mock_data.py`), страница
  рендерится всегда (200); slug вне реестра — featured-демо с
  подставленным `slug`;
- DB-логика оставлена в вьюхе/сервисе для prod-переключения позже
  (там отсутствующая/неопубликованная статья — 404, `views_count`
  растёт только при полной загрузке);
- `body` — Markdown, HTML собирает frontend;
- `cta` — дескриптор CTA-кнопки (`{label:str, url:str}`);
- `related` — не более 3 других статей (`ArticleCardDTO`).

## Legal — `/legal/`

Публичная страница правовых документов. Отдаёт метаданные и текст
документов (`apps/legal/documents.py`, `LEGAL_DOCUMENTS`).

```json
{
  "component": "Legal",
  "props": {
    "documents": {
      "privacy": {
        "title": "Политика конфиденциальности",
        "updated_at": "2026-07-01",
        "text": "Мы собираем и обрабатываем персональные данные…"
      },
      "agreement": {
        "title": "Пользовательское соглашение",
        "updated_at": "2026-07-01",
        "text": "Используя сервис TG Pulse, вы соглашаетесь…"
      },
      "offer": {
        "title": "Публичная оферта",
        "updated_at": "2026-07-01",
        "text": "Настоящая оферта адресована…"
      }
    }
  },
  "url": "/legal/"
}
```

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `documents` | `Record<slug, {title, updated_at, text}>` | да | `slug` — ключ вкладки на FE (`privacy`/`agreement`/`offer`) |
| `documents[].title` | `str` | да | заголовок документа |
| `documents[].text` | `str` | да | тело документа |
| `documents[].updated_at` | `str` | да | дата обновления (FE пока не рендерит) |

Тип на FE — `frontend/src/types/legal.ts` (`LegalPageProps`).
Вкладка «Соглашение» использует ключ `agreement` (ранее мок использовал
`terms`).

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

Backend отдаёт как реальные данные очереди (`pendingRequests`/
`pendingCount`/`pagination`), так и FE-структуру строк таблицы
`userRequests` (`ModerationListService` маппит очередь). Страница
`pages/Admin.tsx` потребляет `userRequests` (цвет аватара дорисовывается на
клиенте — `addColorsToUsersRequests`) и `pendingCount` (бейдж вкладки).

### Целевые props (FE)

Типы — `frontend/src/types/user.ts` (`UserRequest`, `UserRequestWithColors`,
`UserRequestProps`).

```json
{
  "component": "Admin",
  "props": {
    "userRequests": [
      {
        "title": "Example channel",
        "username": "user",
        "author": "user",
        "time": "13.08.2026",
        "category": "technology"
      }
    ],
    "pendingCount": 15
  },
  "url": "/admin/moderation/?page=1"
}
```

| prop | тип | обяз. | примечание |
|------|-----|-------|------------|
| `userRequests[]` | `UserRequest[]` | да | строки таблицы модерации (без `color`) |
| `userRequests[].title` | `str` | да | название канала или `channel_identifier` |
| `userRequests[].username` | `str` | да | username заявителя (`""` при отсутствии) |
| `userRequests[].author` | `str` | да | совпадает с `username` |
| `userRequests[].time` | `str` | да | дата подачи `%d.%m.%Y` |
| `userRequests[].category` | `str` | да | |
| `pendingCount` | `int` | да | общее число `pending`-заявок; используется бейджем вкладки |
| `userRequests[].color` | `str` | да | цвет аватара; **вычисляется на клиенте** (`addColorsToUsersRequests`), из BE не приходит |

### Текущий backend

Детальный контракт — [`moderation_contract.md`](./moderation_contract.md).
Props — `ModerationDTO`.

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
    },
    "userRequests": [
      {
        "title": "Example channel",
        "username": "user",
        "author": "user",
        "time": "13.08.2026",
        "category": "technology"
      }
    ]
  },
  "url": "/admin/moderation/?page=1"
}
```

Примечания:

- `GET` поддерживает query-параметр `page` (по умолчанию 1, размер 10);
- `pendingCount` — общее число `pending`-заявок, не размер страницы;
- `submitted_by` и `channel` могут быть `null`.

### Маппинг BE → целевую структуру

Маппинг выполняется на бэкенде в
`ModerationQueue.get_user_request_data` (`apps/admin/moderation/services/queue.py`).

| Целевой prop (FE) | Источник (BE) | Статус |
|-------------------|---------------|--------|
| `userRequests[].title` | `pendingRequests[].channel.title`, фолбэк `channel_identifier` | реализовано на BE |
| `userRequests[].username` | `pendingRequests[].submitted_by.username`, фолбэк `""` | реализовано на BE |
| `userRequests[].author` | `pendingRequests[].submitted_by.username` | совпадает с `username` |
| `userRequests[].time` | `pendingRequests[].created_at` | формат `%d.%m.%Y` |
| `userRequests[].category` | `pendingRequests[].category` | совпадает |
| `userRequests[].color` | — | **вычисляется на клиенте** (`addColorsToUsersRequests`) |
| `pendingCount` | `pendingCount` | FE использует для бейджа вкладки |
| — | `pendingRequests`, `pagination` | передаётся BE, **FE не потребляет** (для пагинации FE-тип придётся расширить) |

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

## Формат ошибок валидации

Форма элемента ошибок едина для всех форм:

```json
{
  "form": {
    "data": { "<field>": "<value>", "password1": "", "password2": "" },
    "errors": { "<field>": [{ "message": "Текст ошибки", "code": "invalid" }] }
  }
}
```

Backend получает её через `form.errors.get_json_data()` (Django-формы);
сырой `form.errors` (списки строк) в Inertia-props не передаётся.

⚠️ **Placement разный** — контракт фиксирует его как есть, нормализация
планируется вместе с переводом view на DTO (#197):

| Форма | Где лежат ошибки | Структура `form` |
|-------|------------------|------------------|
| Логин, Регистрация | `form.errors` | `{data, errors}` |
| Profile (`UserCabinetView`) | top-level `errors` (+ `values`) | `form` — плоские данные |
| `UpdateUserProfile` | top-level `errors` | `form` — плоские данные |
| `RestorePasswordRequest` | top-level `errors` (рядом с `email`) | нет `form` |
| `RestorePassword` | top-level `errors` (+ `new_password1/2`, `uid`, `token`) | нет `form`; пароли эхом в top-level props |
| Группы (create/update) | top-level `errors` | `form` — плоские данные |
| Добавление каналов | `form.errors` (+ `form.values`) | `{errors, values}` |

Пароли после невалидного POST в `form.data` всегда пустые
(исключение — `RestorePassword`: пароли в top-level props, см. таблицу).

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
(`ArticleDetailDTO`), `Admin` (`ModerationDTO`), `Channels`
(`ChannelsCatalogDTO`), `Compare` (`CompareDTO`), `AICabinet`
(`AICabinetDTO`), `Collection` (`CollectionDetailDTO`).

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
| `DashboardView` / `DashboardDTO` vs `pages/Dashboard.tsx` | BE отдаёт реальный `DashboardDTO` **и** FE-структуру `channel`/`kpis`/`growthData`/`posts` из `apps/homepage/mock_data.py`; FE потребляет вторую, первая сохранена для БД | FE-структура перенесена на BE — см. [Dashboard](#dashboard--dashboard) |
| `PostPagePropsDTO` vs `pages/Post.tsx` | BE: `post`/`channel`; FE: `analysis`/`reactions`; формы `reactions` различаются (`{total, details}` vs список) | целевая — FE; поднять `post_analysis` в top-level `analysis` — см. [Post](#post--детальный-разбор-поста) |
| `ModerationDTO` vs `pages/Admin.tsx` | BE отдаёт `pendingRequests`/`pendingCount`/`pagination` и готовую FE-структуру `userRequests`; `color` — только на клиенте | маппинг выполняется на BE (`ModerationQueue.get_user_request_data`) — см. [Admin](#admin--adminmoderation) |
| `main` | старые `component` (`Home`, `UserProfilePage`, `AdminModeration`, `PostPage`, `BlogArticle`) | канонические имена #198 |
| placement `errors` у форм | top-level `errors` (Profile, UpdateUserProfile, RestorePassword×2, группы create/update) vs `form.errors` (логин, регистрация, добавление каналов) | единая форма элемента `[{message, code}]` уже обеспечена `get_json_data()`; нормализация placement — при переводе view на DTO (#197), см. [«Формат ошибок валидации»](#формат-ошибок-валидации) |

## Чек-лист

1. Дождаться слияния #194 (glob-резолвер + канонические страницы) и #198
   (канонические `component` в backend).
2. Создать отсутствующие страницы `FormRegistration.tsx`, `GroupDetail.tsx`,
   `ChannelAnalytics.tsx`, `UpdateUserProfile.tsx`,
   `RestorePasswordRequest.tsx`, `RestorePassword.tsx`.
3. Убрать дублирование общих props: `csrfToken` из `PostPagePropsDTO` /
   `PostDetailView`, `role` из `UserCabinetView` (`user_role`, `user.role`).
4. `Channels`, `Compare`, `AICabinet`, `Collection`, `Collections` (каталог),
   `Dashboard`, `Admin`, `Legal`, `Landing` (тарифы) переведены на
   мок-данные/адаптеры бэкенда (`apps/*/mock_data.py`,
   `ModerationQueue.get_user_request_data`, `LEGAL_DOCUMENTS`);
   при подключении БД view переключаются с моков на реальные данные.
   Остаётся согласовать `NotFound`.
5. Перевести словарные view на DTO из `dto_convention.md` (#197) и заодно
   нормализовать placement `errors` (top-level vs `form.errors` — см.
   [«Формат ошибок валидации»](#формат-ошибок-валидации)).
6. Обновить docstring-и из таблицы расхождений.
7. Выровнять `Post` по целевой FE-структуре (см. таблицу маппинга в разделе
   экрана): адаптировать DTO/view на backend **либо** добавить адаптер в
   странице frontend; до этого мок-дефолт в `pages/Post.tsx` скрывает
   расхождение. `Dashboard`/`Admin` уже выровнены (FE-структура отдаётся
   бэкендом).
8. Обновлять контракт при каждом изменении формы props, маршрута или
   имени компонента.

## Согласование

Критерий приёмки — документ просмотрен одним frontend- и одним
backend-разработчиком. Отметки о ревью:

| Роль | Статус | Ревьюер |
|------|--------|---------|
| Frontend | ⏳ ожидает | — |
| Backend | ⏳ ожидает | — |
