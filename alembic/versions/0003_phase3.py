"""phase 3 inventory, assets, industry, contracts"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0003_phase3"
down_revision = "0002_phase2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project_buckets", sa.Column("bucket_type", sa.String(length=64), nullable=True))
    op.add_column("project_buckets", sa.Column("accounting_mode", sa.String(length=32), nullable=False, server_default="fifo"))
    op.add_column("project_buckets", sa.Column("default_location_id", sa.BigInteger(), nullable=True))
    op.add_column("project_buckets", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column("bucket_assignments", sa.Column("locked", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.create_table(
        "character_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("asset_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("location_id", sa.BigInteger(), nullable=False),
        sa.Column("location_type", sa.String(length=64), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("location_flag", sa.String(length=64), nullable=True),
        sa.Column("quantity", sa.BigInteger(), nullable=False),
        sa.Column("is_singleton", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("item_id", sa.BigInteger(), nullable=True),
        sa.Column("blueprint_copy", sa.Boolean(), nullable=True),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=True),
        sa.Column("is_present", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "inventory_lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=True),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_uuid", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity_total", sa.Numeric(20, 4), nullable=False),
        sa.Column("quantity_remaining", sa.Numeric(20, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=False),
        sa.Column("total_cost", sa.Numeric(18, 2), nullable=False),
        sa.Column("location_id", sa.BigInteger(), nullable=True),
        sa.Column("location_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lot_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_lots.id"), nullable=False),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=True),
        sa.Column("movement_type", sa.String(length=32), nullable=False),
        sa.Column("ref_source_type", sa.String(length=32), nullable=False),
        sa.Column("ref_source_uuid", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 4), nullable=False),
        sa.Column("unit_value", sa.Numeric(18, 4), nullable=True),
        sa.Column("total_value", sa.Numeric(18, 2), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "industry_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("eve_job_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("blueprint_type_id", sa.BigInteger(), nullable=True),
        sa.Column("blueprint_type_name", sa.String(length=255), nullable=True),
        sa.Column("product_type_id", sa.BigInteger(), nullable=True),
        sa.Column("product_type_name", sa.String(length=255), nullable=True),
        sa.Column("station_id", sa.BigInteger(), nullable=True),
        sa.Column("station_name", sa.String(length=255), nullable=True),
        sa.Column("installer_id", sa.BigInteger(), nullable=True),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("runs", sa.Integer(), nullable=False),
        sa.Column("cost", sa.Numeric(18, 2), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("licensed_runs", sa.Integer(), nullable=True),
        sa.Column("successful_runs", sa.Integer(), nullable=True),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "industry_job_materials",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("industry_jobs.id"), nullable=False),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("quantity_required", sa.Numeric(20, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True),
        sa.Column("total_cost", sa.Numeric(18, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "industry_job_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("industry_jobs.id"), nullable=False),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("quantity_produced", sa.Numeric(20, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(18, 4), nullable=True),
        sa.Column("total_cost", sa.Numeric(18, 2), nullable=True),
        sa.Column("lot_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventory_lots.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("character_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("eve_characters.id"), nullable=False),
        sa.Column("contract_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("issuer_id", sa.BigInteger(), nullable=True),
        sa.Column("issuer_name", sa.String(length=255), nullable=True),
        sa.Column("assignee_id", sa.BigInteger(), nullable=True),
        sa.Column("acceptor_id", sa.BigInteger(), nullable=True),
        sa.Column("start_location_id", sa.BigInteger(), nullable=True),
        sa.Column("start_location_name", sa.String(length=255), nullable=True),
        sa.Column("end_location_id", sa.BigInteger(), nullable=True),
        sa.Column("end_location_name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("price", sa.Numeric(18, 2), nullable=True),
        sa.Column("reward", sa.Numeric(18, 2), nullable=True),
        sa.Column("collateral", sa.Numeric(18, 2), nullable=True),
        sa.Column("buyout", sa.Numeric(18, 2), nullable=True),
        sa.Column("volume", sa.Numeric(20, 4), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_accepted", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_completed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("bucket_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("project_buckets.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "contract_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("contract_fk", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id"), nullable=False),
        sa.Column("record_id", sa.BigInteger(), nullable=True),
        sa.Column("type_id", sa.BigInteger(), nullable=False),
        sa.Column("type_name", sa.String(length=255), nullable=True),
        sa.Column("quantity", sa.Numeric(20, 4), nullable=False),
        sa.Column("is_included", sa.Boolean(), nullable=False),
        sa.Column("is_singleton", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("raw_quantity", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "resolved_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("location_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("location_type", sa.String(length=64), nullable=False),
        sa.Column("resolved_name", sa.String(length=255), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("resolved_locations")
    op.drop_table("contract_items")
    op.drop_table("contracts")
    op.drop_table("industry_job_outputs")
    op.drop_table("industry_job_materials")
    op.drop_table("industry_jobs")
    op.drop_table("inventory_movements")
    op.drop_table("inventory_lots")
    op.drop_table("character_assets")
    op.drop_column("bucket_assignments", "locked")
    op.drop_column("project_buckets", "closed_at")
    op.drop_column("project_buckets", "default_location_id")
    op.drop_column("project_buckets", "accounting_mode")
    op.drop_column("project_buckets", "bucket_type")
