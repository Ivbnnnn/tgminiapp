"""Create Telegram marketplace tables.

Revision ID: 0001_marketplace
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0001_marketplace"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_table(
        "brands",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("normalized_name", sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sizes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("type", sa.String(64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "search_suggestions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("query", sa.String(255), nullable=False),
        sa.Column("normalized_query", sa.String(255), nullable=False),
        sa.Column("popularity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("popularity >= 0", name="ck_search_suggestions_popularity_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_query"),
    )
    op.create_index("idx_search_suggestions_normalized_query", "search_suggestions", ["normalized_query"])
    op.create_index("idx_search_suggestions_popularity", "search_suggestions", ["popularity"])

    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.BigInteger(), nullable=True),
        sa.Column("brand_id", sa.BigInteger(), nullable=True),
        sa.Column("size_id", sa.BigInteger(), nullable=True),
        sa.Column("seller_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("seller_telegram_username", sa.String(255), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("condition", sa.String(64), server_default="used", nullable=False),
        sa.Column("gender", sa.String(64), nullable=True),
        sa.Column("color", sa.String(64), nullable=True),
        sa.Column("material", sa.String(128), nullable=True),
        sa.Column("is_unique", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("status", sa.String(64), server_default="active", nullable=False),
        sa.Column("search_vector", postgresql.TSVECTOR(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        sa.CheckConstraint("stock_quantity >= 0", name="ck_products_stock_non_negative"),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["size_id"], ["sizes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("category_id", "brand_id", "size_id", "status", "price"):
        op.create_index(f"idx_products_{column}", "products", [column])
    op.create_index("idx_products_search_vector", "products", ["search_vector"], postgresql_using="gin")

    op.create_table(
        "product_photos",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("position BETWEEN 1 AND 4", name="ck_product_photos_position_between_1_and_4"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "position", name="uq_product_photo_position"),
    )
    op.create_index("idx_product_photos_product_id", "product_photos", ["product_id"])

    op.create_table(
        "favorites",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "product_id"),
    )
    op.create_index("idx_favorites_user_id", "favorites", ["user_id"])
    op.create_index("idx_favorites_product_id", "favorites", ["product_id"])

    op.create_table(
        "user_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("user_id", "product_id", "event_type", "created_at"):
        op.create_index(f"idx_user_events_{column}", "user_events", [column])


def downgrade() -> None:
    op.drop_table("user_events")
    op.drop_table("favorites")
    op.drop_table("product_photos")
    op.drop_table("products")
    op.drop_table("search_suggestions")
    op.drop_table("sizes")
    op.drop_table("categories")
    op.drop_table("brands")
    op.drop_table("users")
