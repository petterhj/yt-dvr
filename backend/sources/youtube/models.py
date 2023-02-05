from datetime import datetime

from pydantic import BaseModel, Field, validator

from models import ItemBase


class YoutubeItem(ItemBase):
    source: str = "youtube"
    item_id: str = Field(..., alias="resourceId")
    series_title: str = Field(None, alias="videoOwnerChannelTitle")
    added_at: datetime = Field(..., alias="publishedAt")
    thumbnail: str = Field(None, alias="thumbnails")

    @validator("item_id", pre=True)
    def get_item_id(cls, v) -> str:
        return v if type(v) == str else v["videoId"]

    @validator("item_url", pre=True, always=True)
    def get_item_url(cls, v: str, values: dict):
        return f"https://www.youtube.com/watch?v={values['item_id']}"

    @validator("series_url", pre=True, always=True)
    def get_series_url(cls, v: str, values: dict):
        if values.get("series_title"):
            return f"https://www.youtube.com/@{values['series_title']}"

    @validator("thumbnail", pre=True)
    def get_thumbnail(cls, v) -> str:
        for quality in ("maxres", "standard", "high", "medium", "default"):
            if v.get(quality):
                return v[quality]["url"]

    class Config:
        extra = "ignore"
