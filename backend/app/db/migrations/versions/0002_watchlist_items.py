"""watchlist items

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "watchlist_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_name", sa.String(length=500), nullable=False),
        sa.Column("group_key", sa.String(length=500), nullable=False),
        sa.Column("marketplace", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_watchlist_items_group_key", "watchlist_items", ["group_key"])


def downgrade() -> None:
    op.drop_index("ix_watchlist_items_group_key", table_name="watchlist_items")
    op.drop_table("watchlist_items")
