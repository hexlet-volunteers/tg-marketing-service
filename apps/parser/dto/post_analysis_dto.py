from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PostAnalysisDTO(BaseModel):
    status: str
    why_worked: List[str]
    how_to_improve: List[str]
    similar_posts: List[Dict[str, Any]]
    model_version: Optional[str]


class PostDataDTO(BaseModel):
    id: int
    telegram_message_id: int
    channel_id: int
    text: str
    published_at: str
    views: int
    forwards: int
    comments_count: int
    is_pinned: bool
    media_type: str
    permalink: str
    reactions: Dict[str, Any]
    post_analysis: PostAnalysisDTO


class PostPagePropsDTO(BaseModel):
    """Обертка для props, которую ожидает Inertia"""

    post: PostDataDTO
