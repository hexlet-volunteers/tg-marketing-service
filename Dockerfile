# Рабочий образ приложения (issue #394): uv/зависимости, код,
# entrypoint поднимает web-процесс (gunicorn по умолчанию,
# runserver — комнда docker compose в compose.yml).
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -yq --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

WORKDIR /app

# Сначала только манифесты зависимостей: слой с uv sync кэшируется,
# пока не изменился uv.lock / pyproject.toml.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync

# Код в контейнерах compose монтируется volume'ом c хоста; здесь
# копия нужна для standalone-запуска образа (make prod-run).
COPY . .

EXPOSE 8000

# CMD переопределяется в compose (dev: runserver / celery / flower),
# по умолчанию — prod web-процесс: миграции, статика, gunicorn.
CMD ["sh", "-c", "make migrate && make collectstatic && exec make prod-run"]
