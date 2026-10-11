# DTO и Inertia props

## Назначение

Сырые `dict`, создаваемые напрямую во view, могут привести к ошибкам формы данных,
которые обнаруживаются только на стороне frontend или уже у пользователя в интерфейсе.

Pydantic DTO решают эту проблему:

- валидируют структуру данных на backend;
- фиксируют контракт между Django и React;
- служат единственным источником истины для формы Inertia props;
- позволяют обнаруживать ошибки данных до передачи их во frontend.

Каждая Inertia-страница должна иметь явный контракт данных в виде DTO.


## Структура DTO

Каждое Django-приложение, которое передает данные в Inertia-представления,
должно иметь пакет `dto/`.

Пример:
```
apps/
├── parser/
│ ├── dto/
│ │ ├── channel_dto.py
│ └── views.py
│
└── homepage/
└── dto/
└── dashboard_dto.py
```

DTO должны быть обычными Pydantic-моделями:

```python
from pydantic import BaseModel


class ChannelDTO(BaseModel):
    id: int
    title: str


class ChannelListDTO(BaseModel):
    channels: list[ChannelDTO]
```

#### DTO отвечают только за:

описание структуры данных;
валидацию типов;
формирование frontend-контракта.

#### DTO не должны содержать:

бизнес-логику;
работу с ORM;
запросы к базе данных.

## Создание DTO

Рекомендуется создавать небольшие переиспользуемые DTO и собирать из них DTO уровня страницы.

Например:
```
TelegramChannel ORM
        |
        v
   ChannelDTO
        |
        v
 ChannelListDTO
        |
        v
 ChannelAnalytics props
```
ChannelDTO описывает отдельный элемент данных.

ChannelListDTO описывает полный контракт страницы.

## Сериализация DTO

Перед передачей данных в Inertia DTO сериализуется через:
```
model_dump(mode="json")
```
Это гарантирует преобразование данных в JSON-совместимые типы.

Например:
```python
dto = ChannelListDTO(
    channels=[
        ChannelDTO(
            id=1,
            title="Example channel",
        )
    ]
)

dto.model_dump(mode="json")
```
Результат:
```json
{
  "channels": [
    {
      "id": 1,
      "title": "Example channel"
    }
  ]
}
```
## Renderer helper

Для рендера Inertia-страниц с DTO используется:
```python
config.renderers.render_inertia_from_dto(
    request,
    component,
    props=dto,
)
```
Хелпер принимает экземпляр Pydantic DTO и автоматически сериализует его перед передачей в Inertia.

Пример:
```python
dto = ChannelListDTO(
    channels=channel_dtos,
)

return render_inertia_from_dto(
    request,
    "ChannelAnalytics",
    props=dto,
)
```
Внутри renderer выполняется:
```
props = dto.model_dump(mode="json")
```
После этого во frontend передается обычная JSON-структура.

## Правила использования

Не передавать ORM-модели напрямую в Inertia props.

Нельзя:
```python
return render_inertia(
    request,
    "ChannelAnalytics",
    props={"channels": TelegramChannel.objects.all()},
)
```
Не создавать вручную структуры данных во view.

Нельзя:
```python
props = {
    "channels": [
        {
            "id": channel.id,
            "title": channel.title,
        }
    ]
}
```
Правильно:
```
channel_dtos = [
    ChannelDTO(**channel.get_data())
    for channel in channels
]

dto = ChannelListDTO(
    channels=channel_dtos,
)

return render_inertia_from_dto(
    request,
    "ChannelAnalytics",
    props=dto,
)
```
## ParserListView

ParserListView для страницы ChannelAnalytics является эталонным примером использования DTO.

Поток данных:
```
TelegramChannel ORM
        |
        v
   ChannelDTO
        |
        v
 ChannelListDTO
        |
        v
render_inertia_from_dto()
        |
        v
model_dump(mode="json")
        |
        v
 Inertia props
        |
        v
 React component
```
Новые экранные задачи должны использовать аналогичный подход со своими DTO.

## DashboardDTO

Поток DashboardDTO
(apps/homepage/dto/dashboard_dto.py) остается без изменений.

Существующая реализация Dashboard продолжает работать в текущем виде и не входит в данный рефакторинг.
