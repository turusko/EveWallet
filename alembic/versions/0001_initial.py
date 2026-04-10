"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "eve_characters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("character_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("character_name", sa.String(length=255), nullable=False),
        sa.Column("character_owner_hash", sa.String(length=255), nullable=True),
        sa.Column("scopes", sa.Text(), nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unlinked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "eve_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False, unique=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "wallet_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("transaction_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("unit_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(18, 2), nullable=False),
        sa.Column("is_buy", sa.Boolean(), nullable=False),
        sa.Column("is_personal", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("client_id", sa.BigInteger(), nullable=True),
        sa.Column("client_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_wallet_transactions_date", "wallet_transactions", ["date"])
    op.create_table(
        "market_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("region_id", sa.BigInteger(), nullable=True),
        sa.Column("price", sa.Numeric(18, 2), nullable=False),
        sa.Column("volume_total", sa.Integer(), nullable=False),
        sa.Column("volume_remain", sa.Integer(), nullable=False),
        sa.Column("min_volume", sa.Integer(), nullable=True),
        sa.Column("is_buy_order", sa.Boolean(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("escrow", sa.Numeric(18, 2), nullable=True),
        sa.Column("broker_fee", sa.Numeric(18, 2), nullable=True),
        sa.Column("sales_tax", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "project_buckets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    source_type = sa.Enum("wallet_transaction", "market_order", name="source_type_enum")
    source_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "bucket_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=False),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("source_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("assigned_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("source_type", "source_uuid", name="uq_assignment_source"),
    )


def downgrade() -> None:
    op.drop_table("bucket_assignments")
    op.drop_table("project_buckets")
    op.drop_table("market_orders")
    op.drop_index("ix_wallet_transactions_date", table_name="wallet_transactions")
    op.drop_table("wallet_transactions")
    op.drop_table("eve_tokens")
    op.drop_table("eve_characters")
    op.drop_table("users")
