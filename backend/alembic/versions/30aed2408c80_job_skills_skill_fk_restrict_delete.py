"""job_skills skill fk restrict delete

Revision ID: 30aed2408c80
Revises: 71183d75c8f9
Create Date: 2026-01-25 16:23:20.031786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30aed2408c80'
down_revision: Union[str, Sequence[str], None] = '71183d75c8f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing FK (currently CASCADE)
    op.drop_constraint(
        "job_skills_skill_id_fkey",
        "job_skills",
        type_="foreignkey",
    )

    # Recreate FK with RESTRICT
    op.create_foreign_key(
        "job_skills_skill_id_fkey",
        source_table="job_skills",
        referent_table="skills",
        local_cols=["skill_id"],
        remote_cols=["id"],
        ondelete="RESTRICT"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert back to CASCADE
    op.drop_constraint(
        "job_skills_skill_id_fkey",
        "job_skills",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "job_skills_skill_id_fkey",
        source_table="job_skills",
        referent_table="skills",
        local_cols=["skill_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )
