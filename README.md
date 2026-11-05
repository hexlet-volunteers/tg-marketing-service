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
- **Django 6**
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
- **GitHub Actions** — CI (lint, типы, тесты)
- **pytest** + **pytest-django** — тесты
- **Ruff** — линтер
- **mypy** + **django-stubs** — проверка типов

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
│   ├── admin/           # админка модерации каналов
│   ├── ai/              # клиент LLM и разбор AI-инсайтов
│   ├── billing/         # тарифы и подписки
│   ├── blog/            # статьи блога
│   ├── group_channels/  # подборки каналов
│   ├── homepage/        # главная страница, дашборд
│   ├── legal/           # тексты правовых документов
│   ├── parser/          # Telegram-каналы, статистика, AI-инсайты
│   └── users/           # пользователи, роли, партнёрские профили
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

### 0a. Запуск через Docker Compose (issues #381, #382)

Раньше локальный стейк требовал 5 терминалов (Django, Redis, Celery worker, Celery beat, Flower) и ещё парочку для фронтенда. Теперь всё поднимается одной командой ([`compose.yml`](compose.yml)):

```sh
docker compose up
```

Compose поднимает уже сконфигурированные между собой сервисы:

| Сервис | Порт | Что это |
| --- | --- | --- |
| `web` | [localhost:8000](http://localhost:8000) | Django: миграции + collectstatic + runserver |
| `frontend` | [localhost:5173](http://localhost:5173) | Vite dev-сервер (HMR), django-vite смотрит сюда |
| `redis` | 6379 (только внутри сети) | broker для Celery |
| `celery-worker` | — | воркер с `CELERY_BROKER_URL=redis://redis:6379/0` |
| `celery-beat` | — | планировщик `CELERY_BEAT_SCHEDULE` |
| `flower` | [localhost:5555](http://localhost:5555) | мониторинг задач |

Все сервисы используют переменные из `.env` (`env_file`), поэтому `.env` должен существовать ещё до `docker compose up`. Код монтируется с хоста, так что правки подхватываются без пересборки; зависимости (`uv`-venv и `node_modules`) живут в named-томах, а не в локальных директориях. SQLite-база — файл `db.sqlite3` в корне репозитория, данные переживают перезапуск.

Миграции применяются автоматически при старте `web`; для ручного прогона и django-команд:

```sh
docker compose exec web uv run python manage.py migrate
docker compose exec web uv run python manage.py seed_demo   # демо-данные (только DEBUG)
```

Для генерации Telegram-сессии в контейнере (интерактивная команда):

```sh
docker compose exec web uv run python manage.py start_telegram_session
```

Полученную строку пропишите в `.env` как `TELEGRAM_SESSION_STRING` и перезапустите сервисы парсера:

```sh
docker compose restart celery-worker celery-beat
```

Полезные команды:

```sh
docker compose build          # пересобрать образы после смены зависимостей
docker compose logs -f web    # логи отдельного сервиса
docker compose down           # остановить стек (данные остаются)
docker compose down -v        # остановить и снести тома зависимостей
```

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
make migrate         # makemigrations + migrate
make seed-demo       # демо-данные из mocks/ (только DEBUG); см. docs/demo_data.md
make dev             # dev-сервер Django → http://127.0.0.1:8000
```

Для продакшена:

```sh
make collectstatic          # собрать статические файлы
make prod-run               # Gunicorn
```

Порт прод-сервера задаётся переменной `PORT` в [`Makefile`](Makefile) (`make prod-run PORT=8080`). Настройки — в [`config/settings.py`](config/settings.py).

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
make test        # pytest
make lint        # ruff
make lint-fix    # ruff check --fix
make typecheck   # mypy
```

### Pre-commit

Pre-commit автоматически проверяет код перед каждым коммитом (ruff lint + format, mypy). Установите hooks один раз:

```sh
uv run pre-commit install
```

Подробнее об использовании и обходе ошибок — в [`PRE-COMMIT.md`](PRE-COMMIT.md).

## Полезные команды Make

| Команда | Действие |
|---------|----------|
| `make install` | Установка зависимостей (`uv sync`) |
| `make migrate` | Миграции БД (`makemigrations` + `migrate`) |
| `make dev` | Dev-сервер Django |
| `make prod-run` | Прод-сервер (Gunicorn) |
| `make collectstatic` | Сбор статических файлов |
| `make s` | Генерация Telegram-сессии |
| `make redis` / `make celery` / `make celery-beat` / `make flower` | Фоновые задачи |
| `make test` / `make lint` / `make lint-fix` / `make typecheck` | Тесты, линтер и проверка типов |
