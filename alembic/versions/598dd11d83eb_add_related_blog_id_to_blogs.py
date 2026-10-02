"""add related_blog_id to blogs

Revision ID: 598dd11d83eb
Revises: 54ac6fea77c7
Create Date: 2026-10-02 11:27:13.985562

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "598dd11d83eb"
down_revision: str | Sequence[str] | None = "54ac6fea77c7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FK_NAME = "fk_blogs_related_blog_id"


def upgrade() -> None:
    op.add_column("blogs", sa.Column("related_blog_id", sa.Integer(), nullable=True))
    # Named explicitly: an inline ForeignKey would leave Postgres free to invent
    # a name, which downgrade() could not reference deterministically.
    op.create_foreign_key(FK_NAME, "blogs", "blogs", ["related_blog_id"], ["id"])
    # Postgres does not index foreign key columns, so queries that follow the
    # relation would otherwise scan the whole table.
    op.create_index("ix_blogs_related_blog_id", "blogs", ["related_blog_id"])


def downgrade() -> None:
    op.drop_index("ix_blogs_related_blog_id", table_name="blogs")
    op.drop_constraint(FK_NAME, "blogs", type_="foreignkey")
    op.drop_column("blogs", "related_blog_id")