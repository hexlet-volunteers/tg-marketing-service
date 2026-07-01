# Фронтенд

SPA-часть проекта: React + TypeScript, интегрируется с Django через Inertia.js.

## Стек

- **TypeScript**
- **React 19**
- **Mantine** — библиотека UI-компонентов и хуков (`@mantine/core`, `@mantine/hooks`)
- **Redux Toolkit** — управление состоянием
- **React Router** — клиентский роутинг
- **React Hook Form** — работа с формами
- **Vite** — сборка и dev-сервер
- Остальные зависимости — в [`package.json`](package.json)

## Методологии и соглашения

- Архитектура — [Feature-Sliced Design (FSD)](https://feature-sliced.design/ru/): слои `app/`, `pages/`, `widgets/`, `features/`, `components/`.
- Вёрстка — **mobile first**.
- Названия веток в git: `[type]/[short-description]`. Возможные типы:
  - `feat` — добавляет функциональность для конечного пользователя;
  - `refactor` — изменения кода без новой функциональности и без фикса багов;
  - `bugfix` — исправление ошибок;
  - `chore` — изменения, не влияющие на код приложения (зависимости / конфиги / CI / скрипты и пр.);
  - `docs` — документация.

## Запуск

```sh
git clone https://github.com/Hexlet/hexlet-price-tracker.git
cd hexlet-price-tracker/frontend
npm i
npm run dev
```

## Сборка

```sh
npm run build
```

> Все команды выполняются из папки `frontend/`.

## Скрипты

| Команда | Действие |
|---------|----------|
| `npm run dev` | Dev-сервер Vite |
| `npm run build` | Сборка (`tsc -b && vite build`) |
| `npm run preview` | Предпросмотр собранного приложения |
| `npm run lint` | ESLint |
| `npm run typecheck` | Проверка типов (`tsc --noEmit`) |

Остальные скрипты — в [`package.json`](package.json).
