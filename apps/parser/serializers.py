from django.contrib import admin

from apps.parser.models import Post
from apps.parser.services.analysis import PostAnalysisService


class PostSerializer:
    """
    Сериализатор для модели Post и связанных метрик.
    Предназначен для передачи данных в Inertia через props.
    """

    @classmethod
    def get_post_data(cls, post: Post) -> dict:
        breakdown = post.get_reactions_breakdown()

        """
        Словарь пропсов для фронтенда (Inertia.js):
       
        {
            "id": int,
            "telegram_message_id": int,
            "channel_id": int,
            "text": str,
            "published_at": str,
            "views": int,
            "forwards": int,
            "comments_count": int,
            "reposts": int,
            "is_pinned": bool,
            "media_type": str,
            "permalink": str,
            "reactions": {
                "total": int,
                "details": dict
            },
            "post_analysis": {
                "why_worked": list[str],
                "how_to_improve": list[str],
                "similar_posts": list[dict],
                "model_version": str
            }
        }
        """

        post_analysis_data = {}

        if hasattr(post, "post_analysis"):
            analysis = post.post_analysis
            post_analysis_data = {
                "status": "completed",
                "why_worked": analysis.why_worked.split("\n"),
                "how_to_improve": analysis.how_to_improve.split("\n"),
                "similar_posts": [
                    {
                        "telegram_message_id": p.telegram_message_id,
                        "text": p.text,
                        "permalink": p.permalink,
                        "views": p.views,
                        "forwards": p.forwards,
                        "comments_count": p.comments_count,
                        "reposts": p.reposts,
                        "total_reactions": p.total_reactions(),
                    }
                    for p in analysis.similar_posts.all()
                ],
                "model_version": analysis.model_version,
            }
        else:
            # метод, который мгновенно возвращает управление
            PostAnalysisService.trigger_analysis_if_needed(post)

            post_analysis_data = {
                "status": "processing",
                "why_worked": [],
                "how_to_improve": [],
                "similar_posts": [],
                "model_version": None,
            }

        return {
            "id": post.id,
            "telegram_message_id": post.telegram_message_id,
            "channel_id": post.channel.id,
            "text": post.text,
            "published_at": post.published_at.isoformat(),
            "views": post.views,
            "forwards": post.forwards,
            "comments_count": post.comments_count,
            "reposts": post.reposts,
            "is_pinned": post.is_pinned,
            "media_type": post.media_type,
            "permalink": post.permalink,
            "reactions": {
                "total": breakdown["total"],
                "details": breakdown["details"],
            },
            "post_analysis": post_analysis_data,
        }

    @classmethod
    def get_serialized_post_for_inertia(cls, post_id: int) -> dict:
        try:
            # select_related, чтобы подтянуть AI данные одним запросом
            post = Post.objects.select_related("post_analysis").get(id=post_id)
            return cls.get_post_data(post)
        except Post.DoesNotExist:
            raise Post.DoesNotExist(f"Post with id {post_id} does not exist")

    @classmethod
    def get_posts_list_data(cls, queryset) -> list[dict]:
        """
        Возвращает список сериализованных постов для представления списка
        """
        return [cls.get_post_data(post) for post in queryset]

    @staticmethod
    def get_admin_list_display() -> list:
        """
        Ключевые метрики для отображения в админке (list_display)
        """
        return [
            "telegram_message_id",
            "text_preview",
            "published_at",
            "views",
            "forwards",
            "comments_count",
            "reposts",
            "is_pinned",
            "media_type",
            "permalink",
            "total_reactions",
        ]

    @classmethod
    def get_admin_list_filter(cls) -> tuple:
        """
        Поля для фильтрации в админке
        """
        return (
            "media_type",
            "is_pinned",
            "published_at",
            ("channel", admin.RelatedFieldListFilter),
        )

    @classmethod
    def get_admin_search_fields(cls) -> tuple:
        """
        Поля для поиска в админке
        """
        return (
            "telegram_message_id",
            "text",
            "channel__title",
            "channel__username",
        )
