from typing import TypedDict


class SubmittedByData(TypedDict):
    id: int
    username: str | None


class ChannelData(TypedDict):
    id: int
    username: str | None
    title: str | None


class ModerationRequestData(TypedDict):
    id: int
    submitted_by: SubmittedByData | None
    channel_identifier: str
    channel: ChannelData | None
    category: str
    country: str
    language: str
    status: str
    reject_reason: str | None
    created_at: str
    resolved_at: str | None
