"""add message client_msg_id

Revision ID: b7c3d4e5f6a8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c3d4e5f6a8'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'message',
        sa.Column('client_msg_id', sa.String(length=36), nullable=True),
    )
    op.create_index(
        'uq_message_chat_client_msg_id',
        'message',
        ['chat_id', 'client_msg_id'],
        unique=True,
        postgresql_where=sa.text('client_msg_id IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_message_chat_client_msg_id', table_name='message')
    op.drop_column('message', 'client_msg_id')
