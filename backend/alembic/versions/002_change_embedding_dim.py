"""Change embedding dimension from 1536 to 384 for sentence-transformers.

Revision ID: 002
Revises: 001
Create Date: 2026-06-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user_memory", "embedding")
    op.add_column(
        "user_memory",
        sa.Column("embedding", Vector(384), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_memory", "embedding")
    op.add_column(
        "user_memory",
        sa.Column("embedding", Vector(1536), nullable=True),
    )
