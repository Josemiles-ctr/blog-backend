"""related_blog_id on delete set null

Revision ID: 97d79592a143
Revises: 87b6f5cc3af7
Create Date: 2026-10-02 11:59:38.233248

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "97d79592a143"
down_revision: str | Sequence[str] | None = "87b6f5cc3af7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FK_NAME = "fk_blogs_related_blog_id"


def upgrade() -> None:
    op.drop_constraint(FK_NAME, "blogs", type_="foreignkey")
    op.create_foreign_key(
        FK_NAME, "blogs", "blogs", ["related_blog_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint(FK_NAME, "blogs", type_="foreignkey")
    op.create_foreign_key(FK_NAME, "blogs", "blogs", ["related_blog_id"], ["id"])