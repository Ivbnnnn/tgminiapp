"""Add approved seller whitelist.

Revision ID: 0002_seller_whitelist
Revises: 0001_marketplace
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0002_seller_whitelist"
down_revision: str | None = "0001_marketplace"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sellers",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id", name="uq_sellers_telegram_id"),
        sa.UniqueConstraint("user_id", name="uq_sellers_user_id"),
    )
    op.add_column("products", sa.Column("seller_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_products_seller_id",
        "products",
        "sellers",
        ["seller_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_products_seller_id", "products", ["seller_id"])


def downgrade() -> None:
    op.drop_index("idx_products_seller_id", table_name="products")
    op.drop_constraint("fk_products_seller_id", "products", type_="foreignkey")
    op.drop_column("products", "seller_id")
    op.drop_table("sellers")
