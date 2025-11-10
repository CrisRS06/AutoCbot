"""
Feature Engineering for Crypto Mean Reversion ML
Creates comprehensive feature set from OHLCV data
"""

import pandas as pd
import numpy as np
import ta

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create all features for ML model

    Args:
        df: DataFrame with OHLCV data

    Returns:
        DataFrame with engineered features
    """

    # Copy to avoid modifying original
    data = df.copy()

    # ========== PRICE FEATURES ==========
    # Returns
    data['returns'] = np.log(data['close'] / data['close'].shift(1))

    # Lag returns
    for lag in [1, 5, 10, 20]:
        data[f'return_lag_{lag}'] = data['returns'].shift(lag)

    # Price momentum
    for period in [5, 10, 20]:
        data[f'price_change_{period}'] = data['close'].pct_change(period)

    # ========== MOVING AVERAGES ==========
    for window in [5, 10, 20, 50, 200]:
        data[f'sma_{window}'] = ta.trend.sma_indicator(data['close'], window)
        data[f'ema_{window}'] = ta.trend.ema_indicator(data['close'], window)

    # Price-to-MA ratios
    for window in [20, 50]:
        data[f'price_sma_ratio_{window}'] = data['close'] / data[f'sma_{window}']

    # MA crossovers
    data['sma_20_50_cross'] = (data['sma_20'] > data['sma_50']).astype(int)

    # ========== VOLATILITY FEATURES ==========
    # Rolling volatility
    for window in [10, 20, 30]:
        data[f'volatility_{window}'] = data['returns'].rolling(window).std()
        data[f'volatility_pct_{window}'] = data[f'volatility_{window}'] / data['close']

    # Bollinger Bands
    bb_20 = ta.volatility.BollingerBands(data['close'], window=20, window_dev=2)
    data['bb_upper'] = bb_20.bollinger_hband()
    data['bb_lower'] = bb_20.bollinger_lband()
    data['bb_middle'] = bb_20.bollinger_mavg()
    data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
    data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])

    # ATR
    data['atr'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'])
    data['atr_pct'] = data['atr'] / data['close']

    # ========== MOMENTUM INDICATORS ==========
    # RSI
    data['rsi_14'] = ta.momentum.rsi(data['close'], window=14)
    data['rsi_7'] = ta.momentum.rsi(data['close'], window=7)

    # Stochastic
    stoch = ta.momentum.StochasticOscillator(data['high'], data['low'], data['close'])
    data['stoch_k'] = stoch.stoch()
    data['stoch_d'] = stoch.stoch_signal()

    # MACD
    macd = ta.trend.MACD(data['close'])
    data['macd'] = macd.macd()
    data['macd_signal'] = macd.macd_signal()
    data['macd_diff'] = macd.macd_diff()

    # ROC (Rate of Change)
    for period in [5, 10, 20]:
        data[f'roc_{period}'] = ta.momentum.roc(data['close'], period)

    # ========== VOLUME FEATURES ==========
    # Volume moving averages
    for period in [5, 10, 20]:
        data[f'volume_sma_{period}'] = data['volume'].rolling(period).mean()
        data[f'volume_ratio_{period}'] = data['volume'] / data[f'volume_sma_{period}']

    # OBV (On-Balance Volume)
    data['obv'] = ta.volume.on_balance_volume(data['close'], data['volume'])
    data['obv_sma_20'] = data['obv'].rolling(20).mean()

    # Volume-weighted average price
    data['vwap'] = (data['volume'] * (data['high'] + data['low'] + data['close']) / 3).cumsum() / data['volume'].cumsum()

    # ========== MEAN REVERSION FEATURES ==========
    # Z-scores
    for period in [10, 20, 30, 50]:
        mean = data['close'].rolling(period).mean()
        std = data['close'].rolling(period).std()
        data[f'zscore_{period}'] = (data['close'] - mean) / std
        data[f'distance_sma_{period}'] = (data['close'] - mean) / data['close']

    # ========== TREND FEATURES ==========
    # ADX
    adx = ta.trend.ADXIndicator(data['high'], data['low'], data['close'])
    data['adx'] = adx.adx()
    data['adx_pos'] = adx.adx_pos()
    data['adx_neg'] = adx.adx_neg()

    # ========== TIME FEATURES ==========
    if isinstance(data.index, pd.DatetimeIndex):
        data['hour'] = data.index.hour
        data['day_of_week'] = data.index.dayofweek
        data['month'] = data.index.month

    # ========== INTERACTION FEATURES ==========
    # RSI * Volume (oversold with volume = stronger signal)
    data['rsi_volume'] = data['rsi_14'] * data['volume_ratio_20']

    # BB position * ADX (mean reversion in ranging market)
    data['bb_pos_adx'] = data['bb_position'] * (25 - data['adx']).clip(lower=0)

    return data


def select_features(df: pd.DataFrame) -> list:
    """
    Select most important features for model

    Returns list of feature column names
    """

    features = [
        # Price momentum
        'returns', 'return_lag_1', 'return_lag_5', 'return_lag_10',
        'price_change_5', 'price_change_10', 'price_change_20',

        # Moving averages
        'price_sma_ratio_20', 'price_sma_ratio_50', 'sma_20_50_cross',

        # Volatility
        'volatility_20', 'volatility_pct_20', 'bb_width', 'bb_position', 'atr_pct',

        # Momentum indicators
        'rsi_14', 'rsi_7', 'stoch_k', 'macd_diff', 'roc_10',

        # Volume
        'volume_ratio_5', 'volume_ratio_20', 'obv',

        # Mean reversion
        'zscore_20', 'zscore_30', 'distance_sma_20',

        # Trend
        'adx', 'adx_pos', 'adx_neg',

        # Time
        'hour', 'day_of_week',

        # Interactions
        'rsi_volume', 'bb_pos_adx'
    ]

    # Filter to only include columns that exist
    available_features = [f for f in features if f in df.columns]

    return available_features
