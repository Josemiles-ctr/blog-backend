from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.domain.entities import BlogCreate, BlogRead, BlogUpdate
from src.domain.repositories import blog_repository
from src.infrastructure.database.session import get_db

blogs_router = APIRouter(prefix="/blogs", tags=["blogs"])


@blogs_router.post("", response_model=BlogRead, status_code=status.HTTP_201_CREATED)
def create_blog(data: BlogCreate, db: Session = Depends(get_db)) -> BlogRead:
    try:
        blog = blog_repository.create_blog(db, data)
    except blog_repository.UnknownAuthorError as exc:
        raise HTTPException(status_code=404, detail=f"Author {exc.author_id} not found")
    return BlogRead.model_validate(blog)


@blogs_router.get("", response_model=list[BlogRead])
def list_blogs(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> list[BlogRead]:
    return [BlogRead.model_validate(b) for b in blog_repository.list_blogs(db, skip, limit)]


@blogs_router.get("/{blog_id}", response_model=BlogRead)
def get_blog(blog_id: int, db: Session = Depends(get_db)) -> BlogRead:
    blog = blog_repository.get_blog(db, blog_id)
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogRead.model_validate(blog)


@blogs_router.patch("/{blog_id}", response_model=BlogRead)
def update_blog(
    blog_id: int, data: BlogUpdate, db: Session = Depends(get_db)
) -> BlogRead:
    try:
        blog = blog_repository.update_blog(db, blog_id, data)
    except blog_repository.UnknownAuthorError as exc:
        raise HTTPException(status_code=404, detail=f"Author {exc.author_id} not found")
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return BlogRead.model_validate(blog)


@blogs_router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, db: Session = Depends(get_db)) -> None:
    if not blog_repository.delete_blog(db, blog_id):
        raise HTTPException(status_code=404, detail="Blog not found")