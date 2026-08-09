"""Add database initialization logic

Revision ID: dabc93d3e41b
Revises:
Create Date: 2026-07-24 01:13:51.740624

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dabc93d3e41b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema"""
    op.create_table(
        "users",
        sa.Column("id", sa.BIGINT, autoincrement=False, primary_key=True),
        sa.Column("version", sa.Integer),
        sa.Column("username", sa.Text, nullable=False),
        sa.Column("auth0_id", sa.Text, nullable=True, unique=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade database schema"""
    # Add any necessary downgrade logic here
    op.drop_table("users", schema="public")
