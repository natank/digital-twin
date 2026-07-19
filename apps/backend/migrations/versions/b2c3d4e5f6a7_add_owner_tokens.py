"""add owner_tokens table for verify/reset flows

Revision ID: b2c3d4e5f6a7
Revises: efc842b1f7de
Create Date: 2026-07-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "efc842b1f7de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "owner_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_type", sa.String(length=32), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["owners.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_owner_tokens_owner_id"), "owner_tokens", ["owner_id"], unique=False)
    op.create_index(op.f("ix_owner_tokens_token_hash"), "owner_tokens", ["token_hash"], unique=True)
    op.create_index(
        op.f("ix_owner_tokens_token_type"), "owner_tokens", ["token_type"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_owner_tokens_token_type"), table_name="owner_tokens")
    op.drop_index(op.f("ix_owner_tokens_token_hash"), table_name="owner_tokens")
    op.drop_index(op.f("ix_owner_tokens_owner_id"), table_name="owner_tokens")
    op.drop_table("owner_tokens")
