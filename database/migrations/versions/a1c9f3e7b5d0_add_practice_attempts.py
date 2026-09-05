"""add practice attempts

Revision ID: a1c9f3e7b5d0
Revises: f4c3d8a1e7b2
Create Date: 2026-09-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c9f3e7b5d0'
down_revision: Union[str, None] = 'f4c3d8a1e7b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'practice_attempts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('practice_set_id', sa.Uuid(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('total', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.ForeignKeyConstraint(['practice_set_id'], ['practice_sets.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_practice_attempts_student_id'), 'practice_attempts', ['student_id'], unique=False)
    op.create_index(
        op.f('ix_practice_attempts_practice_set_id'), 'practice_attempts', ['practice_set_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_practice_attempts_practice_set_id'), table_name='practice_attempts')
    op.drop_index(op.f('ix_practice_attempts_student_id'), table_name='practice_attempts')
    op.drop_table('practice_attempts')
