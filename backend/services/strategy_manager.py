"""Strategy Manager Service"""

import logging
from typing import List, Optional, Dict
from models.schemas import StrategyConfig

logger = logging.getLogger(__name__)


class StrategyManager:
    """Manages trading strategies"""

    def __init__(self):
        self.strategies: Dict[str, StrategyConfig] = {}

    async def list_strategies(self) -> List[StrategyConfig]:
        """List all strategies"""
        return list(self.strategies.values())

    async def get_strategy(self, name: str) -> Optional[StrategyConfig]:
        """Get strategy by name"""
        return self.strategies.get(name)

    async def save_strategy(self, config: StrategyConfig) -> StrategyConfig:
        """Save or update strategy"""
        self.strategies[config.name] = config
        return config

    async def toggle_strategy(self, name: str) -> StrategyConfig:
        """Enable/disable strategy"""
        if name in self.strategies:
            self.strategies[name].enabled = not self.strategies[name].enabled
            return self.strategies[name]
        raise ValueError(f"Strategy {name} not found")

    async def delete_strategy(self, name: str) -> Dict:
        """Delete strategy"""
        if name in self.strategies:
            del self.strategies[name]
            return {"success": True}
        return {"success": False, "error": "Strategy not found"}
