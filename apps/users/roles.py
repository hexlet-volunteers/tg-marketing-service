from django.db import models

from apps.users.models import User


class UserRoleHistoryManager(models.Manager):
    def current_role(self, user):
        """
        Возвращает объект Role текущей роли пользователя или None
        """
        history = self.filter(user=user, end_date__isnull=True).first()
        if history:
            return history.role
        return None


class Role(models.Model):
    """Модели ролей и модель истории ролей"""

    code = models.CharField(
        max_length=50, verbose_name="Уникальный идентификатор роли", unique=True
    )
    name = models.CharField(max_length=50, verbose_name="Роль")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return str(self.name) or "NONE"


class UserRoleHistory(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
    )
    start_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата назначения"
    )
    end_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата снятия"
    )
    reason = models.CharField(max_length=250, null=True, blank=True)

    objects = UserRoleHistoryManager()

    class Meta:
        verbose_name = "История роли"
        verbose_name_plural = "История ролей"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                condition=models.Q(end_date__isnull=True),
                name="unique_current_role_per_user",
            )
        ]

    def __str__(self):
        return f"Роль {self.role.name} пользователя {self.user.username}"

    @property
    def is_current_role(self):
        return self.end_date is None
