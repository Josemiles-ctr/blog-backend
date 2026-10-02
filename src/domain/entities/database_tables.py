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
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)

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

class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    Comments: Mapped[list["Comment"]] = relationship(
        "Comment", backref="blog", cascade="all, delete-orphan", passive_deletes=True
    )
    
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