from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from apps.billing.models import Plan, Subscription
from apps.users.demo.base import BaseSeedStep
from apps.users.demo.context import DemoSeedContext
from apps.users.models import NotificationSettings, PartnerProfile, User
from apps.users.roles import Role, UserRoleHistory
from mocks import users as users_mocks


class RolesStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        Role._default_manager.bulk_create(
            [
                Role(code=code, name=name)
                for code, name in users_mocks.ROLE_LABELS.items()
            ],
            ignore_conflicts=True,
        )


class UsersStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        users: dict[str, User] = {}
        role_codes = {
            "demo_admin": "user",
            "demo_partner": "partner",
            "demo_moderator": "channel_moderator",
        }
        roles = {
            role.code: role
            for role in Role._default_manager.filter(
                code__in=set(role_codes.values())
            )
        }
        role_histories: list[UserRoleHistory] = []
        notification_settings: list[NotificationSettings] = []

        for username in users_mocks.DEMO_USERNAMES:
            defaults = {
                "email": f"{username}@demo.test",
                "role": "user",
                "is_active": True,
                "first_name": username.replace("demo_", "").capitalize(),
                "last_name": "Demo",
            }
            user, _ = User.objects.update_or_create(
                username=username, defaults=defaults
            )
            user.set_password(users_mocks.DEMO_PASSWORD)
            user.is_staff = username == "demo_admin"
            user.is_superuser = username == "demo_admin"
            user.save()
            users[username] = user

            role = roles.get(role_codes.get(username, "user"))
            if role is not None:
                role_histories.append(
                    UserRoleHistory(
                        user=user,
                        role=role,
                        reason="demo_seed",
                    )
                )
            notification_settings.append(NotificationSettings(user=user))
            if username == "demo_partner":
                PartnerProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        "status": "active",
                        "balance": Decimal("12500.00"),
                        "payment_details": "demo@example.com",
                    },
                )

        UserRoleHistory.objects.bulk_create(
            role_histories, ignore_conflicts=True
        )
        NotificationSettings.objects.bulk_create(
            notification_settings, ignore_conflicts=True
        )
        ctx.users = users

    def summary(self, ctx: DemoSeedContext) -> str | None:
        count = User.objects.filter(
            username__in=users_mocks.DEMO_USERNAMES
        ).count()
        return f"Пользователи: {count}"


class SubscriptionsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        plans = {plan.code: plan for plan in Plan.objects.all()}
        now = ctx.now
        subscriptions = {
            "demo_user": (
                "Free",
                Subscription.BillingPeriod.MONTHLY,
                None,
            ),
            "demo_partner": (
                "Pro",
                Subscription.BillingPeriod.ANNUAL,
                now + timedelta(days=365),
            ),
            "demo_moderator": (
                "Pro",
                Subscription.BillingPeriod.MONTHLY,
                now + timedelta(days=30),
            ),
            "demo_admin": (
                "Agency",
                Subscription.BillingPeriod.ANNUAL,
                now + timedelta(days=365),
            ),
        }
        for username, (code, period, period_end) in subscriptions.items():
            user = ctx.users.get(username)
            plan = plans.get(code)
            if user is None or plan is None:
                continue
            Subscription.objects.update_or_create(
                user=user,
                defaults={
                    "plan": plan,
                    "status": Subscription.Status.ACTIVE,
                    "billing_period": period,
                    "started_at": now,
                    "current_period_end": period_end,
                },
            )

    def summary(self, ctx: DemoSeedContext) -> str | None:
        return f"Тарифы: {Plan.objects.count()}"
