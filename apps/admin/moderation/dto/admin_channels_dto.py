from pydantic import BaseModel


class AdminChannelData(BaseModel):
    channelId: int
    username: str
    title: str
    category: str
    isVerified: bool
    subscribers: int


class AdminChannelsDTO(BaseModel):
    channels: list[AdminChannelData]
    categories: list[str]
