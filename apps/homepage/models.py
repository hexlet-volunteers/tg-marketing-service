from django.db import models


class HomePageComponent(models.Model):
    COMPONENT_TYPES = [
        ("hero", "Hero секция"),
        ("features", "Возможности"),
        ("screenshots", "Скриншоты"),
        ("ai_assistant", "ИИ-помощник"),
        ("how_it_works", "Как это работает"),
        ("subscriptions", "Подписки"),
        ("faq", "FAQ"),
        ("footer", "Футер"),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.JSONField(
        verbose_name="Содержимое",
        help_text="JSON с данными компонента",
    )
    component_type = models.CharField(
        max_length=50, choices=COMPONENT_TYPES, verbose_name="Тип компонента"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Компонент главной страницы"
        verbose_name_plural = "Компоненты главной страницы"
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"{self.get_component_type_display()}: {self.title}"
