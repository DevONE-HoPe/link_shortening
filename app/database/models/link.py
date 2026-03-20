from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import Base, big_int_pk, created_at


class Link(Base):
    __tablename__ = "links"

    id: Mapped[big_int_pk]
    short_id: Mapped[str] = mapped_column(String(20), nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[created_at]

    __table_args__ = (
        Index("ix_links_short_id", "short_id", unique=True),
    )
