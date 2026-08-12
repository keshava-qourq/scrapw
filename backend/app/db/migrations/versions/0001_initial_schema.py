"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

availability_status = postgresql.ENUM(
    "in_stock", "out_of_stock", "limited_stock", "unknown",
    name="availability_status",
)
# Column-level reference must not re-create the type; we create it explicitly
# below before the table that uses it.
availability_status_column_type = postgresql.ENUM(
    "in_stock", "out_of_stock", "limited_stock", "unknown",
    name="availability_status",
    create_type=False,
)


def upgrade() -> None:
    availability_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "marketplaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_marketplaces_code"),
    )
    op.create_index("ix_marketplaces_code", "marketplaces", ["code"])

    op.create_table(
        "canonical_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("brand", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("marketplace_id", sa.Integer(), sa.ForeignKey("marketplaces.id"), nullable=False),
        sa.Column("marketplace_product_id", sa.String(length=255), nullable=False),
        sa.Column("product_url", sa.Text(), nullable=False),
        sa.Column(
            "canonical_product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("canonical_products.id"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("brand", sa.String(length=200), nullable=True),
        sa.Column("category", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("images", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("mrp", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_percentage", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("availability", availability_status_column_type, nullable=False, server_default="unknown"),
        sa.Column("sizes", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("colors", postgresql.ARRAY(sa.Text()), nullable=False, server_default="{}"),
        sa.Column("seller_name", sa.String(length=255), nullable=True),
        sa.Column("seller_rating", sa.Float(), nullable=True),
        sa.Column("specifications", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("raw_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "marketplace_id", "marketplace_product_id", name="uq_marketplace_product"
        ),
    )
    op.create_index("ix_products_brand_category", "products", ["brand", "category"])
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category", "products", ["category"])


def downgrade() -> None:
    op.drop_index("ix_products_category", table_name="products")
    op.drop_index("ix_products_brand", table_name="products")
    op.drop_index("ix_products_brand_category", table_name="products")
    op.drop_table("products")
    op.drop_table("canonical_products")
    op.drop_index("ix_marketplaces_code", table_name="marketplaces")
    op.drop_table("marketplaces")
    availability_status.drop(op.get_bind(), checkfirst=True)
