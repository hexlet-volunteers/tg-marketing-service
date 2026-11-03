from django.test import TestCase, override_settings
from django.urls import path
from django.views import View
from inertia import render

from apps.parser.models import ChannelModerator, TelegramChannel
from apps.users.constants import UserRole
from apps.users.models import User
from config.mixins import ChannelModeratorRequiredMixin


class ModeratorView(ChannelModeratorRequiredMixin, View):
    """Тестовое представление для проверки доступа модератора через Inertia."""

    def get(self, request):
        return render(
            request,
            "Moderator/Test",
            props={"message": "Доступ разрешён"},
        )


urlpatterns = [
    path("test-moderator/", ModeratorView.as_view(), name="test-moderator"),
]


@override_settings(ROOT_URLCONF=__name__)
class ChannelModeratorRequiredMixinTest(TestCase):
    """Проверки доступа модератора через Django test client."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="secret123",
            role=UserRole.CHANNEL_MODERATOR,
        )
        self.channel = TelegramChannel.objects.create(
            channel_id=987654321,
            title="Тестовый канал",
        )

    def test_channel_moderator_can_access_view(self) -> None:
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )
        self.client.force_login(self.user)

        response = self.client.get(
            "/test-moderator/",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Inertia"), "true")
        self.assertEqual(
            response.json()["props"]["auth"]["role"],
            UserRole.CHANNEL_MODERATOR,
        )
        self.assertFalse(response.json()["props"]["is_admin"])

    def test_partner_owner_can_access_view(self) -> None:
        """Партнёр-владелец проходит guard."""
        self.user.role = UserRole.PARTNER
        self.user.save(update_fields=["role"])
        ChannelModerator.objects.create(
            user=self.user,
            channel=self.channel,
            is_owner=True,
        )
        self.client.force_login(self.user)

        response = self.client.get(
            "/test-moderator/",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["props"]["auth"]["role"],
            UserRole.PARTNER,
        )
        self.assertFalse(response.json()["props"]["is_admin"])

    def test_user_with_wrong_role_is_denied(self) -> None:
        self.user.role = UserRole.USER
        self.user.save(update_fields=["role"])
        self.client.force_login(self.user)

        response = self.client.get("/test-moderator/")

        self.assertIn(response.status_code, (302, 403))

    def test_user_without_channel_moderator_status_is_denied(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get("/test-moderator/")

        self.assertIn(response.status_code, (302, 403))
