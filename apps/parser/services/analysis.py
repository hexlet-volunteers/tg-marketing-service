from typing import Optional

from apps.parser.models import Post, PostAnalysis

from .ai_provider import (
    AIAnalysisResult,
    BaseAIProvider,
    CandidatePost,
    DeterministicFallbackProvider,
)


class PostAnalysisService:
    def __init__(self, provider: Optional[BaseAIProvider] = None):
        self.provider = provider or DeterministicFallbackProvider()

    def get_analysis(
        self, post: Post, force_regenerate: bool = False
    ) -> PostAnalysis:
        # 1. Попытка получить из кеша (БД)
        if not force_regenerate:
            existing = PostAnalysis.objects.filter(post=post).first()
            if existing:
                return existing

        # 2. Генерация через провайдера
        metrics = {
            "views": post.views,
            "forwards": post.forwards,
            "comments": post.comments_count,
        }

        candidates_qs = (
            Post.objects.filter(channel=post.channel)
            .exclude(id=post.id)
            .order_by("-published_at")[:20]
        )
        candidates: list[CandidatePost] = [
            {
                "id": c.id,
                "text": c.text,
                "views": c.views,
                "forwards": c.forwards,
                "comments_count": c.comments_count,
                "reposts": c.reposts,
            }
            for c in candidates_qs
        ]

        try:
            data: AIAnalysisResult = self.provider.analyze(
                post.text, metrics, candidates
            )
        except Exception:
            # 3. Фолбэк на заглушку при любой ошибке провайдера
            data = DeterministicFallbackProvider().analyze(
                post.text, metrics, candidates
            )

        # 4. Сохранение/Обновление в PostAnalysis
        analysis, created = PostAnalysis.objects.update_or_create(
            post=post,
            defaults={
                "why_worked": "\n".join(data["why_worked"]),
                "how_to_improve": "\n".join(data["how_to_improve"]),
                "model_version": self.provider.__class__.__name__,
            },
        )

        # Обновление ManyToMany (similar_posts)
        analysis.similar_posts.clear()
        if data["similar_posts_ids"]:
            analysis.similar_posts.set(data["similar_posts_ids"])

        return analysis

    @classmethod
    def trigger_analysis_if_needed(cls, post: Post):
        """
        Быстрый метод для Сериализатора.
        Проверяет наличие анализа и, если его нет, ставит задачу в очередь.
        """
        if not PostAnalysis.objects.filter(post=post).exists():
            # Вызываем Celery задачу
            from apps.parser.tasks import run_post_analysis_task

            run_post_analysis_task.delay(post.id)  # type: ignore[attr-defined]
