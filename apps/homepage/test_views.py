from datetime import timedelta
from typing import Any

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.billing.models import Plan, Subscription
from apps.homepage.models import HomePageComponent
from apps.parser.models import (
    ChannelModerator,
    ChannelStats,
    Post,
    PostReaction,
    TelegramChannel,
)
from apps.users.models import User
from mocks.landing import MOCK_KPIS


class IndexViewTest(TestCase):
    component: HomePageComponent

    @classmethod
    def setUpTestData(cls):
        cls.component = HomePageComponent.objects.create(
            title="My Component Title",
            content={"content": "Some content here"},
            order=1,
            is_active=True,
        )

    def test_index_view_with_inertia_props(self):
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)

        # Django test client автоматически декодирует JSON
        data = response.json()

        # Inertia-обёртка
        self.assertIn("component", data)
        self.assertIn("props", data)
        self.assertIn("url", data)
        self.assertIn("version", data)

        # Проверяем props
        props = data["props"]
        self.assertIn("components", props)

        components = props["components"]
        self.assertGreater(len(components), 0)

        first_component = components[0]["props"]
        self.assertEqual(first_component["title"], self.component.title)
        self.assertEqual(
            first_component["content"], self.component.content["content"]
        )
        self.assertEqual(first_component["order"], self.component.order)

    def test_index_view_serves_tariffs(self):
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]
        tariffs = props["tariffs"]

        self.assertEqual(
            [tariff["name"] for tariff in tariffs],
            ["Free", "Pro", "Agency"],
        )
        pro = next(tariff for tariff in tariffs if tariff["name"] == "Pro")
        self.assertEqual(pro["price"], "990 ₽")
        self.assertEqual(pro["period"], "в месяц")
        self.assertEqual(pro["button"]["variant"], "primary")
        self.assertTrue(pro["isHighlighted"])

    def _get_inertia_props(
        self,
        url_name: str = "main_index",
    ) -> dict[str, Any]:
        response = self.client.get(
            reverse(url_name),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_guest_inertia_props_include_shared_auth_state(self) -> None:
        props = self._get_inertia_props()

        self.assertIsNone(props["auth"])
        self.assertEqual(props["role"], "guest")
        self.assertFalse(props["is_admin"])
        self.assertIn("csrfToken", props)
        self.assertTrue(props["csrfToken"])
        self.assertIsNone(props["flash"])

    def test_authenticated_user_inertia_props_include_shared_auth_state(
        self,
    ) -> None:
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="secret123",
            role="partner",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["auth"]["id"], user.id)
        self.assertEqual(props["auth"]["email"], user.email)
        self.assertEqual(props["auth"]["role"], "partner")
        self.assertEqual(props["role"], "partner")
        self.assertFalse(props["is_admin"])
        self.assertIn("csrfToken", props)

    def test_admin_user_shared_props(self) -> None:
        user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="secret123",
            role="admin",
            is_staff=True,
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "admin")
        self.assertEqual(props["auth"]["role"], "admin")
        self.assertTrue(props["is_admin"])

    def test_channel_moderator_user_shared_props(self) -> None:
        user = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="secret123",
            role="channel_moderator",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "channel_moderator")
        self.assertEqual(props["auth"]["role"], "channel_moderator")
        self.assertFalse(props["is_admin"])

    def test_flash_message_persists_after_redirect(self) -> None:
        session = self.client.session
        session["flash"] = {"success": "Пользователь успешно зарегистрирован"}
        session.save()

        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        props = response.json()["props"]

        self.assertEqual(
            props["flash"], {"success": "Пользователь успешно зарегистрирован"}
        )

        # Flash должен быть извлечён из сессии однократно
        self.assertIsNone(self.client.session.get("flash"))

    def test_flash_survives_chain_of_redirects(self) -> None:
        """Flash не теряется на промежуточном редиректе."""
        user = User.objects.create_user(
            username="redirectuser",
            email="redirect@example.com",
            password="secret123",
            role="user",
        )
        self.client.force_login(user)
        session = self.client.session
        session["flash"] = {"success": "Сообщение через redirect"}
        session.save()

        # /home перенаправляет авторизованных на /dashboard
        response = self.client.get(
            reverse("main_index"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        final_url = response.redirect_chain[-1][0]
        self.assertIn("dashboard", final_url)

        props = response.json()["props"]
        self.assertEqual(
            props["flash"], {"success": "Сообщение через redirect"}
        )

    def test_unknown_role_fallback_to_user(self) -> None:
        user = User.objects.create_user(
            username="unknownrole",
            email="unknown@example.com",
            password="secret123",
            role="something_weird",
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "user")
        self.assertEqual(props["auth"]["role"], "user")
        self.assertFalse(props["is_admin"])

    def test_is_admin_true_for_superuser(self) -> None:
        user = User.objects.create_user(
            username="superuser",
            email="super@example.com",
            password="secret123",
            role="user",
            is_superuser=True,
        )
        self.client.force_login(user)

        props = self._get_inertia_props("homepage:dashboard")

        self.assertEqual(props["role"], "user")
        self.assertTrue(props["is_admin"])

    def test_invalid_flash_values_normalized_to_none(self) -> None:
        for invalid_flash in ["", "plain string", {}, []]:
            with self.subTest(flash=invalid_flash):
                session = self.client.session
                session["flash"] = invalid_flash
                session.save()

                props = self._get_inertia_props()
                self.assertIsNone(props["flash"])
                self.assertIsNone(self.client.session.get("flash"))

    def test_registration_flash_survives_redirect_chain(self) -> None:
        """Регистрация устанавливает flash и редиректит на главную."""
        response = self.client.post(
            reverse("users:user_create"),
            data={
                "first_name": "Test",
                "last_name": "User",
                "username": "testregister",
                "password1": "ComplexPass123!",
                "password2": "ComplexPass123!",
                "email": "testregister@example.com",
                "bio": "",
                "avatar_image": "",
                "terms": "on",
            },
            follow=True,
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)

        props = response.json()["props"]
        self.assertEqual(
            props["flash"], {"success": "Пользователь успешно зарегистрирован"}
        )
        self.assertTrue(User.objects.filter(username="testregister").exists())


class DashboardSubscriptionTest(TestCase):
    def _get_dashboard_stats(self) -> dict[str, Any]:
        response = self.client.get(
            reverse("homepage:dashboard"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]["stats"]

    def test_days_left_zero_for_default_free_subscription(self) -> None:
        user = User.objects.create_user(
            username="free",
            email="free@example.com",
            password="secret123",
            role="user",
        )
        self.client.force_login(user)

        stats = self._get_dashboard_stats()

        self.assertEqual(stats["days_left"], 0)

    def test_days_left_comes_from_active_subscription(self) -> None:
        user = User.objects.create_user(
            username="pro",
            email="pro@example.com",
            password="secret123",
            role="user",
        )
        subscription = Subscription.objects.get(user=user)
        subscription.plan = Plan.objects.get(code=Plan.Code.PRO)
        subscription.current_period_end = timezone.now() + timedelta(days=7)
        subscription.save()
        self.client.force_login(user)

        stats = self._get_dashboard_stats()

        self.assertEqual(stats["days_left"], 7)


class DashboardPagePropsTest(TestCase):
    def _login(self, username: str = "dashuser") -> User:
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="secret123",
            role="user",
        )
        self.client.force_login(user)
        return user

    def _create_channel(
        self,
        user: User,
        *,
        username: str = "db_channel",
        with_stats: bool = True,
        with_posts: bool = True,
    ) -> TelegramChannel:
        channel = TelegramChannel.objects.create(
            channel_id=777,
            username=username,
            title="DB Channel",
            participants_count=1000,
            average_views=200,
            citation_index=8.3,
            category="Технологии",
            country="Россия",
            is_public=True,
            is_verified=True,
        )
        ChannelModerator.objects.create(user=user, channel=channel)
        now = timezone.now()
        if with_stats:
            for days_ago, participants in ((30, 800), (0, 1000)):
                stat = ChannelStats.objects.create(
                    channel=channel,
                    participants_count=participants,
                    daily_growth=0,
                )
                ChannelStats.objects.filter(pk=stat.pk).update(
                    parsed_at=now - timedelta(days=days_ago)
                )
        if with_posts:
            post = Post.objects.create(
                channel=channel,
                telegram_message_id=1,
                text="Пост из БД",
                published_at=now,
                views=1000,
                forwards=10,
                comments_count=5,
            )
            PostReaction.objects.create(post=post, emoji="🔥", count=3)
        return channel

    def _get_props(self) -> dict[str, Any]:
        response = self.client.get(
            reverse("homepage:dashboard"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["props"]

    def test_dashboard_without_db_data_returns_empty_props(self) -> None:
        self._login()

        props = self._get_props()

        self.assertEqual(props["channel"], {})
        self.assertEqual(props["kpis"], [])
        self.assertEqual(props["growthData"], [])
        self.assertEqual(props["posts"], [])

    def test_public_channel_is_not_used_as_dashboard_fallback(self) -> None:
        self._login()
        TelegramChannel.objects.create(
            channel_id=999,
            username="unrelated_public",
            title="Unrelated Public",
            participants_count=5000,
            is_public=True,
        )

        props = self._get_props()

        self.assertEqual(props["channel"], {})
        self.assertEqual(props["kpis"], [])
        self.assertEqual(props["growthData"], [])
        self.assertEqual(props["posts"], [])

    def test_dashboard_channel_without_stats_or_posts(self) -> None:
        user = self._login()
        self._create_channel(user, with_stats=False, with_posts=False)

        props = self._get_props()

        channel = props["channel"]
        self.assertEqual(channel["name"], "DB Channel")
        self.assertEqual(channel["subscribers"], 1000)
        self.assertEqual(channel["type"], "channel")
        self.assertEqual(channel["imageUrl"], "")
        self.assertEqual(channel["growth30d"], 0.0)

        kpis = {kpi["label"]: kpi for kpi in props["kpis"]}
        self.assertEqual(kpis["Подписчики"]["value"], 1000)
        self.assertEqual(kpis["Подписчики"]["delta"], 0)
        self.assertEqual(kpis["Ср. охват"]["value"], 200)
        self.assertEqual(
            kpis["Ср. охват"]["percentDelta"],
            MOCK_KPIS[1]["percentDelta"],
        )
        self.assertEqual(kpis["ER"]["value"], 0.0)
        self.assertEqual(
            kpis["ER"]["percentDelta"],
            MOCK_KPIS[2]["percentDelta"],
        )
        self.assertEqual(kpis["Индекс цитирования"]["value"], 8)
        self.assertEqual(
            kpis["Индекс цитирования"]["delta"],
            MOCK_KPIS[3]["delta"],
        )

        self.assertEqual(props["growthData"], [])
        self.assertEqual(props["posts"], [])

    def test_dashboard_uses_mock_channel_fields(self) -> None:
        user = self._login()
        self._create_channel(
            user,
            username="marketinghub",
            with_stats=False,
            with_posts=False,
        )

        props = self._get_props()

        self.assertEqual(props["channel"]["type"], "group")
        self.assertEqual(props["channel"]["imageUrl"], "")

    def test_dashboard_uses_db_growth_and_posts(self) -> None:
        user = self._login()
        self._create_channel(user)

        props = self._get_props()

        kpis = {kpi["label"]: kpi for kpi in props["kpis"]}
        self.assertEqual(kpis["Подписчики"]["value"], 1000)
        self.assertEqual(kpis["Подписчики"]["delta"], 200)
        self.assertEqual(kpis["Ср. охват"]["value"], 200)
        self.assertEqual(kpis["ER"]["value"], 1.8)
        self.assertEqual(props["growthData"][-1]["подписчики"], 1000)
        self.assertEqual(props["posts"][0]["views"], 1000)
        self.assertEqual(props["posts"][0]["reactions"], 3)

    def test_dashboard_keeps_real_dto_props(self) -> None:
        self._login()
        props = self._get_props()

        self.assertIn("stats", props)
        self.assertIn("ai_insights", props)
        self.assertGreaterEqual(len(props["ai_insights"]), 1)
        self.assertIn("quick_actions", props)

    def test_dashboard_requires_auth(self) -> None:
        response = self.client.get(
            reverse("homepage:dashboard"),
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 302)
