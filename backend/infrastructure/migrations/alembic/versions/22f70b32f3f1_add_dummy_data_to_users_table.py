"""Add dummy data to users table

Revision ID: 22f70b32f3f1
Revises: 73dafa634170
Create Date: 2026-08-08 02:29:25.268758

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.sql.expression import text

from infrastructure.config import database_settings

# revision identifiers, used by Alembic.
revision: str = "22f70b32f3f1"
down_revision: str | Sequence[str] | None = "73dafa634170"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()

    params = (
        {
            "test1": database_settings.TEST1_AUTH0_ID,
            "test2": database_settings.TEST2_AUTH0_ID,
            "test3": database_settings.TEST3_AUTH0_ID,
        },
    )
    connection.execute(
        text("""
        INSERT INTO users (id, version, username, auth0_id) VALUES
        (1, 0, 'user1', :test1),
        (2, 0, 'user2', :test2),
        (2894388762935840, 0, 'j.tabac', :test3)
    """),
        params,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE FROM users WHERE id IN (1, 2, 2894388762935840);
    """)
