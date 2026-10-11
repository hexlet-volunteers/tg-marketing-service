from django.test import TestCase
from django.urls import reverse

from apps.group_channels.models import Group
from apps.group_channels.views import DEFAULT_AVATAR_GROUP
from apps.users.models import User


class CreateGroupViewTest(TestCase):
    def test_owner_creates_group_and_receives_inertia_response(self) -> None:
        user = User.objects.create_user(
            username="group-owner", email="owner@example.com", role="user"
        )
        self.client.force_login(user)
        url = reverse("group_channels:group_create")

        response = self.client.post(
            url,
            {"name": "My collection", "description": "Selected channels"},
            HTTP_ACCEPT="application/json",
            HTTP_X_INERTIA="true",
        )

        self.assertEqual(response.status_code, 200)
        group = Group.objects.get()
        self.assertEqual(group.owner, user)
        self.assertEqual(group.name, "My collection")
        self.assertEqual(group.description, "Selected channels")
        self.assertEqual(group.image_url, DEFAULT_AVATAR_GROUP)
        data = response.json()
        self.assertEqual(data["component"], "Channels")
        self.assertEqual(data["url"], url)
        self.assertEqual(data["props"]["group"], {"name": group.name})
        self.assertTrue(data["props"]["flash"]["success"])
