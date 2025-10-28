"""Add username to User (default to email)

Revision ID: 7324b5c60296
Revises: 302451e5419f
Create Date: 2025-10-28 10:13:33.177835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7324b5c60296'
down_revision: Union[str, Sequence[str], None] = '302451e5419f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column 'username' as nullable first
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Fill existing users with a default value (using email)
    op.execute("UPDATE users SET username = email")
    
    # Alter column to set nullable=False
    op.alter_column('users', 'username', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index on 'username'
    op.drop_index(op.f('ix_users_username'), table_name='users')
    
    # Drop column 'username'
    op.drop_column('users', 'username')
