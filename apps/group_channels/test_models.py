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

        self.assertEqual(self.group.saves_count, 1)
        self.assertEqual(self.group.saves.first(), save)
        self.assertEqual(self.user.saved_collections.first(), save)
