"""add tasks

Revision ID: 73dafa634170
Revises: dabc93d3e41b
Create Date: 2026-08-02 12:13:46.287960

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlmodel import ForeignKey

# revision identifiers, used by Alembic.
revision: str = "73dafa634170"
down_revision: str | Sequence[str] | None = "dabc93d3e41b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = "dabc93d3e41b"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tasks",
        sa.Column("id", sa.BIGINT, autoincrement=False, primary_key=True),
        sa.Column("version", sa.Integer),
        sa.Column("name", sa.Text),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("completed", sa.Boolean),
        sa.Column("user_id", sa.BIGINT, ForeignKey("users.id"), autoincrement=False),
        if_not_exists=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tasks", schema="public")
