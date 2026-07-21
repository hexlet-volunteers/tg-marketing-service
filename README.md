# Telegram Marketing Service

**SPA-веб-приложение** для сбора, сравнения и анализа Telegram-каналов: парсит каналы, копит статистику (подписчики, просмотры, динамика роста), объединяет их в тематические подборки и даёт пользователям аналитику и AI-инсайты.

> Проект в активной разработке. Фронтенд (React SPA) интегрирован с Django через Inertia.js.

## Дизайн

Макеты и спецификация продукта (**tgpulse**) — в [`docs/design/`](docs/design/README.md): интерактивный hi-fi прототип всех экранов, спека с дизайн-токенами и маппингом на **Mantine**, карта «экран → майлстоун». Это источник истины для фронтенд-задач.

## Ссылки

- Хостинг — _скоро_.
- Swagger / API-документация — _скоро_.

## Стек

### Фронтенд

- **TypeScript**
- **React 19**
- **Mantine** — библиотека UI-компонентов и хуков (`@mantine/core`, `@mantine/hooks`)
- **Redux Toolkit** — управление состоянием
- **React Router** — клиентский роутинг
- **React Hook Form** — работа с формами
- **Vite** — сборка и dev-сервер
- Остальные зависимости — в [`frontend/package.json`](frontend/package.json)

### Бэкенд

- **Python 3.12**, менеджер зависимостей **uv**
- **Django 5.2**
- **PostgreSQL** (в проде) / **SQLite** (локально) — через `dj-database-url`
- **Celery + Redis** — фоновые задачи и планировщик (Celery Beat), мониторинг через **Flower**
- **Telethon** — парсинг Telegram
- **django-allauth** — аутентификация, вход через Яндекс OAuth
- **django-guardian** — ролевая модель и права доступа (см. [`docs/rbac.md`](docs/rbac.md))
- **Inertia.js** (`inertia-django`) + **django-vite** — связка Django ↔ React SPA
- **Gunicorn** — прод-сервер
- Остальные зависимости — в [`pyproject.toml`](pyproject.toml)

### Инфраструктура

- **Docker** — контейнеризация
- **GitHub Actions** — CI (тесты)
- **pytest** + **pytest-django** — тесты
- **Ruff** — линтер

## Возможности

- Парсинг Telegram-каналов через Telethon: название, описание, число подписчиков, закреплённые и последние сообщения, средние просмотры.
- Хранение истории статистики каналов и расчёт дневного прироста подписчиков.
- Тематические подборки каналов (`Group`), включая редакторские и автоподборки по категориям.
- Ролевая модель: `guest`, `user`, `partner`, `channel_moderator` (подробнее — [`docs/rbac.md`](docs/rbac.md)).
- Партнёрская программа: профиль партнёра, баланс, партнёрский код.
- AI-инсайты по каналам (тренды, рекомендации, предупреждения).

## Структура проекта

```
.
├── apps/
│   ├── users/           # пользователи, роли, партнёрские профили
│   ├── parser/          # Telegram-каналы, парсинг, статистика, AI-инсайты
│   ├── group_channels/  # подборки каналов
│   └── homepage/        # главная страница, дашборд
├── config/              # настройки Django, Celery, URL-маршруты
├── frontend/            # React + Mantine SPA
├── templates/           # серверные шаблоны Django
└── manage.py
```

## Локальная установка

Для полноценной работы нужны настроенные Django и Telegram. Фоновые задачи требуют Redis и Celery (запускаются в отдельных терминалах).

### 0. Зависимости и окружение

```sh
make install   # uv sync
```

Скопируйте [`.env.example`](.env.example) в `.env` и заполните значения.

### 1. Telegram

Настройка Telegram нужна только для парсинга данных; запуск проекта и тестов работает без неё.

1. Авторизуйтесь на [my.telegram.org/apps](https://my.telegram.org/apps) по номеру телефона вашего Telegram-аккаунта.
2. Откройте **API development tools**, заполните поля **App configuration** (если уже заполнены — не меняйте) и сохраните настройки.
3. В `.env` пропишите `TELEGRAM_API_ID` (= App api_id), `TELEGRAM_API_HASH` (= App api_hash) и `PHONE`.
4. Сгенерируйте / обновите строку сессии:

   ```sh
   make s   # uv run python manage.py start_telegram_session
   ```

   Команде можно передать параметры `API_ID`, `API_HASH`, `PHONE` для первичной настройки клиента, а также готовую `StringSession` для запуска уже сохранённой сессии.

### 2. Бэкенд (через Make)

```sh
make migrate         # применить миграции БД
make dev             # dev-сервер Django → http://127.0.0.1:8000
```

Для продакшена:

```sh
make collectstatic          # собрать статические файлы
make prod-run               # Gunicorn; порт: make prod-run PORT=8080
```

Порт dev-сервера задаётся переменной `PORT` в [`Makefile`](Makefile). Настройки — в [`config/settings.py`](config/settings.py).

### 3. Фоновые задачи (Redis + Celery)

Каждую команду запускайте в отдельном терминале:

```sh
make redis          # Redis
make celery         # Celery worker
make celery-beat    # планировщик задач (Celery Beat)
make flower         # мониторинг задач (только для разработки)
```

Расписание задач — в `CELERY_BEAT_SCHEDULE` ([`config/settings.py`](config/settings.py)). По умолчанию все каналы парсятся по расписанию раз в день.

### 4. Фронтенд

См. [`frontend/README.md`](frontend/README.md).

### 5. Режимы работы django-vite

Фронтенд запускается в одном из двух режимов. Переключение контролируется
переменной `DEBUG` в `.env`: `django-vite` использует `dev_mode = DEBUG`
([`config/settings.py`](config/settings.py)).

#### Dev-режим (HMR)

В development ассеты отдаются Vite dev-сервером, поэтому изменения во фронтенде
видны мгновенно.

Требования: `DEBUG=True` в `.env`.

Запустите в двух терминалах:

```sh
# терминал 1 — Django
make dev
# → http://127.0.0.1:8000
```

```sh
# терминал 2 — Vite dev-сервер
cd frontend
npm run dev
# → http://localhost:5173
```

В этом режиме `django-vite` проксирует запросы к ассетам на `localhost:5173`.
В шаблоне [`templates/base.html`](templates/base.html) используются теги
`{% vite_hmr_client %}`, `{% vite_react_refresh %}` и
`{% vite_asset 'src/main.tsx' %}`.

#### Prod-режим (собранные ассеты с хешами)

В production Django самостоятельно отдаёт собранные статические файлы по
манифесту Vite.

Требования: `DEBUG=False` (или `DEBUG` не задана) и собранный фронтенд.

```sh
cd frontend
npm run build

cd ..
make collectstatic
make prod-run
```

`django-vite` читает `manifest.json` и резолвит ассеты с хешами в именах файлов.
Пути сборки Vite (`build.outDir`) и `manifest_path` / `STATICFILES_DIRS` должны
быть согласованы отдельно при финальной настройке фронтенда. Текущие значения
в [`config/settings.py`](config/settings.py):

- `STATICFILES_DIRS = [BASE_DIR / "frontend" / "static"]`
- `manifest_path = STATIC_ROOT / "manifest.json"`

## Тесты и линтер

```sh
make test       # pytest
make lint       # ruff
make lint-fix   # ruff check --fix
```

## Полезные команды Make

| Команда | Действие |
|---------|----------|
| `make install` | Установка зависимостей (`uv sync`) |
| `make migrate` | Миграции БД |
| `make dev` | Dev-сервер Django |
| `make prod-run` | Прод-сервер (Gunicorn) |
| `make collectstatic` | Сбор статических файлов |
| `make s` | Генерация Telegram-сессии |
| `make redis` / `make celery` / `make celery-beat` / `make flower` | Фоновые задачи |
| `make test` / `make lint` / `make lint-fix` | Тесты и линтер |

 
