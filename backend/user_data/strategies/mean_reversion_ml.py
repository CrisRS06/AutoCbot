"""
Mean Reversion Strategy with LightGBM ML Filter
Combines technical indicators with ML probability predictions
"""

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import joblib
import numpy as np
from pathlib import Path
import sys
import os

# Add strategies directory to path for importing features
sys.path.insert(0, str(Path(__file__).parent))

class MeanReversionML(IStrategy):

    INTERFACE_VERSION = 3
    timeframe = '5m'
    can_short = False

    minimal_roi = {"0": 0.10, "20": 0.05, "40": 0.03, "60": 0.01}
    stoploss = -0.05
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True
    startup_candle_count = 200

    # ML probability threshold
    ml_threshold = 0.60

    def __init__(self, config: dict) -> None:
        super().__init__(config)

        # Load trained model
        model_path = Path("user_data/models/mean_reversion_lgb.pkl")
        if model_path.exists():
            self.model = joblib.load(model_path)
            self.logger.info("ML model loaded successfully")
        else:
            self.logger.warning("ML model not found - using rules only")
            self.model = None

        # Load feature list
        feature_path = Path("user_data/models/feature_list.txt")
        if feature_path.exists():
            with open(feature_path, 'r') as f:
                self.feature_columns = [line.strip() for line in f.readlines()]
        else:
            self.feature_columns = []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Calculate ALL features needed for ML model
        from features import create_features
        dataframe = create_features(dataframe)

        # Add ML predictions if model available
        if self.model is not None and len(self.feature_columns) > 0:
            try:
                # Prepare features
                X = dataframe[self.feature_columns].fillna(0)

                # Get predictions
                predictions = self.model.predict_proba(X)[:, 1]
                dataframe['ml_probability'] = predictions

            except Exception as e:
                self.logger.error(f"ML prediction error: {e}")
                dataframe['ml_probability'] = 0.5  # Neutral if error
        else:
            dataframe['ml_probability'] = 0.5  # Neutral if no model

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # BASE RULES (Technical indicators)
        base_conditions = (
            (dataframe['adx'] < 25) &
            (dataframe['close'] < dataframe['bb_lower']) &
            (dataframe['rsi_14'] < 30) &
            (dataframe['zscore_20'] < -2.0) &
            (dataframe['volume_ratio_20'] > 1.0) &
            (dataframe['volume'] > 0)
        )

        # ML FILTER (Only enter if ML predicts high probability)
        ml_filter = (dataframe['ml_probability'] > self.ml_threshold)

        # COMBINED: Base rules AND ML confirmation
        dataframe.loc[
            (base_conditions & ml_filter),
            ['enter_long', 'enter_tag']
        ] = (1, 'ml_mean_revert')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                ((dataframe['close'] >= dataframe['bb_middle']) &
                 (dataframe['rsi_14'] > 70)) |
                (dataframe['zscore_20'] > 0) |
                (dataframe['adx'] > 35)
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'mean_reached_ml')

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return self.stoploss

        last_candle = dataframe.iloc[-1].squeeze()

        # ATR-based stops
        if current_profit < 0:
            atr_stop = -(last_candle['atr'] / current_rate) * 2.5
            return max(atr_stop, -0.05)

        # Profit protection
        if current_profit > 0.05:
            return 0.01
        elif current_profit > 0.03:
            return -0.01
        elif current_profit > 0.01:
            return -0.02

        return -0.03
