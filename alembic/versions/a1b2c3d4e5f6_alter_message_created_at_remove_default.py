"""alter_message_created_at_remove_default

Revision ID: a1b2c3d4e5f6
Revises: 8a5930249a03
Create Date: 2026-06-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '8a5930249a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('message', 'created_at', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('message', 'created_at', server_default=sa.text('now()'))