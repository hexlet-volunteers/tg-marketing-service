from typing import Any

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

MIGRATE_FROM = [("users", "0014_seed_admin_role")]
MIGRATE_TO = [("users", "0015_rename_moderated_channels_role")]


class RenameModeratedChannelsRoleMigrationTest(TransactionTestCase):
    """0015: moderated_channels → channel_moderator."""

    def _fixture_teardown(self) -> None:
        # Не эмитим post_migrate при flush: иначе guardian создаёт
        # AnonymousUser, срабатывает billing-сигнал и падает на пустом Plan.
        for db_name in self._databases_names(  # type: ignore[attr-defined]
            include_mirrors=False
        ):
            call_command(
                "flush",
                verbosity=0,
                interactive=False,
                database=db_name,
                reset_sequences=False,
                allow_cascade=True,
                inhibit_post_migrate=True,
            )

    def _migrate(self, targets: list[tuple[str, str]]) -> Any:
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def test_only_old_role_is_renamed_in_place(self) -> None:
        """Основная ветка: в базе только moderated_channels."""
        old_apps = self._migrate(MIGRATE_FROM)
        role_model = old_apps.get_model("users", "Role")
        user_model = old_apps.get_model("users", "User")

        old_role = role_model.objects.create(
            code="moderated_channels", name="Старая"
        )
        user = user_model.objects.create(
            username="m1",
            email="m1@example.com",
            role="moderated_channels",
        )

        new_apps = self._migrate(MIGRATE_TO)
        new_role_model = new_apps.get_model("users", "Role")
        new_user_model = new_apps.get_model("users", "User")

        renamed = new_role_model.objects.get(pk=old_role.pk)
        self.assertEqual(renamed.code, "channel_moderator")
        self.assertFalse(
            new_role_model.objects.filter(code="moderated_channels").exists()
        )
        self.assertEqual(
            new_user_model.objects.get(pk=user.pk).role,
            "channel_moderator",
        )

    def test_merge_when_both_roles_exist(self) -> None:
        old_apps = self._migrate(MIGRATE_FROM)
        role_model = old_apps.get_model("users", "Role")
        user_model = old_apps.get_model("users", "User")
        history_model = old_apps.get_model("users", "UserRoleHistory")

        old_role = role_model.objects.create(
            code="moderated_channels", name="Старая"
        )
        new_role = role_model.objects.create(
            code="channel_moderator", name="Новая"
        )
        user = user_model.objects.create(
            username="m2",
            email="m2@example.com",
            role="moderated_channels",
        )
        history_model.objects.create(user=user, role=old_role)

        new_apps = self._migrate(MIGRATE_TO)
        new_role_model = new_apps.get_model("users", "Role")
        new_user_model = new_apps.get_model("users", "User")
        new_history_model = new_apps.get_model("users", "UserRoleHistory")

        self.assertFalse(
            new_role_model.objects.filter(code="moderated_channels").exists()
        )
        self.assertEqual(
            new_role_model.objects.filter(code="channel_moderator").count(),
            1,
        )
        self.assertEqual(
            new_user_model.objects.get(pk=user.pk).role,
            "channel_moderator",
        )
        self.assertTrue(
            new_history_model.objects.filter(
                user_id=user.pk, role_id=new_role.pk
            ).exists()
        )

    def test_merge_closes_conflicting_active_history(self) -> None:
        """Если активны обе роли — не падаем на unique_current_role_per_user."""
        old_apps = self._migrate(MIGRATE_FROM)
        role_model = old_apps.get_model("users", "Role")
        user_model = old_apps.get_model("users", "User")
        history_model = old_apps.get_model("users", "UserRoleHistory")

        old_role = role_model.objects.create(
            code="moderated_channels", name="Старая"
        )
        new_role = role_model.objects.create(
            code="channel_moderator", name="Новая"
        )
        user = user_model.objects.create(
            username="m3",
            email="m3@example.com",
            role="moderated_channels",
        )
        history_model.objects.create(user=user, role=old_role)
        history_model.objects.create(user=user, role=new_role)

        new_apps = self._migrate(MIGRATE_TO)
        new_history_model = new_apps.get_model("users", "UserRoleHistory")

        active = new_history_model.objects.filter(
            user_id=user.pk, end_date__isnull=True
        )
        self.assertEqual(active.count(), 1)

    def test_creates_target_role_when_absent(self) -> None:
        """Ни старого, ни нового кода — создаём channel_moderator."""
        self._migrate(MIGRATE_FROM)
        new_apps = self._migrate(MIGRATE_TO)
        new_role_model = new_apps.get_model("users", "Role")
        self.assertTrue(
            new_role_model.objects.filter(code="channel_moderator").exists()
        )
