"""
Mean Reversion Base Strategy - Complete Implementation
Optimized for 5-minute crypto trading on Binance
"""

from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
from datetime import datetime
import talib.abstract as ta
import numpy as np

class MeanReversionBase(IStrategy):

    INTERFACE_VERSION = 3
    timeframe = '5m'
    can_short = False

    minimal_roi = {
        "0": 0.10,
        "20": 0.05,
        "40": 0.03,
        "60": 0.01
    }

    stoploss = -0.05
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    startup_candle_count = 200

    # Hyperparameters
    bb_period = IntParameter(15, 25, default=20, space='buy')
    bb_std = DecimalParameter(1.5, 2.5, default=2.0, space='buy')
    buy_rsi_period = IntParameter(7, 21, default=14, space='buy')
    buy_rsi = IntParameter(20, 35, default=30, space='buy')
    sell_rsi = IntParameter(60, 80, default=70, space='sell')
    zscore_period = IntParameter(20, 50, default=30, space='buy')
    adx_period = IntParameter(10, 20, default=14, space='buy')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe, timeperiod=self.bb_period.value,
                              nbdevup=self.bb_std.value, nbdevdn=self.bb_std.value)
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=self.buy_rsi_period.value)

        # Z-Score
        dataframe['price_mean'] = dataframe['close'].rolling(self.zscore_period.value).mean()
        dataframe['price_std'] = dataframe['close'].rolling(self.zscore_period.value).std()
        dataframe['zscore'] = (dataframe['close'] - dataframe['price_mean']) / dataframe['price_std']

        # ADX (trend filter)
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=self.adx_period.value)

        # ATR (for stops)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)

        # Volume
        dataframe['volume_ma'] = dataframe['volume'].rolling(20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']

        # Moving averages for context
        dataframe['sma_200'] = ta.SMA(dataframe, timeperiod=200)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['adx'] < 25) &                          # Not trending
                (dataframe['close'] < dataframe['bb_lower']) &     # Below lower BB
                (dataframe['rsi'] < self.buy_rsi.value) &          # Oversold
                (dataframe['zscore'] < -2.0) &                     # 2 SD below mean
                (dataframe['volume_ratio'] > 1.0) &                # Volume confirmation
                (dataframe['close'] > dataframe['sma_200']) &      # Above long-term MA
                (dataframe['bb_width'] > 0.02) &                   # Sufficient volatility
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'enter_tag']
        ] = (1, 'mean_revert_oversold')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (
                    (dataframe['close'] >= dataframe['bb_middle']) &
                    (dataframe['rsi'] > self.sell_rsi.value)
                ) |
                (dataframe['zscore'] > 0) |
                (dataframe['adx'] > 35)  # Strong trend developing
            ),
            ['exit_long', 'exit_tag']
        ] = (1, 'mean_reached')

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty:
            return self.stoploss

        last_candle = dataframe.iloc[-1].squeeze()

        # ATR-based stop for losing trades
        if current_profit < 0:
            atr_stop = -(last_candle['atr'] / current_rate) * 2.5
            return max(atr_stop, -0.05)

        # Tighten stops as profit increases
        if current_profit > 0.05:
            return 0.01
        elif current_profit > 0.03:
            return -0.01
        elif current_profit > 0.01:
            return -0.02

        return -0.03
