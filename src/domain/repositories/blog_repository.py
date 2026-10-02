from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from src.domain.entities import (
    Blog,
    BlogCreate,
    BlogUpdate,
    Reference,
    Topic,
)


def _load(db: Session, blog_id: int) -> Blog | None:
    stmt = (
        select(Blog)
        .options(selectinload(Blog.topics), selectinload(Blog.references), selectinload(Blog.author))
        .where(Blog.id == blog_id)
    )
    return db.scalars(stmt).one_or_none()


def _resolve_topics(db: Session, names: list[str]) -> list[Topic]:
    existing = {
        t.name: t
        for t in db.scalars(select(Topic).where(Topic.name.in_(names))).all()
    }
    resolved = []
    for name in names:
        topic = existing.get(name)
        if topic is None:
            topic = Topic(name=name)
            db.add(topic)
            existing[name] = topic
        resolved.append(topic)
    return resolved


def _resolve_references(
    db: Session, items: list[tuple[str, str | None]]
) -> list[Reference]:
    titles = [t for t, _ in items]
    existing = {
        (r.title, r.link): r
        for r in db.scalars(
            select(Reference).where(Reference.title.in_(titles))
        ).all()
    }
    resolved = []
    for title, link in items:
        link_str = str(link) if link is not None else None
        ref = existing.get((title, link_str))
        if ref is None:
            ref = Reference(title=title, link=link_str)
            db.add(ref)
            existing[(title, link_str)] = ref
        resolved.append(ref)
    return resolved


def _prune_orphans(db: Session) -> None:
    db.execute(delete(Topic).where(~Topic.blogs.any()))
    db.execute(delete(Reference).where(~Reference.blogs.any()))


def _apply(db: Session, blog: Blog, data: BlogCreate | BlogUpdate) -> None:
    if data.topics is not None:
        blog.topics = _resolve_topics(db, [t.name for t in data.topics])
    if data.references is not None:
        blog.references = _resolve_references(
            db, [(r.title, str(r.link) if r.link else None) for r in data.references]
        )


def create_blog(db: Session, data: BlogCreate) -> Blog:
    blog = Blog(title=data.title, content=data.content)
    _apply(db, blog, data)
    db.add(blog)
    db.commit()
    return _load(db, blog.id)  # type: ignore[return-value]


def get_blog(db: Session, blog_id: int) -> Blog | None:
    return _load(db, blog_id)


def list_blogs(db: Session, skip: int = 0, limit: int = 100) -> list[Blog]:
    stmt = (
        select(Blog)
        .options(selectinload(Blog.topics), selectinload(Blog.references))
        .order_by(Blog.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


def update_blog(db: Session, blog_id: int, data: BlogUpdate) -> Blog | None:
    blog = _load(db, blog_id)
    if blog is None:
        return None

    for field in ("title", "content"):
        value = getattr(data, field)
        if value is not None:
            setattr(blog, field, value)

    _apply(db, blog, data)
    db.flush()
    _prune_orphans(db)
    db.commit()
    return _load(db, blog_id)


def delete_blog(db: Session, blog_id: int) -> bool:
    blog = _load(db, blog_id)
    if blog is None:
        return False
    db.delete(blog)
    db.flush()
    _prune_orphans(db)
    db.commit()
    return True