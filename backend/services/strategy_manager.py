"""
Strategy Manager Service - Database-backed version
"""

import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.models import Strategy, StrategyType
from models.schemas import StrategyConfig

logger = logging.getLogger(__name__)


class StrategyManager:
    """Manages trading strategies with database persistence"""

    def __init__(self, db: Session = None):
        """
        Initialize StrategyManager

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def _strategy_to_config(self, strategy: Strategy) -> StrategyConfig:
        """Convert database Strategy model to StrategyConfig schema"""
        params = strategy.parameters or {}
        return StrategyConfig(
            name=strategy.name,
            enabled=strategy.is_active,
            pairs=params.get("pairs", []),
            timeframe=params.get("timeframe", "1h"),
            stake_amount=params.get("stake_amount", 100.0),
            stop_loss=params.get("stop_loss", -0.05),
            take_profit=params.get("take_profit", 0.10),
            max_open_trades=params.get("max_open_trades", 5),
            trailing_stop=params.get("trailing_stop", False),
            use_ml=params.get("use_ml", False),
            use_sentiment=params.get("use_sentiment", False),
            min_confidence=params.get("min_confidence", 0.6)
        )

    def _config_to_strategy_params(self, config: StrategyConfig) -> Dict:
        """Extract parameters from StrategyConfig for database storage"""
        # Build parameters dict from StrategyConfig fields
        parameters = {
            "pairs": config.pairs,
            "timeframe": config.timeframe,
            "stake_amount": config.stake_amount,
            "stop_loss": config.stop_loss,
            "take_profit": config.take_profit,
            "max_open_trades": config.max_open_trades,
            "trailing_stop": config.trailing_stop,
            "use_ml": config.use_ml,
            "use_sentiment": config.use_sentiment,
            "min_confidence": config.min_confidence
        }

        return {
            "name": config.name,
            "type": StrategyType.CUSTOM,  # Default to CUSTOM since type is not in StrategyConfig
            "description": f"Strategy: {config.name}",
            "parameters": parameters,
            "is_active": config.enabled
        }

    async def list_strategies(self, user_id: int, include_deleted: bool = False) -> List[StrategyConfig]:
        """
        List all strategies for a specific user

        Args:
            user_id: User ID to filter strategies
            include_deleted: Include soft-deleted strategies

        Returns:
            List of StrategyConfig objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            query = self.db.query(Strategy).filter(Strategy.user_id == user_id)
            if not include_deleted:
                query = query.filter(Strategy.is_deleted == False)

            strategies = query.all()
            return [self._strategy_to_config(s) for s in strategies]

        except Exception as e:
            logger.error(f"Error listing strategies for user {user_id}: {e}")
            return []

    async def get_strategy(self, name: str, user_id: int) -> Optional[StrategyConfig]:
        """
        Get strategy by name for a specific user

        Args:
            name: Strategy name
            user_id: User ID to verify ownership

        Returns:
            StrategyConfig or None
        """
        if not self.db:
            logger.warning("No database session available")
            return None

        try:
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == name,
                    Strategy.user_id == user_id,
                    Strategy.is_deleted == False
                )
            ).first()

            if strategy:
                return self._strategy_to_config(strategy)
            return None

        except Exception as e:
            logger.error(f"Error getting strategy {name} for user {user_id}: {e}")
            return None

    async def get_strategy_by_id(self, strategy_id: int) -> Optional[StrategyConfig]:
        """
        Get strategy by ID

        Args:
            strategy_id: Strategy database ID

        Returns:
            StrategyConfig or None
        """
        if not self.db:
            logger.warning("No database session available")
            return None

        try:
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.id == strategy_id,
                    Strategy.is_deleted == False
                )
            ).first()

            if strategy:
                return self._strategy_to_config(strategy)
            return None

        except Exception as e:
            logger.error(f"Error getting strategy by ID {strategy_id}: {e}")
            return None

    async def save_strategy(self, config: StrategyConfig, user_id: int) -> StrategyConfig:
        """
        Save or update strategy for a specific user

        Args:
            config: StrategyConfig to save
            user_id: User ID to associate with strategy

        Returns:
            Saved StrategyConfig
        """
        if not self.db:
            logger.warning("No database session available")
            raise ValueError("Database session not available")

        try:
            # Check if strategy exists for this user
            existing = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == config.name,
                    Strategy.user_id == user_id,
                    Strategy.is_deleted == False
                )
            ).first()

            if existing:
                # Update existing strategy
                params = self._config_to_strategy_params(config)
                for key, value in params.items():
                    setattr(existing, key, value)

                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated strategy: {config.name} for user {user_id}")
                return self._strategy_to_config(existing)
            else:
                # Create new strategy
                params = self._config_to_strategy_params(config)
                params['user_id'] = user_id  # Associate with user
                new_strategy = Strategy(**params)

                self.db.add(new_strategy)
                self.db.commit()
                self.db.refresh(new_strategy)
                logger.info(f"Created new strategy: {config.name} for user {user_id}")
                return self._strategy_to_config(new_strategy)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving strategy {config.name} for user {user_id}: {e}")
            raise

    async def toggle_strategy(self, name: str, user_id: int) -> StrategyConfig:
        """
        Enable/disable strategy for a specific user

        Args:
            name: Strategy name
            user_id: User ID to verify ownership

        Returns:
            Updated StrategyConfig

        Raises:
            ValueError: If strategy not found or user doesn't own it
        """
        if not self.db:
            raise ValueError("Database session not available")

        try:
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == name,
                    Strategy.user_id == user_id,
                    Strategy.is_deleted == False
                )
            ).first()

            if not strategy:
                raise ValueError(f"Strategy {name} not found for user {user_id}")

            strategy.is_active = not strategy.is_active
            self.db.commit()
            self.db.refresh(strategy)

            logger.info(f"Toggled strategy {name} for user {user_id}: active={strategy.is_active}")
            return self._strategy_to_config(strategy)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling strategy {name} for user {user_id}: {e}")
            raise

    async def delete_strategy(self, name: str, user_id: int, hard_delete: bool = False) -> Dict:
        """
        Delete strategy for a specific user (soft delete by default)

        Args:
            name: Strategy name
            user_id: User ID to verify ownership
            hard_delete: If True, permanently delete from database

        Returns:
            Dict with success status
        """
        if not self.db:
            return {"success": False, "error": "Database session not available"}

        try:
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == name,
                    Strategy.user_id == user_id
                )
            ).first()

            if not strategy:
                return {"success": False, "error": "Strategy not found for user"}

            if hard_delete:
                # Permanently delete
                self.db.delete(strategy)
                logger.info(f"Hard deleted strategy: {name} for user {user_id}")
            else:
                # Soft delete
                strategy.is_deleted = True
                strategy.is_active = False
                logger.info(f"Soft deleted strategy: {name} for user {user_id}")

            self.db.commit()
            return {"success": True}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting strategy {name} for user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_active_strategies(self, user_id: int) -> List[StrategyConfig]:
        """
        Get all active (enabled) strategies for a specific user

        Args:
            user_id: User ID to filter strategies

        Returns:
            List of active StrategyConfig objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            strategies = self.db.query(Strategy).filter(
                and_(
                    Strategy.user_id == user_id,
                    Strategy.is_active == True,
                    Strategy.is_deleted == False
                )
            ).all()

            return [self._strategy_to_config(s) for s in strategies]

        except Exception as e:
            logger.error(f"Error getting active strategies for user {user_id}: {e}")
            return []
