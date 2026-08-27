"""add groups

Revision ID: f4c3d8a1e7b2
Revises: e8f21b6a9c4d
Create Date: 2026-08-27 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4c3d8a1e7b2'
down_revision: Union[str, None] = 'e8f21b6a9c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'groups',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('teacher_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['teacher_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_groups_teacher_id'), 'groups', ['teacher_id'], unique=False)

    op.create_table(
        'group_members',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('group_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'student_id', name='uq_group_members_group_student'),
    )
    op.create_index(op.f('ix_group_members_group_id'), 'group_members', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_members_student_id'), 'group_members', ['student_id'], unique=False)

    op.create_table(
        'group_tasks',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('group_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_group_tasks_group_id'), 'group_tasks', ['group_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_group_tasks_group_id'), table_name='group_tasks')
    op.drop_table('group_tasks')
    op.drop_index(op.f('ix_group_members_student_id'), table_name='group_members')
    op.drop_index(op.f('ix_group_members_group_id'), table_name='group_members')
    op.drop_table('group_members')
    op.drop_index(op.f('ix_groups_teacher_id'), table_name='groups')
    op.drop_table('groups')
