from typing import List, Optional

from sqlalchemy import BigInteger, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    telegram_id: int = Field(primary_key=True, sa_column=Column(BigInteger()))


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default="")
    chat_id: int = Field(sa_column=Column(BigInteger()))
    participants: List["Participant"] = Relationship(back_populates="activity")

    __table_args__ = (
        UniqueConstraint("chat_id", "name", name="unique_name_in_chat"),
    )


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    telegram_id: Optional[int] = Field(
        primary_key=True, sa_column=Column(BigInteger())
    )
    name: str
    counter: int = Field(default=0, ge=0)

    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    activity: Activity = Relationship(back_populates="participants")

    def __eq__(self, other):
        if not isinstance(other, Participant):
            return False

        if self.id and other.id:
            return self.id == other.id

        if self.telegram_id and other.telegram_id:
            return self.telegram_id == other.telegram_id

        return self.name == other.name
