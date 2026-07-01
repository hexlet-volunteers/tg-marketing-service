# RBAC — ролевая модель и права доступа

Ролевая модель проекта построена на встроенных группах Django и библиотеке **django-guardian** (object-level permissions).

## Установка

`django-guardian` уже добавлена в [`pyproject.toml`](pyproject.toml) и устанавливается вместе с остальными зависимостями:

```sh
make install   # uv sync
```

Ручная установка (вне uv):

```sh
pip install django-guardian
```

## Настройка `settings.py`

```python
INSTALLED_APPS = [
    # ...
    'guardian',
    # ...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',   # основной бэкенд аутентификации
    'guardian.backends.ObjectPermissionBackend',   # object-level permissions
]

# Опционально: возвращать 403 при отказе в доступе
GUARDIAN_RAISE_403 = True
```

Middleware для ролей и (при необходимости) object-level прав:

```python
MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ...
    'apps.users.middleware.RoleMiddleware',              # прокидывает роль в request
    # 'guardian.middleware.ObjectPermissionMiddleware',  # включить для object-level прав
]
```

Создание таблиц:

```sh
make migrate
# или напрямую:
python manage.py migrate guardian
```

## Ключевые модули

| Модуль | Назначение |
|--------|-----------|
| [`apps/users/roles.py`](apps/users/roles.py) | Модели `Role` и `UserRoleHistory` (история назначения ролей) |
| [`config/mixins.py`](config/mixins.py) | Миксины для ограничения доступа к вью по ролям |
| [`apps/users/middleware.py`](apps/users/middleware.py) | `RoleMiddleware` — прокидывает текущую роль в `request.role` |

Получить роль внутри запроса:

```python
role = request.role
```

Через модель — стандартным API Django ORM (`Role`, `UserRoleHistory`).

## Роли

| Код | Название |
|-----|----------|
| `guest` | Guest |
| `user` | User |
| `partner` | Partner |
| `channel_moderator` | Channel Moderator |

## Ограничение доступа во вью

В [`config/mixins.py`](config/mixins.py) есть готовые миксины — наследуйте их в нужном представлении:

- `UserAuthenticationCheckMixin` — требует авторизации;
- `GuestRequiredMixin` — только для неавторизованных (гостей);
- `UserRequiredMixin` — для любых авторизованных (`user`, `partner`, `channel_moderator`);
- `PartnerRequiredMixin` — только для активных партнёров;
- `ChannelModeratorRequiredMixin` — только для модераторов каналов.

Базовый класс `RoleRequiredMixin` позволяет описать собственную роль — переопределите `allowed_roles` (и при необходимости метод `_test_role`).

## Контроль прав в админке

В стандартную админ-панель Django встроен раздел object-level permissions (django-guardian). Откройте объект (пользователь, группа, канал и т.д.) — в правом верхнем углу появится кнопка управления правами, ведущая в соответствующий раздел.
