from typing import Any

from django.apps import apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db.models.signals import post_migrate
from django.test import TransactionTestCase
from guardian.management import create_anonymous_user

from apps.users.test_url_validator import INVALID_IMAGE_URLS, VALID_IMAGE_URLS
from apps.users.validators import validate_http_url


class ImageURLMigrationTest(TransactionTestCase):
    migrate_from = [
        ("users", "0012_merge_email_uniqueness_notifications"),
        (
            "group_channels",
            "0004_group_curator_group_saves_count_group_views_count",
        ),
    ]
    migrate_to = [
        ("users", "0013_validate_avatar_urls"),
        ("group_channels", "0005_validate_image_urls"),
    ]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        guardian_app = apps.get_app_config("guardian")
        dispatch_uid = "guardian.management.create_anonymous_user"
        if post_migrate.disconnect(
            sender=guardian_app, dispatch_uid=dispatch_uid
        ):
            cls.addClassCleanup(
                post_migrate.connect,
                create_anonymous_user,
                sender=guardian_app,
                dispatch_uid=dispatch_uid,
            )

    def setUp(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        self.old_user: Any = old_apps.get_model("users", "User")
        self.old_group: Any = old_apps.get_model("group_channels", "Group")

    def tearDown(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_migrations_clear_invalid_urls_and_preserve_valid_data(
        self,
    ) -> None:
        users = []
        groups = []
        urls = (*INVALID_IMAGE_URLS, *VALID_IMAGE_URLS, "")
        for index, url in enumerate(urls):
            user = self.old_user.objects.create(
                username=f"legacy-url-{index}",
                email=f"legacy-url-{index}@example.com",
                password="unchanged-password-hash",
                role="user",
                avatar_image=url,
            )
            users.append(user)
            groups.append(
                self.old_group.objects.create(
                    name=f"Legacy collection {index}",
                    slug=f"legacy-{index}",
                    owner_id=user.pk,
                    image_url=url,
                )
            )
        null_user = self.old_user.objects.create(
            username="legacy-null",
            email="legacy-null@example.com",
            avatar_image=None,
        )

        MigrationExecutor(connection).migrate(self.migrate_to)

        for url, user, group in zip(urls, users, groups, strict=True):
            with self.subTest(url=url):
                expected = "" if url in INVALID_IMAGE_URLS else url
                user.refresh_from_db()
                group.refresh_from_db()
                self.assertEqual(user.avatar_image, expected)
                self.assertEqual(group.image_url, expected)
                self.assertEqual(user.password, "unchanged-password-hash")
                self.assertEqual(group.owner_id, user.pk)
                self.assertEqual(user.role, "user")
                if expected:
                    validate_http_url(expected)
        null_user.refresh_from_db()
        self.assertIsNone(null_user.avatar_image)

        MigrationExecutor(connection).migrate(self.migrate_from)
        MigrationExecutor(connection).migrate(self.migrate_to)
        for url, user, group in zip(urls, users, groups, strict=True):
            user.refresh_from_db()
            group.refresh_from_db()
            expected = "" if url in INVALID_IMAGE_URLS else url
            self.assertEqual(user.avatar_image, expected)
            self.assertEqual(group.image_url, expected)
