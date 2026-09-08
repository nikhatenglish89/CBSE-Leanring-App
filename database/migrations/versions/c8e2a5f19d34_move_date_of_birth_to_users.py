"""move date_of_birth to users, add birthday-email tracking

Revision ID: c8e2a5f19d34
Revises: b7f4d1a6c3e2
Create Date: 2026-09-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8e2a5f19d34'
down_revision: Union[str, None] = 'b7f4d1a6c3e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('last_birthday_email_sent_on', sa.Date(), nullable=True))

    # date_of_birth was previously student-only and never had a UI to set
    # it, but carry over any value that exists rather than silently drop it.
    op.execute(
        """
        UPDATE users
        SET date_of_birth = student_profiles.date_of_birth
        FROM student_profiles
        WHERE student_profiles.user_id = users.id
          AND student_profiles.date_of_birth IS NOT NULL
        """
    )
    with op.batch_alter_table('student_profiles') as batch_op:
        batch_op.drop_column('date_of_birth')


def downgrade() -> None:
    with op.batch_alter_table('student_profiles') as batch_op:
        batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.execute(
        """
        UPDATE student_profiles
        SET date_of_birth = users.date_of_birth
        FROM users
        WHERE users.id = student_profiles.user_id
          AND users.date_of_birth IS NOT NULL
        """
    )
    op.drop_column('users', 'last_birthday_email_sent_on')
    op.drop_column('users', 'date_of_birth')
