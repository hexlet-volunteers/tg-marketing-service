import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string


ROLE_MAXLENGTH = 150
BIO_MAXLENGTH = 200


# Create your models here.
class User(AbstractUser):
    avatar_image = models.CharField(
        verbose_name='url изображения профиля',
        blank=True,
        null=True
    )
    role = models.CharField(max_length=50)
    bio = models.CharField(
        max_length=200,
        verbose_name='о себе',
        blank=True
    )
    email = models.EmailField(
        verbose_name="email адрес",
        blank=True,
        unique=True
    )

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ('can_add_channel', 'Может добавлять каналы'),
            ('can_apply_partnership', 'Может подавать заявку на партнерство'),
        ]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_partner(self):
        """Проверка, является ли пользователь активным партнером."""
        return hasattr(self, 'partner_profile') and \
            self.partner_profile.status == 'active'

    @property
    def is_channel_moderator(self):
        """Проверка, является ли пользователь модератором какого-либо канала."""
        return self.moderated_channels.exists()


class PartnerProfile(models.Model):
    """Расширенный профиль для партнеров."""

    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('pending', 'На рассмотрении'),
        ('rejected', 'Отклонён'),
        ('suspended', 'Приостановлен')
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='partner_profile',
        verbose_name='Пользователь'
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    partner_since = models.DateTimeField(
        verbose_name='Партнёр с',
        auto_now_add=True
    )
    balance = models.DecimalField(
        verbose_name='Баланс',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    payment_details = models.TextField(
        verbose_name='Платёжные реквизиты',
        blank=True
    )
    partner_code = models.CharField(
        verbose_name='Партнерский код',
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Профиль партнёра'
        verbose_name_plural = 'Профили партнёров'
        permissions = [
            ('access_partner_dashboard', 'Доступ к партнерскому кабинету'),
            ('request_payout', 'Может запрашивать выплаты'),
            ('view_traffic_analytics', 'Может просматривать аналитику трафика'),
        ]

    def __str__(self):
        return f"{self.user.username} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения объекта, который генерирует
        уникальный партнерский код при создании нового профиля.

        Метод обеспечивает:
        - Автоматическую генерацию партнерского кода
        - Проверку уникальности сгенерированного кода
        - Безопасное сохранение объекта в базе данных
        """
    
        # Проверяем, существует ли уже партнерский код
        if not self.partner_code:
            """
            Если партнерский код отсутствует, начинаем генерацию уникального кода.
            Используем бесконечный цикл для гарантии уникальности.
            """
            while True:
                # Генерируем случайную строку длиной 6 символов
                random_part = get_random_string(length=6)
                """
                get_random_string генерирует криптографически безопасную случайную строку,
                которая делает код более уникальным.
                """
            
                # Создаем уникальный идентификатор на основе UUID
                unique_id = uuid.uuid4().hex[:8]
                """
                uuid.uuid4() генерирует случайный UUID.
                .hex преобразует его в шестнадцатеричную строку.
                [:8] берет первые 8 символов для компактности.
                """
            
                # Формируем финальный партнерский код
                self.partner_code = f"partner-{self.user_id}-{unique_id}-{random_part}"
                """
                Структура кода:
                - Префикс "partner-" для идентификации
                - ID пользователя для связи с профилем
                - Уникальный идентификатор
                - Случайная строка для дополнительной уникальности
                """
            
                # Проверяем уникальность сгенерированного кода
                if not PartnerProfile.objects.filter(partner_code=self.partner_code).exists():
                    """
                    Проверяем, существует ли такой код в базе данных.
                    Если код уникален, выходим из цикла.
                    """
                    break
         
        # Вызываем родительский метод save для сохранения объекта
        super().save(*args, **kwargs)
