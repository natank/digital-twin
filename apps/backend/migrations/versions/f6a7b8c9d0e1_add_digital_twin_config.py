"""add digital_twin_configs and prompt_versions

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-20

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "digital_twin_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("system_prompt", sa.String(), nullable=False),
        sa.Column("tone", sa.String(length=32), nullable=False),
        sa.Column("response_length", sa.String(length=32), nullable=False),
        sa.Column("allowed_topics", sa.JSON(), nullable=True),
        sa.Column("forbidden_topics", sa.JSON(), nullable=True),
        sa.Column("brand_guidelines", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["owners.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id"),
    )
    op.create_index(
        op.f("ix_digital_twin_configs_owner_id"),
        "digital_twin_configs",
        ["owner_id"],
        unique=True,
    )

    op.create_table(
        "prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("config_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("system_prompt", sa.String(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["config_id"], ["digital_twin_configs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prompt_versions_config_id"), "prompt_versions", ["config_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_prompt_versions_config_id"), table_name="prompt_versions")
    op.drop_table("prompt_versions")
    op.drop_index(
        op.f("ix_digital_twin_configs_owner_id"), table_name="digital_twin_configs"
    )
    op.drop_table("digital_twin_configs")
