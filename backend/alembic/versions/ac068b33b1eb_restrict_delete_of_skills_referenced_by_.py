"""Restrict delete of skills referenced by job_skills

Revision ID: ac068b33b1eb
Revises: 30aed2408c80
Create Date: 2026-01-25 16:32:11.566176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac068b33b1eb'
down_revision: Union[str, Sequence[str], None] = '30aed2408c80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
