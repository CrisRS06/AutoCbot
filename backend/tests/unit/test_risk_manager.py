"""
Unit tests for Risk Manager
Tests position sizing, risk/reward validation, and portfolio risk assessment
"""

import pytest
from services.risk_manager import RiskManager, RiskLimits, PositionSize


class TestPositionSizing:
    """Test position sizing calculations"""

    def test_calculate_position_size_basic(self):
        """Test basic position sizing with 2% risk"""
        rm = RiskManager()
        position = rm.calculate_position_size(
            entry_price=50000,
            stop_loss_price=49000,  # 2% stop loss
            portfolio_value=10000,
            risk_pct=0.02  # Risk $200
        )

        assert position.approved is True
        assert abs(position.risk_amount - 200) < 1  # Risk $200
        assert abs(position.quantity - 0.2) < 0.01  # $200 / $1000 risk per unit
        assert position.risk_pct == pytest.approx(0.02)

    def test_calculate_position_size_exceeds_max(self):
        """Test that position size is capped at max_position_size_pct"""
        rm = RiskManager(RiskLimits(max_position_size_pct=0.05))

        # Tight stop loss would normally create large position
        position = rm.calculate_position_size(
            entry_price=50000,
            stop_loss_price=49500,  # 1% stop loss
            portfolio_value=10000,
            risk_pct=0.10  # Try to risk 10% = would need 20% of portfolio
        )

        # Should be scaled down to 5% max position size
        assert position.position_value <= 500  # 5% of $10k
        assert position.approved is True

    def test_stop_loss_equals_entry_price(self):
        """Test that zero risk per unit is rejected"""
        rm = RiskManager()
        position = rm.calculate_position_size(
            entry_price=50000,
            stop_loss_price=50000,  # Same as entry = no risk
            portfolio_value=10000
        )

        assert position.approved is False
        assert "equals entry price" in position.rejection_reason.lower()

    def test_risk_reward_ratio_validation(self):
        """Test that insufficient risk/reward ratio is rejected"""
        rm = RiskManager(RiskLimits(min_risk_reward_ratio=2.0))

        # 2% stop loss, 1% take profit = 0.5:1 R/R (below 2:1 minimum)
        position = rm.calculate_position_size(
            entry_price=50000,
            stop_loss_price=49000,  # 2% risk
            take_profit_price=50500,  # 1% reward
            portfolio_value=10000
        )

        assert position.approved is False
        assert "risk/reward ratio" in position.rejection_reason.lower()
        assert position.risk_reward_ratio < 1.0

    def test_good_risk_reward_ratio(self):
        """Test that good risk/reward ratio is approved"""
        rm = RiskManager(RiskLimits(min_risk_reward_ratio=1.5))

        # 2% stop loss, 4% take profit = 2:1 R/R
        position = rm.calculate_position_size(
            entry_price=50000,
            stop_loss_price=49000,  # 2% risk
            take_profit_price=52000,  # 4% reward
            portfolio_value=10000,
            risk_pct=0.02
        )

        assert position.approved is True
        assert position.risk_reward_ratio >= 1.5
        assert position.reward_amount > position.risk_amount


class TestStopLossTakeProfit:
    """Test stop loss and take profit calculations"""

    def test_calculate_stop_loss_long(self):
        """Test stop loss calculation for long position"""
        rm = RiskManager()
        stop_loss = rm.calculate_stop_loss(
            entry_price=50000,
            side="buy",
            stop_loss_pct=0.02
        )

        assert stop_loss == pytest.approx(49000)  # 2% below entry

    def test_calculate_stop_loss_short(self):
        """Test stop loss calculation for short position"""
        rm = RiskManager()
        stop_loss = rm.calculate_stop_loss(
            entry_price=50000,
            side="sell",
            stop_loss_pct=0.02
        )

        assert stop_loss == pytest.approx(51000)  # 2% above entry

    def test_calculate_take_profit_percentage(self):
        """Test take profit using percentage"""
        rm = RiskManager()
        take_profit = rm.calculate_take_profit(
            entry_price=50000,
            side="buy",
            take_profit_pct=0.05
        )

        assert take_profit == pytest.approx(52500)  # 5% above entry

    def test_calculate_take_profit_risk_reward_ratio(self):
        """Test take profit using risk/reward ratio"""
        rm = RiskManager()
        take_profit = rm.calculate_take_profit(
            entry_price=50000,
            side="buy",
            risk_reward_ratio=2.0,
            stop_loss_price=49000  # $1000 risk
        )

        # 2:1 R/R = $2000 reward = $52000 take profit
        assert take_profit == pytest.approx(52000)


class TestPortfolioRisk:
    """Test portfolio risk assessment"""

    def test_assess_portfolio_risk_max_positions(self):
        """Test max positions limit"""
        rm = RiskManager(RiskLimits(max_open_positions=3))

        # Already have 3 positions
        open_positions = [
            {"value": 1000, "risk_amount": 20},
            {"value": 1500, "risk_amount": 30},
            {"value": 2000, "risk_amount": 40}
        ]

        assessment = rm.assess_portfolio_risk(
            portfolio_value=10000,
            available_balance=5500,
            open_positions=open_positions,
            new_position_value=1000
        )

        assert assessment.can_open_position is False
        assert "maximum positions" in assessment.reason.lower()

    def test_assess_portfolio_risk_exposure_limit(self):
        """Test exposure percentage limit"""
        rm = RiskManager(RiskLimits(max_total_exposure_pct=0.80))

        # Already have 70% exposed
        open_positions = [
            {"value": 7000, "risk_amount": 140}
        ]

        # Trying to add another 20% would exceed 80% limit
        assessment = rm.assess_portfolio_risk(
            portfolio_value=10000,
            available_balance=3000,
            open_positions=open_positions,
            new_position_value=2000
        )

        assert assessment.can_open_position is False
        assert "exposure limit" in assessment.reason.lower()

    def test_assess_portfolio_risk_insufficient_balance(self):
        """Test insufficient balance check"""
        rm = RiskManager()

        open_positions = [
            {"value": 5000, "risk_amount": 100}
        ]

        # Only $5k available, trying to open $6k position
        assessment = rm.assess_portfolio_risk(
            portfolio_value=10000,
            available_balance=5000,
            open_positions=open_positions,
            new_position_value=6000
        )

        assert assessment.can_open_position is False
        assert "insufficient balance" in assessment.reason.lower()

    def test_assess_portfolio_risk_approved(self):
        """Test successful portfolio risk assessment"""
        rm = RiskManager()

        open_positions = [
            {"value": 2000, "risk_amount": 40}
        ]

        assessment = rm.assess_portfolio_risk(
            portfolio_value=10000,
            available_balance=8000,
            open_positions=open_positions,
            new_position_value=1000
        )

        assert assessment.can_open_position is True
        assert assessment.total_exposure == 2000
        assert assessment.exposure_pct == pytest.approx(0.2)
        assert assessment.open_positions == 1


class TestTradeValidation:
    """Test complete trade validation"""

    def test_validate_trade_success(self):
        """Test successful trade validation"""
        rm = RiskManager()

        approved, reason = rm.validate_trade(
            entry_price=50000,
            stop_loss_price=49000,
            take_profit_price=52000,
            quantity=0.1,
            portfolio_value=10000,
            available_balance=8000,
            open_positions=[]
        )

        assert approved is True
        assert reason is None

    def test_validate_trade_portfolio_limit(self):
        """Test trade rejection due to portfolio limits"""
        rm = RiskManager(RiskLimits(max_open_positions=1))

        # Already have 1 position
        approved, reason = rm.validate_trade(
            entry_price=50000,
            stop_loss_price=49000,
            take_profit_price=None,
            quantity=0.1,
            portfolio_value=10000,
            available_balance=5000,
            open_positions=[{"value": 5000, "risk_amount": 100}]
        )

        assert approved is False
        assert "maximum positions" in reason.lower()
