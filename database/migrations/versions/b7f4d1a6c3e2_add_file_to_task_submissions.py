"""add file attachment to group task submissions

Revision ID: b7f4d1a6c3e2
Revises: d3e9a2c7f158
Create Date: 2026-09-06 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f4d1a6c3e2'
down_revision: Union[str, None] = 'd3e9a2c7f158'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('group_task_submissions', sa.Column('file_name', sa.String(length=255), nullable=True))
    op.add_column('group_task_submissions', sa.Column('file_mime_type', sa.String(length=150), nullable=True))
    op.add_column('group_task_submissions', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('group_task_submissions', sa.Column('file_data', sa.LargeBinary(), nullable=True))
    # content used to be required; a submission can now be file-only.
    # batch_alter_table so this also works on SQLite (no ALTER COLUMN SET DEFAULT).
    with op.batch_alter_table('group_task_submissions') as batch_op:
        batch_op.alter_column('content', server_default='')


def downgrade() -> None:
    with op.batch_alter_table('group_task_submissions') as batch_op:
        batch_op.alter_column('content', server_default=None)
    op.drop_column('group_task_submissions', 'file_data')
    op.drop_column('group_task_submissions', 'file_size')
    op.drop_column('group_task_submissions', 'file_mime_type')
    op.drop_column('group_task_submissions', 'file_name')
