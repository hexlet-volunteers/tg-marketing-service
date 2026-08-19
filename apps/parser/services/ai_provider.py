from abc import ABC, abstractmethod
from typing import List, TypedDict


class AIAnalysisResult(TypedDict):
    why_worked: List[str]
    how_to_improve: List[str]
    similar_posts_ids: List[int]  # ID постов для связи в БД


class CandidatePost(TypedDict):
    id: int
    text: str
    views: int
    forwards: int
    comments_count: int
    reposts: int


class BaseAIProvider(ABC):
    @abstractmethod
    def analyze(
        self, post_text: str, metrics: dict, candidates: List[CandidatePost]
    ) -> AIAnalysisResult:
        pass


class DeterministicFallbackProvider(BaseAIProvider):
    """Детерминированная заглушка без ключа LLM"""

    def analyze(
        self, post_text: str, metrics: dict, candidates: List[CandidatePost]
    ) -> AIAnalysisResult:
        return {
            "why_worked": [
                "High engagement due to topic",
                "Clear call to action",
            ],
            "how_to_improve": [
                "Add more visual elements",
                "Shorten the introduction",
            ],
            "similar_posts_ids": [candidates[0]["id"]] if candidates else [],
        }
