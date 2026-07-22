# Inertia shared props

Каждый Inertia-ответ проекта содержит канонический набор общих props. Они формируются в `config.middleware.InertiaMiddleware` и являются единственным источником состояния авторизации, CSRF-токена и flash-сообщений для фронтенда.

## Контракт

```json
{
  "auth": null | {
    "id": number,
    "name": string,
    "email": string,
    "avatar_url": string | null,
    "role": "guest" | "user" | "partner" | "admin" | "channel_moderator"
  },
  "role": "guest" | "user" | "partner" | "admin" | "channel_moderator",
  "is_admin": boolean,
  "csrfToken": string,
  "flash": null | { "success"?: string, "error"?: string }
}
```

### auth

Объект авторизованного пользователя или `null` для гостя.

| Поле | Описание |
|------|----------|
| `id` | PK пользователя |
| `name` | `get_full_name()` или `username` |
| `email` | Email пользователя |
| `avatar_url` | URL аватара или пустая строка |
| `role` | Роль пользователя в нижнем регистре |

### role

Текущая роль сессии. Гости всегда получают `"guest"`. Авторизованные пользователи получают одну из ролей: `"user"`, `"partner"`, `"admin"`, `"channel_moderator"`.

### is_admin

`true`, если пользователь имеет роль `"admin"`, является staff (`is_staff`) или superuser (`is_superuser`). Для гостя — `false`.

### csrfToken

Токен CSRF для текущей сессии. Единственное место его формирования — `config.middleware.InertiaMiddleware`. Не дублировать вручную во views.

### flash

Одноразовое сообщение из сессии.

```json
{"success": "Пользователь успешно зарегистрирован"}
{"error": "Недостаточно прав"}
```

Записывается перед redirect:

```python
request.session["flash"] = {"success": "Профиль изменён."}
return redirect(...)
```

Middleware извлекает его через `request.session.pop("flash", None)` и передаёт в props. Использование отдельных ключей `flash_success` / `flash_error` запрещено.

## Правило расширения

Смежные задачи, которым нужно добавить новое общее поле (например, `show_upgrade_banner`), **не создают собственный `share()`**. Они расширяют `config.middleware.InertiaMiddleware`:

```python
# config/middleware.py
share(
    request,
    auth=...,
    role=...,
    csrfToken=...,
    flash=...,
    show_upgrade_banner=...,
)
```

Это единственный слой определения общих props.
