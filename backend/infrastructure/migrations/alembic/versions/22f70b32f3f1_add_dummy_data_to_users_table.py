"""Add dummy data to users table

Revision ID: 22f70b32f3f1
Revises: 73dafa634170
Create Date: 2026-08-08 02:29:25.268758

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22f70b32f3f1"
down_revision: str | Sequence[str] | None = "73dafa634170"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO users (id, version, username) VALUES
        (1, 1, 'user1'),
        (2, 1, 'user2'),
        (3, 1, 'user3'),
        (4, 1, 'user4'),
        (5, 1, 'user5')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM users WHERE id IN (1, 2, 3, 4, 5);
    """)
