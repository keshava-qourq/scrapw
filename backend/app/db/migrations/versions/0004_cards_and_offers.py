"""cards and card offers

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

card_type = postgresql.ENUM("credit", "debit", name="card_type")
card_type_column = postgresql.ENUM("credit", "debit", name="card_type", create_type=False)

offer_type = postgresql.ENUM(
    "instant_discount", "cashback", "no_cost_emi", "coupon", name="offer_type"
)
offer_type_column = postgresql.ENUM(
    "instant_discount", "cashback", "no_cost_emi", "coupon", name="offer_type", create_type=False
)


def upgrade() -> None:
    card_type.create(op.get_bind(), checkfirst=True)
    offer_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bank_name", sa.String(length=100), nullable=False),
        sa.Column("card_name", sa.String(length=200), nullable=False),
        sa.Column("card_type", card_type_column, nullable=False, server_default="credit"),
        sa.Column("network", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "card_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cards.id"), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("offer_type", offer_type_column, nullable=False),
        sa.Column("discount_percentage", sa.Float(), nullable=True),
        sa.Column("discount_flat_amount", sa.Float(), nullable=True),
        sa.Column("max_discount_amount", sa.Float(), nullable=True),
        sa.Column("min_transaction_amount", sa.Float(), nullable=True),
        sa.Column("eligible_marketplace", sa.String(length=20), nullable=True),
        sa.Column("eligible_category", sa.String(length=200), nullable=True),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_card_offers_card_id", "card_offers", ["card_id"])


def downgrade() -> None:
    op.drop_index("ix_card_offers_card_id", table_name="card_offers")
    op.drop_table("card_offers")
    op.drop_table("cards")
    offer_type.drop(op.get_bind(), checkfirst=True)
    card_type.drop(op.get_bind(), checkfirst=True)
