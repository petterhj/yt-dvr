from sqlmodel import (
    create_engine,
    select,
    Session,
    SQLModel,
)

from config import DB_FILE_PATH


engine = create_engine(
    "sqlite:///" + DB_FILE_PATH,
    echo=True,
    connect_args={
        "check_same_thread": False,
    }
)


class Session(Session):
    def first_or_none(self, entity, *criterion):
        return self.exec(
            select(entity).where(*criterion)
        ).first()

    def count(self, entity, *criterion):
        return self.query(entity).filter(*criterion).count()

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
