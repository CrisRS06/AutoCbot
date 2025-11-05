"""
Risk Manager Service
Manages trading risk, position sizing, and portfolio limits
"""

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskLimits:
    """Risk management limits configuration"""
    max_position_size_pct: float = 0.10  # Max 10% of portfolio per position
    max_portfolio_risk_pct: float = 0.02  # Max 2% portfolio risk per trade
    max_total_exposure_pct: float = 0.95  # Max 95% of portfolio can be exposed
    max_open_positions: int = 10  # Maximum number of concurrent positions
    max_drawdown_pct: float = 0.20  # Max 20% drawdown before stopping
    min_risk_reward_ratio: float = 1.5  # Minimum risk/reward ratio
    default_stop_loss_pct: float = 0.02  # Default 2% stop-loss
    default_take_profit_pct: float = 0.04  # Default 4% take-profit (2:1 R/R)


@dataclass
class PositionSize:
    """Position sizing calculation result"""
    quantity: float
    entry_price: float
    stop_loss_price: float
    take_profit_price: Optional[float]
    position_value: float
    risk_amount: float
    risk_pct: float
    reward_amount: Optional[float]
    risk_reward_ratio: Optional[float]
    approved: bool
    rejection_reason: Optional[str] = None


@dataclass
class PortfolioRisk:
    """Portfolio risk metrics"""
    total_value: float
    available_balance: float
    total_exposure: float
    exposure_pct: float
    open_positions: int
    total_risk_amount: float
    total_risk_pct: float
    can_open_position: bool
    reason: Optional[str] = None


class RiskManager:
    """
    Risk Manager for trading operations
    Handles position sizing, stop-loss/take-profit calculation, and portfolio risk management
    """

    def __init__(self, limits: Optional[RiskLimits] = None):
        """
        Initialize Risk Manager

        Args:
            limits: Risk limits configuration (uses defaults if not provided)
        """
        self.limits = limits or RiskLimits()
        logger.info(f"Risk Manager initialized with limits: {self.limits}")

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        portfolio_value: float,
        risk_pct: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> PositionSize:
        """
        Calculate position size based on risk parameters

        Args:
            entry_price: Entry price for the position
            stop_loss_price: Stop-loss price
            portfolio_value: Total portfolio value
            risk_pct: Risk percentage (default: use limits.max_portfolio_risk_pct)
            take_profit_price: Optional take-profit price

        Returns:
            PositionSize with calculated values and approval status
        """
        if risk_pct is None:
            risk_pct = self.limits.max_portfolio_risk_pct

        # Ensure risk percentage is within limits
        if risk_pct > self.limits.max_portfolio_risk_pct:
            logger.warning(f"Risk {risk_pct*100}% exceeds limit {self.limits.max_portfolio_risk_pct*100}%")
            risk_pct = self.limits.max_portfolio_risk_pct

        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss_price)

        if risk_per_unit == 0:
            return PositionSize(
                quantity=0,
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                position_value=0,
                risk_amount=0,
                risk_pct=0,
                reward_amount=None,
                risk_reward_ratio=None,
                approved=False,
                rejection_reason="Stop-loss price equals entry price"
            )

        # Calculate maximum risk amount in dollars
        max_risk_amount = portfolio_value * risk_pct

        # Calculate position size
        quantity = max_risk_amount / risk_per_unit

        # Calculate position value
        position_value = quantity * entry_price

        # Check if position size exceeds maximum position size limit
        max_position_value = portfolio_value * self.limits.max_position_size_pct

        if position_value > max_position_value:
            # Scale down quantity to meet position size limit
            quantity = max_position_value / entry_price
            position_value = quantity * entry_price
            actual_risk_amount = quantity * risk_per_unit
            actual_risk_pct = actual_risk_amount / portfolio_value
        else:
            actual_risk_amount = max_risk_amount
            actual_risk_pct = risk_pct

        # Calculate reward if take-profit is provided
        reward_amount = None
        risk_reward_ratio = None

        if take_profit_price:
            reward_per_unit = abs(take_profit_price - entry_price)
            reward_amount = quantity * reward_per_unit
            risk_reward_ratio = reward_amount / actual_risk_amount if actual_risk_amount > 0 else 0

            # Check minimum risk/reward ratio
            if risk_reward_ratio < self.limits.min_risk_reward_ratio:
                return PositionSize(
                    quantity=quantity,
                    entry_price=entry_price,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    position_value=position_value,
                    risk_amount=actual_risk_amount,
                    risk_pct=actual_risk_pct,
                    reward_amount=reward_amount,
                    risk_reward_ratio=risk_reward_ratio,
                    approved=False,
                    rejection_reason=f"Risk/Reward ratio {risk_reward_ratio:.2f} below minimum {self.limits.min_risk_reward_ratio}"
                )

        # Position approved
        return PositionSize(
            quantity=quantity,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            position_value=position_value,
            risk_amount=actual_risk_amount,
            risk_pct=actual_risk_pct,
            reward_amount=reward_amount,
            risk_reward_ratio=risk_reward_ratio,
            approved=True
        )

    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        stop_loss_pct: Optional[float] = None
    ) -> float:
        """
        Calculate stop-loss price

        Args:
            entry_price: Entry price
            side: Trade side ('buy' or 'sell')
            stop_loss_pct: Stop-loss percentage (default: use limits.default_stop_loss_pct)

        Returns:
            Stop-loss price
        """
        if stop_loss_pct is None:
            stop_loss_pct = self.limits.default_stop_loss_pct

        if side.lower() == 'buy':
            # For long positions, stop-loss below entry
            stop_loss = entry_price * (1 - stop_loss_pct)
        else:
            # For short positions, stop-loss above entry
            stop_loss = entry_price * (1 + stop_loss_pct)

        return stop_loss

    def calculate_take_profit(
        self,
        entry_price: float,
        side: str,
        take_profit_pct: Optional[float] = None,
        risk_reward_ratio: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> float:
        """
        Calculate take-profit price

        Args:
            entry_price: Entry price
            side: Trade side ('buy' or 'sell')
            take_profit_pct: Take-profit percentage (if provided, uses this directly)
            risk_reward_ratio: Risk/reward ratio (if provided with stop_loss_price, calculates TP based on R/R)
            stop_loss_price: Stop-loss price (required if using risk_reward_ratio)

        Returns:
            Take-profit price
        """
        # Method 1: Use risk/reward ratio
        if risk_reward_ratio and stop_loss_price:
            risk_per_unit = abs(entry_price - stop_loss_price)
            reward_per_unit = risk_per_unit * risk_reward_ratio

            if side.lower() == 'buy':
                take_profit = entry_price + reward_per_unit
            else:
                take_profit = entry_price - reward_per_unit

            return take_profit

        # Method 2: Use percentage
        if take_profit_pct is None:
            take_profit_pct = self.limits.default_take_profit_pct

        if side.lower() == 'buy':
            # For long positions, take-profit above entry
            take_profit = entry_price * (1 + take_profit_pct)
        else:
            # For short positions, take-profit below entry
            take_profit = entry_price * (1 - take_profit_pct)

        return take_profit

    def assess_portfolio_risk(
        self,
        portfolio_value: float,
        available_balance: float,
        open_positions: List[Dict],
        new_position_value: Optional[float] = None
    ) -> PortfolioRisk:
        """
        Assess current portfolio risk and determine if new position can be opened

        Args:
            portfolio_value: Total portfolio value
            available_balance: Available balance (not in positions)
            open_positions: List of open positions with 'value' and 'risk_amount' keys
            new_position_value: Value of new position to open (optional)

        Returns:
            PortfolioRisk with assessment results
        """
        # Calculate current exposure
        total_position_value = sum(p.get('value', 0) for p in open_positions)
        total_exposure = total_position_value
        exposure_pct = total_exposure / portfolio_value if portfolio_value > 0 else 0

        # Calculate total risk
        total_risk_amount = sum(p.get('risk_amount', 0) for p in open_positions)
        total_risk_pct = total_risk_amount / portfolio_value if portfolio_value > 0 else 0

        num_positions = len(open_positions)

        # If checking for new position
        if new_position_value is not None:
            # Check max positions limit
            if num_positions >= self.limits.max_open_positions:
                return PortfolioRisk(
                    total_value=portfolio_value,
                    available_balance=available_balance,
                    total_exposure=total_exposure,
                    exposure_pct=exposure_pct,
                    open_positions=num_positions,
                    total_risk_amount=total_risk_amount,
                    total_risk_pct=total_risk_pct,
                    can_open_position=False,
                    reason=f"Maximum positions limit reached ({self.limits.max_open_positions})"
                )

            # Check exposure limit
            new_total_exposure = total_exposure + new_position_value
            new_exposure_pct = new_total_exposure / portfolio_value

            if new_exposure_pct > self.limits.max_total_exposure_pct:
                return PortfolioRisk(
                    total_value=portfolio_value,
                    available_balance=available_balance,
                    total_exposure=total_exposure,
                    exposure_pct=exposure_pct,
                    open_positions=num_positions,
                    total_risk_amount=total_risk_amount,
                    total_risk_pct=total_risk_pct,
                    can_open_position=False,
                    reason=f"Exposure limit exceeded ({new_exposure_pct*100:.1f}% > {self.limits.max_total_exposure_pct*100:.1f}%)"
                )

            # Check available balance
            if new_position_value > available_balance:
                return PortfolioRisk(
                    total_value=portfolio_value,
                    available_balance=available_balance,
                    total_exposure=total_exposure,
                    exposure_pct=exposure_pct,
                    open_positions=num_positions,
                    total_risk_amount=total_risk_amount,
                    total_risk_pct=total_risk_pct,
                    can_open_position=False,
                    reason=f"Insufficient balance (need ${new_position_value:.2f}, have ${available_balance:.2f})"
                )

        # All checks passed
        return PortfolioRisk(
            total_value=portfolio_value,
            available_balance=available_balance,
            total_exposure=total_exposure,
            exposure_pct=exposure_pct,
            open_positions=num_positions,
            total_risk_amount=total_risk_amount,
            total_risk_pct=total_risk_pct,
            can_open_position=True
        )

    def validate_trade(
        self,
        entry_price: float,
        stop_loss_price: Optional[float],
        take_profit_price: Optional[float],
        quantity: float,
        portfolio_value: float,
        available_balance: float,
        open_positions: List[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a trade against all risk management rules

        Args:
            entry_price: Entry price
            stop_loss_price: Stop-loss price
            take_profit_price: Take-profit price
            quantity: Position quantity
            portfolio_value: Total portfolio value
            available_balance: Available balance
            open_positions: List of open positions

        Returns:
            Tuple of (approved: bool, rejection_reason: Optional[str])
        """
        position_value = quantity * entry_price

        # Check portfolio risk
        portfolio_risk = self.assess_portfolio_risk(
            portfolio_value=portfolio_value,
            available_balance=available_balance,
            open_positions=open_positions,
            new_position_value=position_value
        )

        if not portfolio_risk.can_open_position:
            return False, portfolio_risk.reason

        # Check position size if stop-loss provided
        if stop_loss_price:
            position_size = self.calculate_position_size(
                entry_price=entry_price,
                stop_loss_price=stop_loss_price,
                portfolio_value=portfolio_value,
                take_profit_price=take_profit_price
            )

            if not position_size.approved:
                return False, position_size.rejection_reason

        return True, None

    def get_limits(self) -> RiskLimits:
        """Get current risk limits"""
        return self.limits

    def update_limits(self, **kwargs):
        """
        Update risk limits

        Args:
            **kwargs: Risk limit parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.limits, key):
                setattr(self.limits, key, value)
                logger.info(f"Updated risk limit {key} = {value}")
            else:
                logger.warning(f"Unknown risk limit parameter: {key}")
