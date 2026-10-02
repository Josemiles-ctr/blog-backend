from datetime import UTC, datetime

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
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Reverse sides are "raise": a blog read never needs these, so allowing a
    # lazy load here would reintroduce the N+1 queries eager loading exists to
    # prevent. They fail loudly instead.
    blogs: Mapped[list[Blog]] = relationship(
        back_populates="author",
        lazy="raise",
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="user",
        lazy="raise",
    )

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
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)

    blog: Mapped[Blog] = relationship(back_populates="comments", lazy="raise")
    user: Mapped[User | None] = relationship(
        back_populates="comments",
        lazy="selectin",
    )


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

    blogs: Mapped[list[Blog]] = relationship(
        secondary=blog_topics,
        back_populates="topics",
        lazy="raise",
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

    blogs: Mapped[list[Blog]] = relationship(
        secondary=blog_references,
        back_populates="references",
        lazy="raise",
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
    # The database column is named "author"; the id lives here and the related
    # User is exposed as `author` so it can be eager loaded like any other.
    author_id: Mapped[int] = mapped_column(
        "author", ForeignKey("users.id"), nullable=False, index=True
    )
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    related_blog_id: Mapped[int | None] = mapped_column(
        # SET NULL, not the default RESTRICT: deleting a post must not fail just
        # because another post links to it. The dangling link becomes null.
        ForeignKey("blogs.id", ondelete="SET NULL"),
        default=None,
        nullable=True,
        index=True,
    )

    # Everything a blog read needs is loaded up front by the ORM, so no query
    # path can trigger a surprise round trip mid-serialisation.
    author: Mapped[User] = relationship(back_populates="blogs", lazy="selectin")
    # Self-referential, so neither "selectin" nor "joined" can resolve it from
    # the model alone: "joined" emits no self-join and "selectin" leaves it unset
    # until touched. It is loaded explicitly via selectinload() by the
    # repository, and "raise" guarantees nothing sneaks in a lazy query.
    related_blog: Mapped[Blog | None] = relationship(
        remote_side="Blog.id",
        foreign_keys=[related_blog_id],
        lazy="raise",
    )
    comments: Mapped[list[Comment]] = relationship(
        back_populates="blog",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    topics: Mapped[list[Topic]] = relationship(
        secondary=blog_topics,
        back_populates="blogs",
        lazy="selectin",
    )
    references: Mapped[list[Reference]] = relationship(
        secondary=blog_references,
        back_populates="blogs",
        lazy="selectin",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, server_default=func.now()
    )