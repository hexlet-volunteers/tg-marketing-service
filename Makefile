PORT ?= 8000

migrate:	
	uv run python manage.py makemigrations
	uv run python manage.py migrate

collectstatic:
	uv run python manage.py collectstatic --noinput

dev:
	uv run python manage.py runserver

prod-run:
	uv run gunicorn -b 0.0.0.0:$(PORT) config.wsgi

lint:
	uv run ruff

lint-fix:
	uv run ruff check --fix

redis:
	redis-server

celery:
	uv run celery -A config worker --loglevel=info

celery-beat:
	uv run celery -A config beat --loglevel=info

flower:
	uv run celery -A config flower

s:
	uv run python manage.py start_telegram_session

fixtures:
	@mkdir -p tests/fixtures
	uv run python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from tests.generate_fixtures import ModelAndFormFixtureGenerator; ModelAndFormFixtureGenerator().generate_all()"

test: fixtures
	uv run pytest tests/ -v --tb=short

test-cov: fixtures
	uv run pytest tests/ --cov=apps --cov=config --cov-report=term-missing

install:
	uv sync
.PHONY: install