"""Initialize BlackBull AI memory tables.

Creates:
  - user_memory: key-value store with pgvector embedding column
  - conversation: tracks user conversation sessions
  - message: stores individual turns within a conversation

Revision ID: 001
Revises:
Create Date: 2026-06-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# pgvector vector type
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension (required if using vector embeddings)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ---- user_memory ----
    op.create_table(
        "user_memory",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column(
            "agent_name", sa.String(100), nullable=False, server_default="shared"
        ),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Add vector column separately for clarity
    if Vector is not None:
        op.add_column("user_memory", sa.Column("embedding", Vector(384), nullable=True))
    else:
        op.add_column("user_memory", sa.Column("embedding", sa.Text, nullable=True))

    op.create_index(
        "ix_user_memory_user_agent", "user_memory", ["user_id", "agent_name"]
    )
    op.create_index(
        "ix_user_memory_user_key", "user_memory", ["user_id", "key"], unique=True
    )

    # ---- conversation ----
    op.create_table(
        "conversation",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", sa.String(255), nullable=False, index=True),
        sa.Column("agent_name", sa.String(100), nullable=False, server_default="yami"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # ---- message ----
    op.create_table(
        "message",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "conversation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("conversation.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("message")
    op.drop_table("conversation")
    op.drop_table("user_memory")
    op.execute("DROP EXTENSION IF EXISTS vector")
