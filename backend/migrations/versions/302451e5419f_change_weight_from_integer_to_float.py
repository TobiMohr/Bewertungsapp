"""change weight from integer to float

Revision ID: 302451e5419f
Revises: d8278200de53
Create Date: 2025-10-27 18:33:32.488318

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '302451e5419f'
down_revision: Union[str, Sequence[str], None] = 'd8278200de53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'session_criteria_association',
        'weight',
        type_=sa.Float(),
        existing_type=sa.Integer(),
        existing_nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'session_criteria_association',
        'weight',
        type_=sa.Integer(),
        existing_type=sa.Float(),
        existing_nullable=False
    )
