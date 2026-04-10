"""create core tables

Revision ID: 0001_create_core_tables
Revises:
Create Date: 2026-04-10 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_create_core_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("image", sa.String(length=255), nullable=False),
        sa.Column("internal_port", sa.Integer(), nullable=False),
        sa.Column("assigned_port", sa.Integer(), nullable=True),
        sa.Column("container_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_apps_id"), "apps", ["id"], unique=False)

    op.create_table(
        "deployments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("app_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["app_id"], ["apps.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deployments_id"), "deployments", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_deployments_id"), table_name="deployments")
    op.drop_table("deployments")
    op.drop_index(op.f("ix_apps_id"), table_name="apps")
    op.drop_table("apps")
