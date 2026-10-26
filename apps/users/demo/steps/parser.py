from __future__ import annotations

from datetime import timedelta
from typing import Any

from apps.parser.models import (
    AIInsight,
    ChannelModerator,
    ChannelStats,
    Post,
    PostAnalysis,
    PostReaction,
    TelegramChannel,
)
from apps.users.demo.base import BaseSeedStep
from apps.users.demo.constants import (
    DEFAULT_POSTS_PER_CHANNEL,
    DEFAULT_STATS_DAYS,
    DEMO_CHANNEL_ID_MIN,
)
from apps.users.demo.context import DemoSeedContext
from mocks import ai as ai_mocks
from mocks import landing as landing_mocks
from mocks import parser as parser_mocks
from mocks import users as users_mocks


class ChannelsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        channels: list[TelegramChannel] = []

        for index, data in enumerate(parser_mocks.MOCK_CHANNELS):
            channel_id = DEMO_CHANNEL_ID_MIN + index + 1
            title = data.get("name") or f"Demo Channel {index}"
            username = (data.get("username") or "").lstrip(
                "@"
            ) or f"demo_channel_{index}"
            subscribers = int(data.get("subscribers", 15000))
            defaults = {
                "username": username,
                "title": title,
                "description": f"Демонстрационный канал {title}",
                "participants_count": subscribers,
                "category": data.get("category") or "IT",
                "country": data.get("country") or "Россия",
                "language": "ru",
                "is_public": True,
                "is_verified": bool(data.get("verified")),
                "average_views": max(int(subscribers * 0.3), 1000),
                "citation_index": float(data.get("er", 5.0)),
            }
            channel, _ = TelegramChannel.objects.update_or_create(
                channel_id=channel_id, defaults=defaults
            )
            channels.append(channel)

        ctx.channels = channels

    def summary(self, ctx: DemoSeedContext) -> str | None:
        count = TelegramChannel.objects.filter(
            channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).count()
        return f"Каналы: {count}"


class ModeratorsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        assignments = {
            "demo_user": ctx.channels,
            "demo_admin": ctx.channels,
            "demo_partner": ctx.channels[:3],
            "demo_moderator": ctx.channels[:2],
        }
        moderators: list[ChannelModerator] = []
        for username, user_channels in assignments.items():
            user = ctx.users.get(username)
            if user is None:
                continue
            is_owner = username == "demo_admin"
            moderators.extend(
                ChannelModerator(
                    user=user,
                    channel=channel,
                    is_owner=is_owner,
                    can_edit=True,
                    can_delete=is_owner,
                    can_manage_moderators=is_owner,
                )
                for channel in user_channels
            )

        ChannelModerator.objects.bulk_create(
            moderators,
            update_conflicts=True,
            unique_fields=["user", "channel"],
            update_fields=[
                "is_owner",
                "can_edit",
                "can_delete",
                "can_manage_moderators",
            ],
        )


class StatsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        ChannelStats.objects.filter(channel__in=ctx.channels).delete()
        mock_channels = parser_mocks.MOCK_CHANNELS
        stats: list[ChannelStats] = []
        parsed_at_values: list[Any] = []

        for index, channel in enumerate(ctx.channels):
            data = mock_channels[index % len(mock_channels)]
            growth_percent = float(data.get("growth30d", 0))
            subscribers = channel.participants_count or 0
            daily_growth = int(round(subscribers * growth_percent / 100 / 30))

            for day_offset in range(DEFAULT_STATS_DAYS):
                parsed_at_values.append(ctx.now - timedelta(days=day_offset))
                stats.append(
                    ChannelStats(
                        channel=channel,
                        participants_count=max(
                            1000, subscribers - daily_growth * day_offset
                        ),
                        daily_growth=daily_growth if day_offset else 0,
                    )
                )

        ChannelStats.objects.bulk_create(stats)
        # `parsed_at` is `auto_now_add`, so it is overwritten on insert and
        # must be restored in a single batched update.
        saved_stats = list(
            ChannelStats.objects.filter(channel__in=ctx.channels).order_by("pk")
        )
        for stat, parsed_at in zip(saved_stats, parsed_at_values):
            stat.parsed_at = parsed_at
        ChannelStats.objects.bulk_update(saved_stats, ["parsed_at"])

    def summary(self, ctx: DemoSeedContext) -> str | None:
        count = ChannelStats.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).count()
        return f"Статистика: {count}"


class PostsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        mock_posts = landing_mocks.MOCK_POSTS
        mock_reactions = parser_mocks.MOCK_POST_REACTIONS
        mock_analysis = parser_mocks.MOCK_POST_ANALYSIS

        posts: list[Post] = []
        expected_keys: set[tuple[int, int]] = set()

        for channel in ctx.channels:
            first_message_id = channel.channel_id * 10000 + 1
            max_message_id = first_message_id + DEFAULT_POSTS_PER_CHANNEL - 1
            channel.posts.filter(
                telegram_message_id__gt=max_message_id
            ).delete()

            for position in range(DEFAULT_POSTS_PER_CHANNEL):
                mock_post = mock_posts[position % len(mock_posts)]
                telegram_message_id = first_message_id + position
                expected_keys.add((channel.pk, telegram_message_id))
                posts.append(
                    Post(
                        channel=channel,
                        telegram_message_id=telegram_message_id,
                        text=str(mock_post["title"]),
                        hashtags=["demo", channel.category or "telegram"],
                        published_at=ctx.now - timedelta(hours=position * 6),
                        views=int(mock_post["views"]),
                        forwards=int(mock_post["forwards"]),
                        comments_count=max(5, int(mock_post["forwards"]) // 10),
                        reposts=max(int(mock_post["forwards"]) // 20, 1),
                        is_pinned=position == 0,
                        media_type=("photo" if position % 2 == 0 else "text"),
                        permalink=(
                            f"https://t.me/"
                            f"{channel.username or channel.channel_id}"
                            f"/{telegram_message_id}"
                        ),
                    )
                )

        Post.objects.bulk_create(
            posts,
            update_conflicts=True,
            unique_fields=["channel", "telegram_message_id"],
            update_fields=[
                "text",
                "hashtags",
                "published_at",
                "views",
                "forwards",
                "comments_count",
                "reposts",
                "is_pinned",
                "media_type",
                "permalink",
            ],
        )

        # `bulk_create(update_conflicts=True)` does not populate pks for
        # conflicting rows, so re-read the seeded posts before creating
        # related rows.
        saved_posts = [
            post
            for post in Post.objects.filter(channel__in=ctx.channels)
            if (post.channel_id, post.telegram_message_id) in expected_keys
        ]
        posts_by_channel: dict[int, list[Post]] = {
            channel.pk: [] for channel in ctx.channels
        }
        for post in sorted(
            saved_posts,
            key=lambda item: (item.channel_id, item.telegram_message_id),
        ):
            posts_by_channel[post.channel_id].append(post)

        PostReaction.objects.filter(post__in=saved_posts).delete()
        PostReaction.objects.bulk_create(
            [
                PostReaction(
                    post=post,
                    emoji=reaction["emoji"],
                    count=int(reaction["count"]),
                )
                for post in saved_posts
                for reaction in mock_reactions
            ]
        )

        for channel in ctx.channels:
            channel_posts = posts_by_channel[channel.pk]
            if not channel_posts:
                continue

            analysis, _ = PostAnalysis.objects.update_or_create(
                post=channel_posts[0],
                defaults={
                    "why_worked": _as_text(mock_analysis["why_worked"]),
                    "how_to_improve": _as_text(mock_analysis["how_to_improve"]),
                    "model_version": "claude-3-5",
                },
            )
            analysis.similar_posts.set(channel_posts[1:3])

    def summary(self, ctx: DemoSeedContext) -> str | None:
        count = Post.objects.filter(
            channel__channel_id__gte=DEMO_CHANNEL_ID_MIN
        ).count()
        return f"Посты: {count}"


class InsightsStep(BaseSeedStep):
    def seed(self, ctx: DemoSeedContext) -> None:
        demo_user = ctx.users.get("demo_user")
        if demo_user is None or not ctx.channels:
            return
        for index, insight in enumerate(ai_mocks.MOCK_INSIGHTS):
            AIInsight.objects.update_or_create(
                user=demo_user,
                channel=ctx.channels[index % len(ctx.channels)],
                insight_type=insight["type"],
                defaults={"insight_text": insight["text"]},
            )

    def summary(self, ctx: DemoSeedContext) -> str | None:
        count = AIInsight.objects.filter(
            user__username__in=users_mocks.DEMO_USERNAMES
        ).count()
        return f"AI-инсайты: {count}"


def _as_text(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value or "")
