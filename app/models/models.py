import datetime
import uuid

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    plan: Mapped[str] = mapped_column(String, nullable=False, default="free")
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now
    )

    share_items: Mapped[list["ShareItem"]] = relationship(
        "ShareItem", back_populates="user", cascade="all, delete-orphan"
    )


class ShareItem(Base):
    __tablename__ = "share_items"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    short_code: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    share_type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    expiry: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now
    )

    user: Mapped["User | None"] = relationship("User", back_populates="share_items")


class SuccessResponse(BaseModel):
    detail: str
    data: dict
