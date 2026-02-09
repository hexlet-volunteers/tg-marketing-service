# PriceAggregator 1.0

## Описание

SPA веб-приложение. Единый портал для сравнения цен для сегментов B2C.

- [Хостинг](Ссылка) пока нет
- [Сваггер](Ссылка) пока нет

## Фронтенд-стэк

- Typescript
- React 19
- Redux Toolkit: упраление состоянием
- React Router: клиентский роутинг
- React Hook Form: формы
- Vite
- shadcn/ui с Tailwind СSS
- см. другие зависимости в [`package.json`](package.json)

## Бэкенд-стек

- Python
- Django
- PostgreSQL
- Docker 
- GitHub Actions
- см. другие зависимости в [`package.json`](package.json)

## Локальная установка
Для запуска приложения на локальном сервере необходима настройка Django, Telegram.  
Для полноценной работы приложения на локальном сервере необходима настройка Redis, Celery (запускаются в отдельном терминале).

### Telegram
Настройка Telegram нужна для парсинга данных.
1. Авторизуйтесь на [My Telegram](https://my.telegram.org/apps) с помощью номера телефона вашего Telegram аккаунта.
#### CLI
1.1. Запустите команду заполнения `TELEGRAM_SESSION_STRING`
   ```sh
   make s
   ```
1.2. Передайте в команде параметры "API_ID", "API_HASH", "PHONE" для первой настройки клиента Telegram. Также передайте StringSession для запуска уже сохраненной версии клиента Telegram. 
#### .env
2.1. В `.env` присвойте переменной "PHONE".  
2.2. Перейдите на [API development tools](https://my.telegram.org/apps).  
2.3. Заполните поля "App configuration". Если поля уже заполнены, не меняйте их.  
2.4. Сохраните настройки.  
2.5. В `.env` присвойте переменной "TELEGRAM_API_ID" значение "App api_id", "TELEGRAM_API_HASH" значение "App api_hash".  
2.6. Если не выполняли п. 1.1, тогда запустите команду 
   ```sh
   make s
   ```


### Бэкенд (запуск через Make)

1. Примените миграции базы данных:
   ```sh
   make migrate
   ```

2. Соберите статические файлы (требуется только для продакшена):
   ```sh
   make collectstatic
   ```

3. Запустите dev сервер Django (требуется только для разработки):
   ```sh
   make dev
   ```
   По умолчанию сервер доступен на http://127.0.0.1:8000. Порт задаётся переменной PORT в [`Makefile`](Makefile).

4. Запустите prod-сервер на Gunicorn (требуется только для продакшена):
   ```sh
   make prod-run
   ```
   Можно указать порт: `make prod-run PORT=8080`. См. настройки в [`config/settings.py`](config/settings.py).

### Фоновые задачи (Redis + Celery). Запускаются в отдельном терминале.

1. Запустите Redis:
   ```sh
   make redis
   ```

2. Запустите Celery worker:
   ```sh
   make celery
   ```

3. Запустите планировщик задач Celery Beat:
   ```sh
   make celery-beat
   ```
   Плановые задачи настраиваются в [`config/settings.py`](config/settings.py) (CELERY_BEAT_SCHEDULE).

4. Откройте мониторинг задач (Flower) (используется только для разработки):
   ```sh
   make flower
   ```


### Утилиты

1. Сгенерируйте/обновите Telegram сессию через management команду (запускает uv run python manage.py set_telegram_session):
   ```sh
   make s
   ```