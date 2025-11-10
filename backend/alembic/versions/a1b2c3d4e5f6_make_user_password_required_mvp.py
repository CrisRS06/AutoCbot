"""Make user password required for MVP

Revision ID: a1b2c3d4e5f6
Revises: 600c4339cb4f
Create Date: 2025-11-10 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '600c4339cb4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Make hashed_password column NOT NULL for MVP security requirements.

    Steps:
    1. Update any NULL passwords to a placeholder (should not exist in production)
    2. Alter column to NOT NULL

    Note: In production, ensure all users have valid passwords before running this.
    """
    # Step 1: Update any NULL passwords to a placeholder
    # This is a safety measure - in a proper migration, you'd want to handle this differently
    # For MVP, we enforce that all new users MUST have a password
    op.execute(
        """
        UPDATE users
        SET hashed_password = '$2b$12$INVALID_PASSWORD_PLACEHOLDER_DO_NOT_USE'
        WHERE hashed_password IS NULL
        """
    )

    # Step 2: Alter the column to NOT NULL
    # The exact syntax depends on the database backend
    # SQLite doesn't support ALTER COLUMN directly, so we need to recreate the table

    # For SQLite (development/MVP):
    # We need to recreate the table with the new constraint
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(length=255),
                              nullable=False,
                              existing_nullable=True)


def downgrade() -> None:
    """
    Revert hashed_password to nullable.

    This allows demo mode where users might not have passwords.
    """
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(length=255),
                              nullable=True,
                              existing_nullable=False)
