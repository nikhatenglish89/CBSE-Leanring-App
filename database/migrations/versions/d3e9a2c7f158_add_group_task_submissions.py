"""add group task submissions

Revision ID: d3e9a2c7f158
Revises: a1c9f3e7b5d0
Create Date: 2026-09-05 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e9a2c7f158'
down_revision: Union[str, None] = 'a1c9f3e7b5d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'group_task_submissions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['group_tasks.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'student_id', name='uq_task_submissions_task_student'),
    )
    op.create_index(
        op.f('ix_group_task_submissions_task_id'), 'group_task_submissions', ['task_id'], unique=False
    )
    op.create_index(
        op.f('ix_group_task_submissions_student_id'), 'group_task_submissions', ['student_id'], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_group_task_submissions_student_id'), table_name='group_task_submissions')
    op.drop_index(op.f('ix_group_task_submissions_task_id'), table_name='group_task_submissions')
    op.drop_table('group_task_submissions')
