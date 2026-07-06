from django.db import models

from apps.users.models import User


class TelegramChannel(models.Model):
    channel_id = models.BigIntegerField(unique=True, verbose_name="ID канала")
    # invite_link = models.URLField(
    #     max_length=255, blank=True, null=True, verbose_name='Инвайт ссылка',
    # )
    username = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Username",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название канала",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание канала",
    )
    # linked_chat_id = models.BigIntegerField(
    #     blank=True, null=True, verbose_name='ID чата канала',
    # )
    participants_count = models.IntegerField(
        default=0,
        verbose_name="Количество подписчиков",
    )
    # photo_url = models.URLField(
    #     max_length=512, blank=True, null=True, verbose_name='Ссылка на фото',
    # )
    parsed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата парсинга",
    )
    pinned_messages = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name="Закрепленное сообщение",
    )
    creation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата создания",
    )
    last_messages = models.JSONField(
        blank=True,
        null=True,
        default=list,
        verbose_name="Последние сообщения",
    )
    average_views = models.IntegerField(
        default=0,
        verbose_name="Среднее количество просмотров",
    )
    category = models.CharField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Категория канала",
    )
    country = models.CharField(
        blank=True,
        null=True,
        verbose_name="Страна канала",
    )
    language = models.CharField(
        blank=True,
        null=True,
        verbose_name="Язык канала",
    )

    class Meta:
        verbose_name = "Telegram канал"
        verbose_name_plural = "Telegram каналы"

    def last_stat(self):
        """Получение последней статистики канала"""
        return self.channelstats_set.order_by("-parsed_at").first()

    def __str__(self):
        return f"{self.channel_id} канал {self.title}"

    def get_data(self):
        """
        Метод возвращает представление данных канала в виде словаря,
        пригодного для передачи на фронтенд (Inertia.js).
        """
        return {
            "id": self.channel_id,
            "username": self.username,
            "title": self.title,
            "description": self.description,
            "participants_count": self.participants_count,
            "parsed_at": self.parsed_at,
            "pinned_messages": self.pinned_messages,
            "creation_date": self.creation_date,
            "last_messages": self.last_messages,
            "average_views": self.average_views,
            "category": self.category,
            "country": self.country,
            "language": self.language,
        }


class ChannelModerator(models.Model):
    """Модель для связи пользователей с каналами в качестве модераторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="moderated_channels",
        verbose_name="Модератор",
    )
    channel = models.ForeignKey(
        TelegramChannel,
        on_delete=models.CASCADE,
        related_name="moderators",
        verbose_name="Канал",
    )
    is_owner = models.BooleanField(
        default=False, verbose_name="Владелец канала"
    )
    can_edit = models.BooleanField(
        default=True, verbose_name="Может редактировать"
    )
    can_delete = models.BooleanField(
        default=False, verbose_name="Может удалять"
    )
    can_manage_moderators = models.BooleanField(
        default=False, verbose_name="Может управлять модераторами"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата назначения",
    )

    class Meta:
        verbose_name = "Модератор канала"
        verbose_name_plural = "Модераторы каналов"
        unique_together = ["user", "channel"]
        db_table = "channel_moderators"

    def __str__(self):
        role = "Владелец" if self.is_owner else "Модератор"
        return f"{self.user} - {role} канала {self.channel.title}"


class ChannelStats(models.Model):
    channel = models.ForeignKey(
        TelegramChannel,
        on_delete=models.CASCADE,
        verbose_name="Канал",
    )
    participants_count = models.IntegerField(
        verbose_name="Количество участников",
    )
    daily_growth = models.IntegerField(
        default=0,
        verbose_name="Прирост за день",
    )
    parsed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Статистика канала"
        verbose_name_plural = "Статистика каналов"
        get_latest_by = "parsed_at"
        ordering = ["-parsed_at"]

    def __str__(self):
        return f"{self.channel} - {self.parsed_at}"


class AIInsight(models.Model):
    """Модель для хранения AI-предложений для пользователей"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ai_insights",
        verbose_name="Пользователь",
    )
    channel = models.ForeignKey(
        TelegramChannel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ai_insights",
        verbose_name="Канал",
    )
    insight_text = models.TextField(verbose_name="Текст инсайта")
    insight_type = models.CharField(
        max_length=50,
        choices=[
            ("trend", "Тренд"),
            ("recommendation", "Рекомендация"),
            ("warning", "Предупреждение"),
            ("positive", "Позитивный"),
        ],
        verbose_name="Тип инсайта",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "AI инсайт"
        verbose_name_plural = "AI инсайты"
        ordering = ["-created_at"]
