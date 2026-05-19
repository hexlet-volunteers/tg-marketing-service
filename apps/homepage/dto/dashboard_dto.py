from pydantic import BaseModel, Field
from typing import List, Optional


class StatsDTO(BaseModel):
    channels: int
    posts: int
    ai_suggestions: int
    days_left: int


class ChannelDTO(BaseModel):
    name: str
    subscribers: int = Field(ge=0)
    posts: int = Field(ge=0)
    views: int = Field(ge=0)
    engagement: float = Field(ge=0, le=100)
    growth: float


class InsightDTO(BaseModel):
    text: str
    type: str
    id: Optional[int] = None


class CollectionDTO(BaseModel):
    name: str
    channels_count: int
    slug: str
    description: Optional[str]
    is_auto: bool


class DashboardDTO(BaseModel):
    stats: StatsDTO
    channels: List[ChannelDTO]
    ai_insights: List[InsightDTO]
    collections: List[CollectionDTO]
    quick_actions: List[str]
