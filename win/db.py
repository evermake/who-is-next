__all__ = ["engine", "create_db_and_tables", "get_session"]

from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine

# Import all models to register them in SQLModel
import win.models  # noqa: F401
from win.config import settings


engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Session:
    with Session(engine) as session:
        yield session
