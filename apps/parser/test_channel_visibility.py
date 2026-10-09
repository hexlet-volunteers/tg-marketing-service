from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from apps.admin.moderation.models import ModerationRequest
from apps.parser.models import TelegramChannel


class ChannelVisibilityTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="visibility_test_user",
            email="visibility_test_user@example.com",
            password="test-password",
        )

        self.unmoderated_channel = self.create_channel(
            1001,
            "Unmoderated channel",
            "unmoderated_channel",
        )
        self.pending_channel = self.create_channel(
            1002,
            "Pending channel",
            "pending_channel",
        )
        self.rejected_channel = self.create_channel(
            1003,
            "Rejected channel",
            "rejected_channel",
        )

        self.pending_channel.is_public = False
        self.pending_channel.save(update_fields=["is_public"])

        self.rejected_channel.is_public = False
        self.rejected_channel.save(update_fields=["is_public"])

        self.approved_channel = self.create_channel(
            1004,
            "Approved channel",
            "approved_channel",
        )

        self.create_moderation_request(self.pending_channel, "pending")
        self.create_moderation_request(self.rejected_channel, "rejected")
        self.create_moderation_request(self.approved_channel, "approved")

    def create_channel(self, channel_id, title, username):
        return TelegramChannel.objects.create(
            channel_id=channel_id,
            title=title,
            username=username,
        )

    def create_moderation_request(self, channel, status):
        return ModerationRequest.objects.create(
            submitted_by=self.user,
            channel_identifier=channel.username,
            channel_by=channel,
            category="test",
            country="test",
            language="test",
            status=status,
        )

    def test_catalogue_shows_only_public_channels(self):
        from apps.parser.views import ParserListView

        visible_ids = set(
            ParserListView()
            .get_queryset()
            .values_list("channel_id", flat=True)
        )

        self.assertEqual(
            visible_ids,
            {
                self.unmoderated_channel.channel_id,
                self.approved_channel.channel_id,
            },
        )

    def test_search_shows_only_public_channels(self):
        response = self.client.get(
            reverse("parser:channel_lookup"),
            {"q": "channel"},
        )

        self.assertEqual(response.status_code, 200)

        visible_usernames = {
            channel["username"] for channel in response.json()
        }

        self.assertEqual(
            visible_usernames,
            {"unmoderated_channel", "approved_channel"},
        )


    def test_new_channel_without_moderation_request_is_hidden(self):
        channel = self.create_channel(
            1005,
            "Failed parsing channel",
            "failed_parsing_channel",
        )
        channel.is_public = False
        channel.save(update_fields=["is_public"])

        from apps.parser.views import ParserListView

        visible_ids = set(
            ParserListView()
            .get_queryset()
            .values_list("channel_id", flat=True)
        )

        self.assertNotIn(channel.channel_id, visible_ids)
        self.assertIn(
            self.unmoderated_channel.channel_id,
            visible_ids,
        )
