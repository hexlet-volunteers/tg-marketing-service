from typing import Any

from django.apps import apps
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.db.models.signals import post_migrate
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from guardian.management import create_anonymous_user

from apps.users.forms import UserUpdateForm
from apps.users.models import User


class EmailUniquenessTest(TestCase):
    owner: User
    other: User

    @classmethod
    def setUpTestData(cls) -> None:
        cls.owner = User.objects.create_user(
            username="email-owner",
            email="owner@example.com",
            password="EmailOwner-Strong-Password-42!",
            role="user",
            first_name="Owner",
            last_name="User",
        )
        cls.other = User.objects.create_user(
            username="email-other",
            email="other@example.com",
            password="EmailOther-Strong-Password-73!",
            role="user",
            first_name="Other",
            last_name="User",
        )

    def setUp(self) -> None:
        self.client = Client(HTTP_X_INERTIA="true")

    def profile_data(self, email: str) -> dict[str, str]:
        return {"first_name": "Other", "last_name": "User", "email": email}

    def test_form_rejects_other_users_email_in_any_case(self) -> None:
        for email in ("owner@example.com", " OWNER@EXAMPLE.COM "):
            with self.subTest(email=email):
                form = UserUpdateForm(
                    data=self.profile_data(email), instance=self.other
                )
                self.assertFalse(form.is_valid())
                self.assertIn("email", form.errors)
                self.other.refresh_from_db()
                self.assertEqual(self.other.email, "other@example.com")

    def test_form_allows_own_email_with_different_case(self) -> None:
        form = UserUpdateForm(
            data=self.profile_data(" OTHER@EXAMPLE.COM "), instance=self.other
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.other.refresh_from_db()
        self.assertEqual(self.other.email, "other@example.com")

    def test_form_normalizes_new_email(self) -> None:
        form = UserUpdateForm(
            data=self.profile_data(" New@Example.COM "), instance=self.other
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.other.refresh_from_db()
        self.assertEqual(self.other.email, "new@example.com")

    def test_both_profile_routes_reject_case_insensitive_duplicate(
        self,
    ) -> None:
        self.client.force_login(self.other)
        urls = (
            (reverse("users:user_cabinet"), "Profile"),
            (
                reverse(
                    "users:user_update",
                    kwargs={"username": self.other.username},
                ),
                "UpdateUserProfile",
            ),
        )
        original_password = self.other.password
        for url, component in urls:
            with self.subTest(url=url):
                response = self.client.post(
                    url,
                    data=self.profile_data("OWNER@EXAMPLE.COM"),
                    HTTP_X_INERTIA="true",
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["component"], component)
                self.assertIn("email", response.json()["props"]["errors"])
                self.other.refresh_from_db()
                self.assertEqual(self.other.email, "other@example.com")
                self.assertEqual(self.other.password, original_password)

        self.client.logout()
        for user, password in (
            (self.owner, "EmailOwner-Strong-Password-42!"),
            (self.other, "EmailOther-Strong-Password-73!"),
        ):
            with self.subTest(user=user.pk):
                response = self.client.post(
                    reverse("users:login"),
                    {"email": user.email.upper(), "password": password},
                )
                self.assertRedirects(
                    response,
                    reverse("homepage:dashboard"),
                    fetch_redirect_response=False,
                )
                self.assertEqual(
                    int(self.client.session["_auth_user_id"]), user.pk
                )
                self.client.logout()

    def test_database_rejects_duplicate_insert_without_form_validation(
        self,
    ) -> None:
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(
                username="duplicate-email",
                email="OWNER@EXAMPLE.COM",
                role="user",
            )
        self.assertFalse(
            User.objects.filter(username="duplicate-email").exists()
        )
        self.assertEqual(
            User.objects.filter(email__iexact=self.owner.email).count(), 1
        )

    def test_database_rejects_duplicate_update_without_form_validation(
        self,
    ) -> None:
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.filter(pk=self.other.pk).update(
                email="OWNER@EXAMPLE.COM"
            )
        self.other.refresh_from_db()
        self.assertEqual(self.other.email, "other@example.com")

    def test_database_allows_different_case_for_the_same_user(self) -> None:
        User.objects.filter(pk=self.owner.pk).update(email="OWNER@EXAMPLE.COM")
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.email, "OWNER@EXAMPLE.COM")
        self.assertEqual(
            User.objects.get(email__iexact="owner@example.com").pk,
            self.owner.pk,
        )


class EmailUniquenessMigrationTest(TransactionTestCase):
    migrate_from = [("users", "0010_subject_request_workflow")]
    migrate_to = [("users", "0011_user_email_ci_unique")]

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
        self.old_user: Any = executor.loader.project_state(
            self.migrate_from
        ).apps.get_model("users", "User")

    def tearDown(self) -> None:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_migration_preserves_existing_accounts_and_enforces_constraint(
        self,
    ) -> None:
        user = self.old_user.objects.create(
            username="legacy-email",
            email="Legacy@Example.COM",
            password="legacy-password-hash",
            role="user",
        )
        MigrationExecutor(connection).migrate(self.migrate_to)
        migrated = User.objects.get(pk=user.pk)
        self.assertEqual(migrated.email, "Legacy@Example.COM")
        self.assertEqual(migrated.password, "legacy-password-hash")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create(
                username="legacy-duplicate", email="LEGACY@example.com"
            )

    def test_migration_reports_duplicates_without_changing_accounts(
        self,
    ) -> None:
        first = self.old_user.objects.create(
            username="legacy-first", email="duplicate@example.com", role="user"
        )
        second = self.old_user.objects.create(
            username="legacy-second", email="DUPLICATE@example.com", role="user"
        )
        try:
            with self.assertRaises(RuntimeError) as raised:
                MigrationExecutor(connection).migrate(self.migrate_to)
            message = str(raised.exception)
            self.assertIn("users_email_ci_unique", message)
            self.assertIn(str(first.pk), message)
            self.assertIn(str(second.pk), message)
            self.assertNotIn("duplicate@example.com", message.lower())
            first.refresh_from_db()
            second.refresh_from_db()
            self.assertEqual(first.email, "duplicate@example.com")
            self.assertEqual(second.email, "DUPLICATE@example.com")
        finally:
            second.delete()

    def test_migration_can_be_reversed_without_changing_email(self) -> None:
        user = self.old_user.objects.create(
            username="legacy-reverse", email="Reverse@Example.COM", role="user"
        )
        MigrationExecutor(connection).migrate(self.migrate_to)
        MigrationExecutor(connection).migrate(self.migrate_from)
        user.refresh_from_db()
        self.assertEqual(user.email, "Reverse@Example.COM")
