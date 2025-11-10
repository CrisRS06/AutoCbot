"""Add user_settings table with encrypted API keys

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-10 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create user_settings table for per-user configuration with encrypted API keys.

    This addresses P0-2 and P0-3 from the system quality audit:
    - Migrates from global JSON file to per-user database storage
    - Implements encryption for sensitive API keys using Fernet
    """
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),

        # API Keys (ENCRYPTED) - stored as Text to accommodate encrypted strings
        sa.Column('binance_api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('binance_secret_encrypted', sa.Text(), nullable=True),
        sa.Column('coingecko_api_key_encrypted', sa.Text(), nullable=True),
        sa.Column('telegram_token_encrypted', sa.Text(), nullable=True),
        sa.Column('telegram_chat_id_encrypted', sa.Text(), nullable=True),

        # Trading Parameters
        sa.Column('default_pairs', sa.String(500), default='BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT'),
        sa.Column('default_timeframe', sa.String(10), default='5m'),
        sa.Column('max_position_size', sa.Float(), default=0.1),
        sa.Column('max_open_trades', sa.Integer(), default=5),

        # Risk Management
        sa.Column('default_stoploss', sa.Float(), default=-0.05),
        sa.Column('default_takeprofit', sa.Float(), default=0.03),

        # Feature Flags (per-user)
        sa.Column('enable_ml_predictions', sa.Boolean(), default=True),
        sa.Column('enable_paper_trading', sa.Boolean(), default=True),
        sa.Column('dry_run', sa.Boolean(), default=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now()),
    )

    # Create index on user_id for fast lookups
    op.create_index('ix_user_settings_user_id', 'user_settings', ['user_id'], unique=True)


def downgrade() -> None:
    """
    Drop user_settings table and revert to global JSON file storage.

    WARNING: This will delete all per-user settings data!
    """
    op.drop_index('ix_user_settings_user_id', table_name='user_settings')
    op.drop_table('user_settings')
