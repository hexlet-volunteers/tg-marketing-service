# Контракт регистрации

## Эндпоинт

`GET /auth/create/` возвращает Inertia-компонент `FormRegistration`.

`POST /auth/create/` создаёт пользователя по email.

## Поля запроса

Обязательные поля:

- `email`
- `password1`
- `password2`

Необязательные поля:

- `first_name`
- `last_name`
- `bio`
- `avatar_image`

Поле `username` форма регистрации не принимает: сервер генерирует его из части email до `@` и случайного суффикса.

## Успешная регистрация

Если данные валидны, сервер:

- создаёт пользователя;
- назначает `role="user"`;
- если `avatar_image` не передан, назначает дефолтный аватар из статического файла `/static/users/default-avatar.svg`;
- выполняет вход нового пользователя через Django auth;
- редиректит на дашборд: `homepage:dashboard` (`/dashboard/`).

## Ошибки валидации

Если данные невалидны, сервер снова рендерит `FormRegistration` и передаёт данные формы вместе с ошибками:

```json
{
  "form": {
    "data": {
      "first_name": "",
      "last_name": "",
      "password1": "",
      "password2": "",
      "email": "",
      "bio": "",
      "avatar_image": ""
    },
    "errors": {}
  }
}
```

Уникальность email возвращается как ошибка поля `email`.

Ошибки валидаторов пароля Django возвращаются как ошибки поля `password2`.
