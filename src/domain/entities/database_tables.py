from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

blog_topics = Table(
    "blog_topics",
    Base.metadata,
    Column(
        "blog_id",
        Integer,
        ForeignKey("blogs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "topic_id",
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

blog_references = Table(
    "blog_references",
    Base.metadata,
    Column(
        "blog_id",
        Integer,
        ForeignKey("blogs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "reference_id",
        Integer,
        ForeignKey("refs.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(500), default=None)

    blogs: Mapped[list["Blog"]] = relationship(
        secondary=blog_topics,
        back_populates="topics",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Topic id={self.id} name={self.name!r}>"

class Reference(Base):
    __tablename__ = "refs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    link: Mapped[str | None] = mapped_column(String(2048), default=None)

    blogs: Mapped[list["Blog"]] = relationship(
        secondary=blog_references,
        back_populates="references",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Reference id={self.id} title={self.title!r}>"


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)

    topics: Mapped[list["Topic"]] = relationship(
        secondary=blog_topics,
        back_populates="blogs",
    )
    references: Mapped[list["Reference"]] = relationship(
        secondary=blog_references,
        back_populates="blogs",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Blog id={self.id} title={self.title!r}>"