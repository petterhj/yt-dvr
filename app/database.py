import os

from sqlmodel import (
    create_engine,
    select,
    Session,
    SQLModel,
)


engine = create_engine(
    "sqlite:///" + os.path.join(os.environ["DATA_PATH"], "log.db"),
    echo=True,
    connect_args={"check_same_thread": False}
)


class Session(Session):
    def first_or_none(self, entity, *criterion):
        return self.exec(
            select(entity).where(*criterion)
        ).first()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
