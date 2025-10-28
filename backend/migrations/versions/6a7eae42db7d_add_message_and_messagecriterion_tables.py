"""Add Message and MessageCriterion tables

Revision ID: 6a7eae42db7d
Revises: 7324b5c60296
Create Date: 2025-10-28 10:35:31.542781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a7eae42db7d'
down_revision: Union[str, Sequence[str], None] = '7324b5c60296'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('channel', sa.String(), nullable=True),
        sa.Column('message_id', sa.String(), nullable=True, unique=True),
        sa.Column('channel_id', sa.String(), nullable=True),
        sa.Column('sent_at', sa.String(), nullable=True),
        sa.Column('platform', sa.String(), nullable=True),
        sa.Column('roles', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('comment', sa.String(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True)
    )

    # Create message_criteria table
    op.create_table(
        'message_criteria',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=False),
        sa.Column('criterion_id', sa.Integer(), sa.ForeignKey('criteria.id'), nullable=False),
        sa.Column('reviewed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('count_value', sa.Integer(), nullable=True),
        sa.Column('is_fulfilled', sa.Boolean(), nullable=True),
        sa.Column('text_value', sa.String(), nullable=True),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('message_criteria')
    op.drop_table('messages')
