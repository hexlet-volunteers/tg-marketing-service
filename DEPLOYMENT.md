## Database
1. На Render, в окошке “New”, выбрать опцию "Postgres".
2. Задать имя для экземпляра "Postgres" (имя базы данных и пользователя по желанию) и переключиться на бесплатный вариант для базы данных. Нажать создать базу данных и подождать пару минут.
3. Записать данные базы данных для указания переменных в отдельный 'env' файл (HOSTDB=Hostname, PORTDB=Port, NAMEDB=Database, USERDB=Username, PASSWORDDB=Password)

## Backend
1. На Render, в окошке “New”, выбрать опцию "Web Service".
2. Выбрать или указать ссылку на нужный репозиторий на GitHub.
3. Сменить "Language" на Python. Сменить "Branch" на нужную ветку (если необходимо).
4. В "Build Command" указать `make collectstatic && make migrate`
5. В "Start Command" указать `make prod-run`
6. Переключиться на бесплатный вариант
7. Указать переменные окружения из `.env` файла, поменяв переменные для базы данных (с локальных на Postgres рендера).
8. Нажать "Deploy Web Service".

## Frontend
1. На Render, в окошке “New”, выбрать опцию "Web Service".
2. Выбрать или указать ссылку на нужный репозиторий на GitHub.
3. Сменить "Language" на Node. Сменить "Branch" на нужную ветку (если необходимо).
4. Указать “Root Directory” `./frontend`
5. В "Build Command" указать `./build_render.sh` [на данный момент]
6. В "Start Command" указать `npm run render` [на данный момент]
7. Переключиться на бесплатный вариант
8. Указать переменные окружения из `.env` файла, поменяв переменные для базы данных (с локальных на Postgres рендера). Добавить переменную ‘VITE_ALLOWED_HOST=name_your_app.onrender.com’
9. Нажать "Deploy Web Service".