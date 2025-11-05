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
        return StrategyConfig(
            name=strategy.name,
            type=strategy.type.value,
            enabled=strategy.is_active,
            parameters=strategy.parameters or {}
        )

    def _config_to_strategy_params(self, config: StrategyConfig) -> Dict:
        """Extract parameters from StrategyConfig for database storage"""
        return {
            "name": config.name,
            "type": StrategyType[config.type.upper()] if hasattr(StrategyType, config.type.upper()) else StrategyType.CUSTOM,
            "description": config.parameters.get("description", ""),
            "parameters": config.parameters,
            "is_active": config.enabled
        }

    async def list_strategies(self, include_deleted: bool = False) -> List[StrategyConfig]:
        """
        List all strategies

        Args:
            include_deleted: Include soft-deleted strategies

        Returns:
            List of StrategyConfig objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            query = self.db.query(Strategy)
            if not include_deleted:
                query = query.filter(Strategy.is_deleted == False)

            strategies = query.all()
            return [self._strategy_to_config(s) for s in strategies]

        except Exception as e:
            logger.error(f"Error listing strategies: {e}")
            return []

    async def get_strategy(self, name: str) -> Optional[StrategyConfig]:
        """
        Get strategy by name

        Args:
            name: Strategy name

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
                    Strategy.is_deleted == False
                )
            ).first()

            if strategy:
                return self._strategy_to_config(strategy)
            return None

        except Exception as e:
            logger.error(f"Error getting strategy {name}: {e}")
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

    async def save_strategy(self, config: StrategyConfig) -> StrategyConfig:
        """
        Save or update strategy

        Args:
            config: StrategyConfig to save

        Returns:
            Saved StrategyConfig
        """
        if not self.db:
            logger.warning("No database session available")
            raise ValueError("Database session not available")

        try:
            # Check if strategy exists
            existing = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == config.name,
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
                logger.info(f"Updated strategy: {config.name}")
                return self._strategy_to_config(existing)
            else:
                # Create new strategy
                params = self._config_to_strategy_params(config)
                new_strategy = Strategy(**params)

                self.db.add(new_strategy)
                self.db.commit()
                self.db.refresh(new_strategy)
                logger.info(f"Created new strategy: {config.name}")
                return self._strategy_to_config(new_strategy)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving strategy {config.name}: {e}")
            raise

    async def toggle_strategy(self, name: str) -> StrategyConfig:
        """
        Enable/disable strategy

        Args:
            name: Strategy name

        Returns:
            Updated StrategyConfig

        Raises:
            ValueError: If strategy not found
        """
        if not self.db:
            raise ValueError("Database session not available")

        try:
            strategy = self.db.query(Strategy).filter(
                and_(
                    Strategy.name == name,
                    Strategy.is_deleted == False
                )
            ).first()

            if not strategy:
                raise ValueError(f"Strategy {name} not found")

            strategy.is_active = not strategy.is_active
            self.db.commit()
            self.db.refresh(strategy)

            logger.info(f"Toggled strategy {name}: active={strategy.is_active}")
            return self._strategy_to_config(strategy)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling strategy {name}: {e}")
            raise

    async def delete_strategy(self, name: str, hard_delete: bool = False) -> Dict:
        """
        Delete strategy (soft delete by default)

        Args:
            name: Strategy name
            hard_delete: If True, permanently delete from database

        Returns:
            Dict with success status
        """
        if not self.db:
            return {"success": False, "error": "Database session not available"}

        try:
            strategy = self.db.query(Strategy).filter(
                Strategy.name == name
            ).first()

            if not strategy:
                return {"success": False, "error": "Strategy not found"}

            if hard_delete:
                # Permanently delete
                self.db.delete(strategy)
                logger.info(f"Hard deleted strategy: {name}")
            else:
                # Soft delete
                strategy.is_deleted = True
                strategy.is_active = False
                logger.info(f"Soft deleted strategy: {name}")

            self.db.commit()
            return {"success": True}

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting strategy {name}: {e}")
            return {"success": False, "error": str(e)}

    async def get_active_strategies(self) -> List[StrategyConfig]:
        """
        Get all active (enabled) strategies

        Returns:
            List of active StrategyConfig objects
        """
        if not self.db:
            logger.warning("No database session available")
            return []

        try:
            strategies = self.db.query(Strategy).filter(
                and_(
                    Strategy.is_active == True,
                    Strategy.is_deleted == False
                )
            ).all()

            return [self._strategy_to_config(s) for s in strategies]

        except Exception as e:
            logger.error(f"Error getting active strategies: {e}")
            return []
