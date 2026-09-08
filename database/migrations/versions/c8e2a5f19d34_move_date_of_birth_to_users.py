"""move date_of_birth to users, add birthday-email tracking

Revision ID: c8e2a5f19d34
Revises: b7f4d1a6c3e2
Create Date: 2026-09-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'c8e2a5f19d34'
down_revision: Union[str, None] = 'b7f4d1a6c3e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotent by inspecting current column state rather than assuming a
    # clean starting point — this migration previously failed partway
    # through on production Postgres (the raw UPDATE...FROM below), and
    # since alembic runs a migration in one transaction, the whole thing
    # rolled back silently, leaving the DB on the old schema while the
    # deployed code already expected the new one. Safe to retry from any
    # partial state now.
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {col["name"] for col in inspector.get_columns("users")}

    if "date_of_birth" not in user_columns:
        op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    if "last_birthday_email_sent_on" not in user_columns:
        op.add_column('users', sa.Column('last_birthday_email_sent_on', sa.Date(), nullable=True))

    student_columns = {col["name"] for col in inspector.get_columns("student_profiles")}
    if "date_of_birth" in student_columns:
        # Dropped without copying data over first: date_of_birth was
        # student-only and never had any UI to set it before this feature,
        # so in practice this column is NULL for every existing row.
        with op.batch_alter_table('student_profiles') as batch_op:
            batch_op.drop_column('date_of_birth')


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    student_columns = {col["name"] for col in inspector.get_columns("student_profiles")}
    if "date_of_birth" not in student_columns:
        with op.batch_alter_table('student_profiles') as batch_op:
            batch_op.add_column(sa.Column('date_of_birth', sa.Date(), nullable=True))

    user_columns = {col["name"] for col in inspector.get_columns("users")}
    if "last_birthday_email_sent_on" in user_columns:
        op.drop_column('users', 'last_birthday_email_sent_on')
    if "date_of_birth" in user_columns:
        op.drop_column('users', 'date_of_birth')
