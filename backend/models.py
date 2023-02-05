from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel, Relationship


class ExportPropertiesMixin(BaseModel):
    @classmethod
    def get_properties(cls):
        return [prop for prop in dir(cls) if isinstance(
            getattr(cls, prop
        ), property) and prop not in ("__values__", "fields")]

    def dict(self, *args, **kwargs):
        attribs = super().dict(*args, **kwargs)
        props = self.get_properties()
        if props:
            attribs.update({
                prop: getattr(self, prop) for prop in props
            })
        return attribs


class ItemBase(SQLModel):
    source: str
    item_id: str
    title: str
    description: str
    thumbnail: str = None
    series_title: str = None
    season_number: int = None
    episode_number: int = None
    item_url: str = None
    series_url: str = None

    class Config:
        allow_population_by_field_name = True


class Item(ItemBase, table=True):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint("source", "item_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)

    jobs: list["Job"] = Relationship(
        sa_relationship_kwargs={
            # https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html#relationship-loading-techniques
            # https://stackoverflow.com/a/74256068/1167835
            "lazy": "selectin",
            "cascade": "delete",
        },
        back_populates="item",
    )

    def __str__(self):
        return f"{self.source}:{self.item_id}"


class ItemIn(SQLModel):
    source: str
    item_id: str


class ItemOut(ItemBase):
    id: Optional[int]


class ItemOutWithJobs(ItemOut):
    jobs: list["JobOut"] = []


class JobStatus(str, Enum):
    NEW = 'new'
    QUEUED = 'queued'
    STARTED = 'started'
    DOWNLOADED = 'downloaded'
    FAILED = 'failed'


class JobBase(SQLModel, ExportPropertiesMixin):
    created_at: datetime
    queued_at: Optional[datetime]
    started_at: Optional[datetime]
    downloaded_at: Optional[datetime]
    failed_at: Optional[datetime]
    result: Optional[str]

    @property
    def status(self):
        if not any([self.queued_at, self.started_at, self.downloaded_at, self.failed_at]):
            return JobStatus.NEW
        elif self.queued_at and not any([self.started_at, self.downloaded_at, self.failed_at]):
            return JobStatus.QUEUED
        elif self.started_at and not any([self.downloaded_at, self.failed_at]):
            return JobStatus.STARTED
        elif self.downloaded_at and not self.failed_at:
            return JobStatus.DOWNLOADED
        elif self.failed_at:
            return JobStatus.FAILED 


class Job(JobBase, table=True):
    __tablename__ = "job"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

    item_id: int = Field(foreign_key="item.id")
    item: Item = Relationship(
        back_populates="jobs",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class JobOut(JobBase):
    id: int


class JobOutWithItem(JobOut):
    item: Optional[ItemOut]


class JobProgress(ExportPropertiesMixin):
    message: str = None
    total_bytes: int = None
    downloaded_bytes: int = None

    @property
    def downloaded_percent(self) -> int:
        if self.total_bytes and self.downloaded_bytes:
            return round((int(self.downloaded_bytes) / int(self.total_bytes)) * 100)
        return None


ItemOut.update_forward_refs()
ItemOutWithJobs.update_forward_refs()
