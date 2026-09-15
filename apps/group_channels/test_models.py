from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.group_channels.models import Group, SavedCollection
from apps.users.models import User


class SavedCollectionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ivan",
            email="ivan@test.ru",
            password="123",
            role="user",
        )
        self.group = Group.objects.create(
            name="Игры",
            owner=self.user,
        )

    def test_save_group(self):
        save = SavedCollection.objects.create(
            user=self.user,
            group=self.group,
        )

        self.group.saves_count = self.group.saves.count()
        self.group.save(update_fields=["saves_count"])

        self.assertEqual(self.group.saves_count, 1)
        self.assertEqual(self.group.saves.first(), save)
        self.assertEqual(self.user.saved_collections.first(), save)

    def test_cant_save_group_twice(self):
        SavedCollection.objects.create(
            user=self.user,
            group=self.group,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SavedCollection.objects.create(
                    user=self.user,
                    group=self.group,
                )
