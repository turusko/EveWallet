"""phase 2 wallet journal, rules, sync jobs, and order extensions"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_phase2"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "wallet_journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("journal_ref_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ref_type", sa.String(length=80), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("tax", sa.Numeric(18, 2), nullable=True),
        sa.Column("tax_receiver_id", sa.BigInteger(), nullable=True),
        sa.Column("context_id", sa.BigInteger(), nullable=True),
        sa.Column("context_id_type", sa.String(length=80), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("first_party_id", sa.BigInteger(), nullable=True),
        sa.Column("second_party_id", sa.BigInteger(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_wallet_journal_entries_date", "wallet_journal_entries", ["date"])

    op.create_table(
        "assignment_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("stop_processing", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("conditions_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("job_type", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("details_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.add_column("market_orders", sa.Column("is_history", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("market_orders", sa.Column("state", sa.String(length=50), nullable=True))
    op.add_column("market_orders", sa.Column("volume_filled", sa.Integer(), nullable=True))
    op.add_column("market_orders", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("market_orders", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))

    op.execute("ALTER TYPE source_type_enum ADD VALUE IF NOT EXISTS 'wallet_journal'")
    op.add_column("bucket_assignments", sa.Column("assignment_method", sa.String(length=20), nullable=False, server_default="manual"))
    op.add_column("bucket_assignments", sa.Column("assignment_rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assignment_rules.id"), nullable=True))


def downgrade() -> None:
    op.drop_column("bucket_assignments", "assignment_rule_id")
    op.drop_column("bucket_assignments", "assignment_method")

    op.drop_column("market_orders", "closed_at")
    op.drop_column("market_orders", "last_seen_at")
    op.drop_column("market_orders", "volume_filled")
    op.drop_column("market_orders", "state")
    op.drop_column("market_orders", "is_history")

    op.drop_table("sync_jobs")
    op.drop_table("assignment_rules")
    op.drop_index("ix_wallet_journal_entries_date", table_name="wallet_journal_entries")
    op.drop_table("wallet_journal_entries")
