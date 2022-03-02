from sqlmodel import (
    create_engine,
    select,
    SQLModel,
)
from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from config import DB_FILE_PATH


engine = create_async_engine(
    "sqlite+aiosqlite:///" + DB_FILE_PATH,
    echo=True,
    connect_args={"check_same_thread": False},
)


class Session(AsyncSession):
    async def first_or_none(self, entity, *criterion):
        return (await self.exec(
            select(entity).where(*criterion)
        )).first()

    async def count(self, entity, *criterion):
        return (await self.exec(
            select(func.count(entity.id)).where(*criterion)
        )).one()


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with Session(engine) as session:
        yield session
