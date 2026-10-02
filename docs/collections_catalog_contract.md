# Контракт каталога подборок

## GET `/collections/`

Публичный endpoint каталога подборок.

Endpoint возвращает Inertia-страницу с компонентом `Collections`.

Успешный ответ содержит Inertia-payload:

```json
{
  "component": "Collections",
  "props": {
    "featured": [
      {
        "id": 1,
        "name": "Новости",
        "slug": "novosti",
        "description": "Новостные каналы",
        "is_editorial": true,
        "curator": "curator",
        "channel_count": 12,
        "cover": "https://example.com/cover.jpg",
        "gradient_key": "collection-1"
      }
    ],
    "collections": [
      {
        "id": 1,
        "name": "Новости",
        "slug": "novosti",
        "description": "Новостные каналы",
        "is_editorial": true,
        "curator": "curator",
        "channel_count": 12,
        "cover": "https://example.com/cover.jpg",
        "gradient_key": "collection-1"
      }
    ]
  },
  "url": "/collections/"
}
```

Общие Inertia props (`auth`, `role`, `is_admin`, `csrfToken`, `flash`)
передаются middleware. Их контракт описан в
[`inertia-shared-props.md`](./inertia-shared-props.md).

## `collections`

`collections` содержит полный список подборок каталога.

Подборки сортируются:

1. по `order` по возрастанию;
2. при одинаковом `order` — по `name` по возрастанию;
3. при одинаковых `order` и `name` — по `id` по возрастанию.

Каждая подборка содержит:

* `id` — идентификатор подборки;
* `name` — название;
* `slug` — URL-идентификатор;
* `description` — описание подборки или `null`;
* `is_editorial` — признак редакторской подборки;
* `curator` — username куратора или `null`;
* `channel_count` — количество каналов в подборке;
* `cover` — URL обложки или пустая строка;
* `gradient_key` — стабильный ключ градиента для оформления подборки.

## `featured`

`featured` содержит не более трёх подборок.

Для формирования `featured` используется следующий порядок:

1. `is_editorial` — редакторские подборки (`true`) идут первыми;
2. `order` — внутри каждой группы по возрастанию;
3. `id` — при одинаковых `is_editorial` и `order` по возрастанию.

Итоговый порядок:

`is_editorial DESC → order ASC → id ASC`.

Из полученного списка выбираются первые три подборки.

Если в каталоге меньше трёх подборок, `featured` содержит все доступные
подборки.

Подборка из `featured` также присутствует в полном списке `collections`.

## `channel_count`

`channel_count` — количество каналов подборки.

Для обычной подборки количество каналов определяется через M2M-связь
`Group.channels`.

Для автоматической подборки количество каналов определяется по категории,
указанной в связанном `AutoGroupRule`. Учитываются все
`TelegramChannel` с соответствующим значением `category`.

Frontend не определяет способ расчёта `channel_count`: backend возвращает
готовое количество.

Расчёт выполняется без N+1-запросов.

## `gradient_key`

`gradient_key` — стабильный ключ для выбора оформления подборки на frontend.

Формируется на backend по идентификатору подборки:

```text
collection-{id}
```

Например:

```text
collection-1
collection-25
collection-142
```

Ключ не зависит от порядка элементов каталога и не изменяется между запросами
для одной и той же подборки.

## Пустой каталог

Если подборок нет, endpoint возвращает успешный Inertia-ответ с пустыми
массивами:

```json
{
  "component": "Collections",
  "props": {
    "featured": [],
    "collections": []
  },
  "url": "/collections/"
}
```

## Ограничения endpoint

Endpoint предназначен только для получения данных каталога.

Создание, изменение и удаление подборок через `/collections/` не выполняется.

Для реализации каталога дополнительные миграции не требуются.
