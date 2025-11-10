"""Add token_blacklist table for token revocation

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-11-10 03:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, Sequence[str], None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create token_blacklist table for server-side token revocation.

    This addresses P1-5 from the system quality audit:
    - Implements proper logout with server-side token invalidation
    - Supports security-related token revocation
    - Enables audit trail of revoked tokens
    """
    op.create_table(
        'token_blacklist',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('token_jti', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('token_type', sa.String(20), nullable=False),

        # Expiration tracking
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False, index=True),

        # Timestamps and metadata
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('reason', sa.String(255), nullable=True),
    )

    # Create composite index for efficient lookups
    op.create_index('idx_token_jti_expires', 'token_blacklist', ['token_jti', 'expires_at'])


def downgrade() -> None:
    """
    Drop token_blacklist table.

    WARNING: This will remove all token revocation data!
    Logged out users will be able to use their old tokens again.
    """
    op.drop_index('idx_token_jti_expires', table_name='token_blacklist')
    op.drop_table('token_blacklist')
