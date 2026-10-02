"""baseline: initial blog schema

Revision ID: 54ac6fea77c7
Revises:
Create Date: 2026-10-02 11:21:03.330147

This is the adoption baseline for the schema that already existed in Supabase
before Alembic was introduced. The DDL is written out literally rather than
imported from the models on purpose: a migration must stay frozen, otherwise
later model edits would silently rewrite history.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "54ac6fea77c7"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE refs (
            id SERIAL NOT NULL,
            title VARCHAR(255) NOT NULL,
            link VARCHAR(2048),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE topics (
            id SERIAL NOT NULL,
            name VARCHAR(100) NOT NULL,
            description VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            UNIQUE (name)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE users (
            id SERIAL NOT NULL,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            UNIQUE (username),
            UNIQUE (email)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE blogs (
            id SERIAL NOT NULL,
            title VARCHAR(255) NOT NULL,
            content VARCHAR NOT NULL,
            author INTEGER NOT NULL,
            views INTEGER NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(author) REFERENCES users (id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE blog_references (
            blog_id INTEGER NOT NULL,
            reference_id INTEGER NOT NULL,
            PRIMARY KEY (blog_id, reference_id),
            FOREIGN KEY(blog_id) REFERENCES blogs (id) ON DELETE CASCADE,
            FOREIGN KEY(reference_id) REFERENCES refs (id) ON DELETE CASCADE
        )
        """
    )
    op.execute("CREATE INDEX ix_blog_references_reference_id ON blog_references (reference_id)")
    op.execute(
        """
        CREATE TABLE blog_topics (
            blog_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            PRIMARY KEY (blog_id, topic_id),
            FOREIGN KEY(blog_id) REFERENCES blogs (id) ON DELETE CASCADE,
            FOREIGN KEY(topic_id) REFERENCES topics (id) ON DELETE CASCADE
        )
        """
    )
    op.execute("CREATE INDEX ix_blog_topics_topic_id ON blog_topics (topic_id)")
    op.execute(
        """
        CREATE TABLE comments (
            id SERIAL NOT NULL,
            blog_id INTEGER NOT NULL,
            user_id INTEGER,
            content VARCHAR NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(blog_id) REFERENCES blogs (id),
            FOREIGN KEY(user_id) REFERENCES users (id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS comments CASCADE")
    op.execute("DROP TABLE IF EXISTS blog_topics CASCADE")
    op.execute("DROP TABLE IF EXISTS blog_references CASCADE")
    op.execute("DROP TABLE IF EXISTS blogs CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS topics CASCADE")
    op.execute("DROP TABLE IF EXISTS refs CASCADE")