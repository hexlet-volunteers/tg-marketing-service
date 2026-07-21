from django.core.validators import URLValidator
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode

from apps.users.models import User


class Group(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Название",
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        allow_unicode=True,
        verbose_name="URL-идентификатор",
        blank=True,
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Описание",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_groups",
        related_query_name="owned_group",
        verbose_name="Владелец",
    )
    is_editorial = models.BooleanField(
        default=False,
        verbose_name="Редакторская подборка",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок на главной",
    )
    channels = models.ManyToManyField(
        "parser.TelegramChannel",
        verbose_name="Каналы",
        blank=True,
        related_name="groups",
    )
    image_url = models.TextField(
        validators=[URLValidator()],
        blank=True,
        verbose_name="обложка группы",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создана",
    )

    class Meta:
        db_table = "groups"
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or not self.slug.strip():
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    @property
    def saves_count(self):
        return self.saves.count()

    def get_data(self):
        """
        Метод возвращает представление данных группы в виде словаря,
        пригодного для передачи на фронтенд (Inertia.js).
        """
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "owner": self.owner.username,
            "is_editorial": self.is_editorial,
            "order": self.order,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat(),
            "saves_count": self.saves_count,
        }


class SavedCollection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_collections",
        verbose_name="Пользователь",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="saves",
        verbose_name="Подборка",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        db_table = "saved_collections"
        verbose_name = "Сохраненная подборка"
        verbose_name_plural = "Сохраненные подборки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "group"],
                name="unique_saved_collection_user_group",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.group}"


class AutoGroupRule(models.Model):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="auto_rule",
        verbose_name="Группа",
    )

    category = models.CharField(max_length=255, verbose_name="Категория")

    materialize = models.BooleanField(
        default=True,
        verbose_name="Материализовать в M2M",
    )

    class Meta:
        db_table = "auto_group_rules"
        verbose_name = "Правило автоподборки"
        verbose_name_plural = "Правила автоподборок"

    def __str__(self):
        return f'AutoRule[{self.group.name}] category="{self.category}"'
