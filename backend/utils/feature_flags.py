"""
Feature Flags for AutoCbot MVP
Allows enabling/disabling features without code changes
"""
import os
from typing import Optional


class FeatureFlags:
    """
    Feature flags configuration for MVP
    Default values are MVP-safe (most features disabled)
    """

    def __init__(self):
        # ML and Advanced Features
        self.enable_ml_strategy: bool = self._get_bool("FEATURE_ENABLE_ML_STRATEGY", False)
        self.enable_sentiment_analysis: bool = self._get_bool("FEATURE_ENABLE_SENTIMENT_ANALYSIS", False)

        # Trading Features
        self.enable_backtest: bool = self._get_bool("FEATURE_ENABLE_BACKTEST", False)
        self.enable_custom_strategies: bool = self._get_bool("FEATURE_ENABLE_CUSTOM_STRATEGIES", False)
        self.enable_multi_exchange: bool = self._get_bool("FEATURE_ENABLE_MULTI_EXCHANGE", False)

        # Notifications
        self.enable_telegram: bool = self._get_bool("FEATURE_ENABLE_TELEGRAM", False)
        self.enable_email: bool = self._get_bool("FEATURE_ENABLE_EMAIL", False)
        self.enable_sms: bool = self._get_bool("FEATURE_ENABLE_SMS", False)

        # Analytics
        self.enable_advanced_metrics: bool = self._get_bool("FEATURE_ENABLE_ADVANCED_METRICS", False)
        self.enable_tax_calculator: bool = self._get_bool("FEATURE_ENABLE_TAX_CALCULATOR", False)

        # External Integrations
        self.enable_coingecko: bool = self._get_bool("FEATURE_ENABLE_COINGECKO", True)  # Free API, keep enabled
        self.enable_lunarcrush: bool = self._get_bool("FEATURE_ENABLE_LUNARCRUSH", False)
        self.enable_glassnode: bool = self._get_bool("FEATURE_ENABLE_GLASSNODE", False)

        # Live Trading (CRITICAL - must be explicitly enabled)
        self.enable_live_trading: bool = self._get_bool("FEATURE_ENABLE_LIVE_TRADING", False)

        # Development/Debug
        self.enable_debug_mode: bool = self._get_bool("FEATURE_ENABLE_DEBUG_MODE", False)

    def _get_bool(self, key: str, default: bool) -> bool:
        """
        Get boolean environment variable

        Args:
            key: Environment variable name
            default: Default value if not set

        Returns:
            Boolean value
        """
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    def to_dict(self) -> dict:
        """
        Convert flags to dictionary for API response

        Returns:
            Dictionary of all flags
        """
        return {
            "ml_strategy": self.enable_ml_strategy,
            "sentiment_analysis": self.enable_sentiment_analysis,
            "backtest": self.enable_backtest,
            "custom_strategies": self.enable_custom_strategies,
            "multi_exchange": self.enable_multi_exchange,
            "telegram": self.enable_telegram,
            "email": self.enable_email,
            "sms": self.enable_sms,
            "advanced_metrics": self.enable_advanced_metrics,
            "tax_calculator": self.enable_tax_calculator,
            "coingecko": self.enable_coingecko,
            "lunarcrush": self.enable_lunarcrush,
            "glassnode": self.enable_glassnode,
            "live_trading": self.enable_live_trading,
            "debug_mode": self.enable_debug_mode,
        }


# Global instance
flags = FeatureFlags()
