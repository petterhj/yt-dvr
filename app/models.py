from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class BaseItem(BaseModel):
    video_id: str
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: datetime
    thumbnail: str = None


class PlaylistItem(BaseItem):
    video_id: str = Field(..., alias="resourceId")
    channel_id: str = Field(..., alias="channelId")
    channel_title: str = Field(..., alias="videoOwnerChannelTitle")
    published_at: datetime = Field(..., alias="publishedAt")
    thumbnail: str = Field(None, alias="thumbnails")

    @validator("video_id", pre=True)
    def get_video_id(cls, v) -> str:
        return v["videoId"]

    @validator("thumbnail", pre=True)
    def get_thumbnail(cls, v) -> str:
        for quality in ("maxres", "standard", "high", "medium", "default"):
            if v.get(quality):
                return v[quality]["url"]

    class Config:
        extra = "ignore"


class DatabaseItemBase(SQLModel):
    created_at: datetime
    started_at: Optional[datetime]
    downloaded_at: Optional[datetime]
    failed_at: Optional[datetime]


class DatabaseItem(DatabaseItemBase, table=True):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("video_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str
    created_at: datetime = Field(
        default_factory=datetime.now,
    )


class DatabaseItemOut(DatabaseItemBase):
    id: int


class Item(BaseItem):
    video_url: Optional[str]
    job: Optional[DatabaseItemBase]

    @validator("video_url", pre=True, always=True)
    def get_video_url(cls, v: str, values: dict):
        return f"https://www.youtube.com/watch?v={values['video_id']}"


class ItemOut(Item):
    job: Optional[DatabaseItemOut]
