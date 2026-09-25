from datetime import timedelta
from decimal import Decimal

from django.contrib import admin
from django.test import TestCase
from django.utils import timezone

from apps.billing.models import Plan, Subscription
from apps.billing.services.subscription_service import (
    get_subscription,
    serialize_subscription,
)
from apps.parser.models import AIInsight, ChannelModerator, TelegramChannel
from apps.users.models import User


class SubscriptionModelTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="freeuser",
            email="free@example.com",
            password="StrongPass12345!",
            role="user",
        )

    def test_new_user_gets_free_subscription(self) -> None:
        subscription = self.user.subscription

        self.assertEqual(subscription.plan.code, Plan.Code.FREE)
        self.assertEqual(subscription.status, Subscription.Status.ACTIVE)
        self.assertEqual(
            subscription.billing_period,
            Subscription.BillingPeriod.MONTHLY,
        )
        self.assertFalse(subscription.is_auto_renew)

    def test_get_subscription_creates_free_when_missing(self) -> None:
        Subscription.objects.filter(user=self.user).delete()

        subscription = get_subscription(self.user)

        self.assertEqual(subscription.plan.code, Plan.Code.FREE)
        self.assertEqual(Subscription.objects.filter(user=self.user).count(), 1)

    def test_days_left_is_zero_without_period_end(self) -> None:
        subscription = self.user.subscription

        self.assertIsNone(subscription.current_period_end)
        self.assertEqual(subscription.days_left, 0)

    def test_days_left_counts_remaining_days(self) -> None:
        subscription = self.user.subscription
        subscription.current_period_end = timezone.now() + timedelta(
            days=10, hours=1
        )
        subscription.save()

        self.assertEqual(subscription.days_left, 11)

    def test_days_left_is_zero_for_inactive_subscription(self) -> None:
        subscription = self.user.subscription
        subscription.status = Subscription.Status.EXPIRED
        subscription.current_period_end = timezone.now() + timedelta(days=5)
        subscription.save()

        self.assertEqual(subscription.days_left, 0)

    def test_days_left_is_zero_when_period_already_ended(self) -> None:
        subscription = self.user.subscription
        subscription.current_period_end = timezone.now() - timedelta(days=1)
        subscription.save()

        self.assertEqual(subscription.days_left, 0)

    def test_channels_used_counts_moderated_channels(self) -> None:
        channel = TelegramChannel.objects.create(
            channel_id=1,
            title="Channel",
        )
        ChannelModerator.objects.create(
            user=self.user,
            channel=channel,
            is_owner=True,
        )

        self.assertEqual(self.user.subscription.channels_used, 1)

    def test_ai_requests_used_counts_insights(self) -> None:
        AIInsight.objects.create(
            user=self.user,
            insight_text="Текст",
            insight_type="trend",
        )

        self.assertEqual(self.user.subscription.ai_requests_used, 1)

    def test_superuser_also_gets_free_subscription(self) -> None:
        superuser = User.objects.create_superuser(
            username="root",
            email="root@example.com",
            password="StrongPass12345!",
        )

        self.assertEqual(superuser.subscription.plan.code, Plan.Code.FREE)

    def test_subscription_is_registered_in_admin(self) -> None:
        self.assertTrue(admin.site.is_registered(Subscription))


class SubscriptionSerializerTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="pro",
            email="pro@example.com",
            password="StrongPass12345!",
            role="user",
        )
        self.pro_plan = Plan.objects.get(code=Plan.Code.PRO)

    def test_serializer_returns_expected_contract(self) -> None:
        subscription = self.user.subscription
        subscription.plan = self.pro_plan
        subscription.save()

        data = serialize_subscription(subscription)

        self.assertEqual(data["plan"], Plan.Code.PRO)
        self.assertEqual(data["period"], Subscription.BillingPeriod.MONTHLY)
        self.assertEqual(Decimal(data["price"]), self.pro_plan.monthly_price)
        self.assertIsNone(data["current_period_end"])
        self.assertEqual(
            data["limits"],
            {
                "channels": self.pro_plan.channels_limit,
                "ai_requests": self.pro_plan.ai_requests_limit,
            },
        )
        self.assertEqual(data["days_left"], 0)
        self.assertEqual(data["channels_used"], 0)
        self.assertEqual(data["ai_requests_used"], 0)

    def test_serializer_uses_annual_price_for_annual_period(self) -> None:
        subscription = self.user.subscription
        subscription.plan = self.pro_plan
        subscription.billing_period = Subscription.BillingPeriod.ANNUAL
        subscription.save()

        data = serialize_subscription(subscription)

        self.assertEqual(data["period"], Subscription.BillingPeriod.ANNUAL)
        self.assertEqual(Decimal(data["price"]), self.pro_plan.annual_price)

    def test_free_price_is_zero_rubles(self) -> None:
        data = serialize_subscription(self.user.subscription)

        self.assertEqual(Decimal(data["price"]), Decimal("0.00"))
