"""
Advanced Trading Metrics Calculations
Implements professional-grade metrics for backtesting and performance analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Union
import logging

logger = logging.getLogger(__name__)


def calculate_returns(equity_curve: Union[List[float], pd.Series]) -> pd.Series:
    """
    Calculate returns from equity curve

    Args:
        equity_curve: List or Series of equity values

    Returns:
        Series of returns
    """
    if isinstance(equity_curve, list):
        equity_curve = pd.Series(equity_curve)

    return equity_curve.pct_change().dropna()


def calculate_sharpe_ratio(
    returns: Union[List[float], pd.Series],
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe Ratio

    Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns

    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate (default 2%)
        periods_per_year: Trading periods per year (252 for daily, 252*24 for hourly)

    Returns:
        Sharpe ratio (annualized)
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    # Convert annual risk-free rate to period rate
    period_risk_free_rate = risk_free_rate / periods_per_year

    excess_returns = returns - period_risk_free_rate

    if excess_returns.std() == 0:
        return 0.0

    sharpe = excess_returns.mean() / excess_returns.std()

    # Annualize
    sharpe_annualized = sharpe * np.sqrt(periods_per_year)

    return float(sharpe_annualized)


def calculate_sortino_ratio(
    returns: Union[List[float], pd.Series],
    target_return: float = 0.0,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sortino Ratio (focuses only on downside deviation)

    Sortino Ratio = (Mean Return - Target Return) / Downside Deviation

    Args:
        returns: Series of returns
        target_return: Minimum acceptable return (default 0)
        periods_per_year: Trading periods per year

    Returns:
        Sortino ratio (annualized)
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    # Calculate downside returns (only negative returns)
    downside_returns = returns[returns < target_return]

    if len(downside_returns) == 0:
        return 0.0

    # Downside deviation
    downside_std = downside_returns.std()

    if downside_std == 0:
        return 0.0

    sortino = (returns.mean() - target_return) / downside_std

    # Annualize
    sortino_annualized = sortino * np.sqrt(periods_per_year)

    return float(sortino_annualized)


def calculate_max_drawdown(equity_curve: Union[List[float], pd.Series]) -> Dict[str, float]:
    """
    Calculate Maximum Drawdown and related metrics

    Args:
        equity_curve: List or Series of equity values

    Returns:
        Dict with max_drawdown, max_drawdown_duration, recovery_factor
    """
    if isinstance(equity_curve, list):
        equity_curve = pd.Series(equity_curve)

    if len(equity_curve) == 0:
        return {
            "max_drawdown": 0.0,
            "max_drawdown_duration": 0,
            "max_drawdown_date": None,
            "recovery_date": None
        }

    # Calculate running maximum
    running_max = equity_curve.expanding().max()

    # Calculate drawdown
    drawdown = (equity_curve - running_max) / running_max

    # Maximum drawdown
    max_dd = float(drawdown.min())

    # Find max drawdown date
    max_dd_date = drawdown.idxmin() if hasattr(drawdown, 'idxmin') else None

    # Calculate drawdown duration
    # Find periods where we're in drawdown
    in_drawdown = drawdown < 0

    max_duration = 0
    current_duration = 0
    recovery_date = None

    for i, is_dd in enumerate(in_drawdown):
        if is_dd:
            current_duration += 1
            max_duration = max(max_duration, current_duration)
        else:
            if current_duration > 0:
                recovery_date = equity_curve.index[i] if hasattr(equity_curve, 'index') else i
            current_duration = 0

    return {
        "max_drawdown": max_dd,
        "max_drawdown_duration": max_duration,
        "max_drawdown_date": max_dd_date,
        "recovery_date": recovery_date
    }


def calculate_calmar_ratio(
    returns: Union[List[float], pd.Series],
    equity_curve: Union[List[float], pd.Series],
    periods_per_year: int = 252
) -> float:
    """
    Calculate Calmar Ratio

    Calmar Ratio = Annualized Return / Maximum Drawdown

    Args:
        returns: Series of returns
        equity_curve: Equity curve for drawdown calculation
        periods_per_year: Trading periods per year

    Returns:
        Calmar ratio
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    # Annualized return
    mean_return = returns.mean()
    annualized_return = mean_return * periods_per_year

    # Max drawdown (absolute value)
    dd_metrics = calculate_max_drawdown(equity_curve)
    max_dd = abs(dd_metrics["max_drawdown"])

    if max_dd == 0:
        return 0.0

    calmar = annualized_return / max_dd

    return float(calmar)


def calculate_profit_factor(wins: List[float], losses: List[float]) -> float:
    """
    Calculate Profit Factor

    Profit Factor = Gross Profit / Gross Loss

    Args:
        wins: List of winning trade P&Ls
        losses: List of losing trade P&Ls (should be negative)

    Returns:
        Profit factor
    """
    if not wins or not losses:
        return 0.0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0

    return gross_profit / gross_loss


def calculate_expectancy(
    win_rate: float,
    avg_win: float,
    avg_loss: float
) -> float:
    """
    Calculate Expectancy (expected value per trade)

    Expectancy = (Win Rate * Avg Win) - (Loss Rate * Avg Loss)

    Args:
        win_rate: Win rate (0-1)
        avg_win: Average winning trade
        avg_loss: Average losing trade (absolute value)

    Returns:
        Expectancy per trade
    """
    loss_rate = 1 - win_rate
    expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))

    return float(expectancy)


def calculate_var(
    returns: Union[List[float], pd.Series],
    confidence: float = 0.95
) -> float:
    """
    Calculate Value at Risk (VaR)

    VaR estimates the maximum loss over a given time period at a given confidence level

    Args:
        returns: Series of returns
        confidence: Confidence level (default 95%)

    Returns:
        VaR value (negative indicates loss)
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    var = np.percentile(returns, (1 - confidence) * 100)

    return float(var)


def calculate_cvar(
    returns: Union[List[float], pd.Series],
    confidence: float = 0.95
) -> float:
    """
    Calculate Conditional Value at Risk (CVaR) / Expected Shortfall

    CVaR is the expected loss given that the loss exceeds VaR

    Args:
        returns: Series of returns
        confidence: Confidence level (default 95%)

    Returns:
        CVaR value (negative indicates loss)
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    var = calculate_var(returns, confidence)

    # Get returns worse than VaR
    tail_returns = returns[returns <= var]

    if len(tail_returns) == 0:
        return var

    cvar = tail_returns.mean()

    return float(cvar)


def calculate_omega_ratio(
    returns: Union[List[float], pd.Series],
    threshold: float = 0.0
) -> float:
    """
    Calculate Omega Ratio

    Omega Ratio = Probability-weighted ratio of gains vs losses relative to threshold

    Args:
        returns: Series of returns
        threshold: Return threshold (default 0)

    Returns:
        Omega ratio
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    # Returns above threshold
    gains = returns[returns > threshold] - threshold
    # Returns below threshold
    losses = threshold - returns[returns < threshold]

    if len(losses) == 0 or losses.sum() == 0:
        return float('inf') if len(gains) > 0 else 0.0

    omega = gains.sum() / losses.sum()

    return float(omega)


def calculate_recovery_factor(
    total_return: float,
    max_drawdown: float
) -> float:
    """
    Calculate Recovery Factor

    Recovery Factor = Total Return / Maximum Drawdown

    Args:
        total_return: Total return (as decimal, e.g., 0.5 for 50%)
        max_drawdown: Maximum drawdown (as decimal, e.g., -0.2 for -20%)

    Returns:
        Recovery factor
    """
    max_dd_abs = abs(max_drawdown)

    if max_dd_abs == 0:
        return 0.0

    recovery = total_return / max_dd_abs

    return float(recovery)


def calculate_tail_ratio(returns: Union[List[float], pd.Series]) -> float:
    """
    Calculate Tail Ratio

    Tail Ratio = 95th percentile / abs(5th percentile)
    Measures the ratio of right tail (gains) to left tail (losses)

    Args:
        returns: Series of returns

    Returns:
        Tail ratio
    """
    if isinstance(returns, list):
        returns = pd.Series(returns)

    if len(returns) == 0:
        return 0.0

    right_tail = np.percentile(returns, 95)
    left_tail = abs(np.percentile(returns, 5))

    if left_tail == 0:
        return 0.0

    tail_ratio = right_tail / left_tail

    return float(tail_ratio)


def calculate_all_metrics(
    equity_curve: Union[List[float], pd.Series],
    trades: List[Dict],
    initial_capital: float,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> Dict[str, Union[float, int]]:
    """
    Calculate all performance metrics

    Args:
        equity_curve: Series of equity values
        trades: List of trade dictionaries with 'pnl' key
        initial_capital: Starting capital
        risk_free_rate: Annual risk-free rate
        periods_per_year: Trading periods per year

    Returns:
        Dictionary with all metrics
    """
    if isinstance(equity_curve, list):
        equity_curve = pd.Series(equity_curve)

    # Basic metrics
    total_trades = len(trades)

    if total_trades == 0:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_return": 0.0,
            "total_return_pct": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_duration": 0,
            "calmar_ratio": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "largest_win": 0.0,
            "largest_loss": 0.0,
            "recovery_factor": 0.0,
            "var_95": 0.0,
            "cvar_95": 0.0,
            "omega_ratio": 0.0,
            "tail_ratio": 0.0
        }

    # Separate wins and losses
    wins = [t['pnl'] for t in trades if t['pnl'] > 0]
    losses = [t['pnl'] for t in trades if t['pnl'] < 0]

    winning_trades = len(wins)
    losing_trades = len(losses)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

    # P&L metrics
    gross_profit = sum(wins) if wins else 0.0
    gross_loss = sum(losses) if losses else 0.0
    net_profit = gross_profit + gross_loss

    avg_win = np.mean(wins) if wins else 0.0
    avg_loss = np.mean(losses) if losses else 0.0
    largest_win = max(wins) if wins else 0.0
    largest_loss = min(losses) if losses else 0.0

    # Total return
    final_value = equity_curve.iloc[-1] if len(equity_curve) > 0 else initial_capital
    total_return = final_value - initial_capital
    total_return_pct = total_return / initial_capital if initial_capital > 0 else 0.0

    # Calculate returns series
    returns = calculate_returns(equity_curve)

    # Advanced metrics
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year)
    sortino = calculate_sortino_ratio(returns, 0.0, periods_per_year)

    dd_metrics = calculate_max_drawdown(equity_curve)
    max_dd = dd_metrics["max_drawdown"]
    max_dd_duration = dd_metrics["max_drawdown_duration"]

    calmar = calculate_calmar_ratio(returns, equity_curve, periods_per_year)
    profit_factor = calculate_profit_factor(wins, losses) if wins and losses else 0.0
    expectancy = calculate_expectancy(win_rate, avg_win, abs(avg_loss))
    recovery = calculate_recovery_factor(total_return_pct, max_dd)

    var_95 = calculate_var(returns, 0.95)
    cvar_95 = calculate_cvar(returns, 0.95)
    omega = calculate_omega_ratio(returns, 0.0)
    tail = calculate_tail_ratio(returns)

    return {
        # Basic metrics
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": float(win_rate),

        # Returns
        "gross_profit": float(gross_profit),
        "gross_loss": float(gross_loss),
        "net_profit": float(net_profit),
        "total_return": float(total_return),
        "total_return_pct": float(total_return_pct),

        # Risk-adjusted metrics
        "sharpe_ratio": float(sharpe),
        "sortino_ratio": float(sortino),
        "calmar_ratio": float(calmar),
        "omega_ratio": float(omega),

        # Drawdown
        "max_drawdown": float(max_dd),
        "max_drawdown_duration": int(max_dd_duration),
        "recovery_factor": float(recovery),

        # Trade metrics
        "profit_factor": float(profit_factor),
        "expectancy": float(expectancy),
        "avg_win": float(avg_win),
        "avg_loss": float(avg_loss),
        "largest_win": float(largest_win),
        "largest_loss": float(largest_loss),

        # Risk metrics
        "var_95": float(var_95),
        "cvar_95": float(cvar_95),
        "tail_ratio": float(tail)
    }
