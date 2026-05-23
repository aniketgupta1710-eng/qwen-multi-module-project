import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app.strategies.builder import StrategyBuilder

def test_strategy_builder():
    df = pd.DataFrame({
        'close': [10, 12, 11, 15, 14],
        'SMA_50': [11, 11, 11, 11, 11]
    })

    # We want to buy when close crosses above SMA_50
    # Day 0: 10 vs 11 -> Below
    # Day 1: 12 vs 11 -> Cross Above! (Buy)
    # Day 2: 11 vs 11 -> Equal (Not cross above)
    # Day 3: 15 vs 11 -> Above (Not cross above)

    builder = StrategyBuilder(df)

    buy_rules = [{"type": "cross_above", "series1": "close", "series2": "SMA_50"}]
    sell_rules = [{"type": "less_than", "series1": "close", "value": 12}]

    result_df = builder.generate_signals(buy_rules, sell_rules)

    assert result_df['buy_signal'].iloc[1] == True
    assert result_df['buy_signal'].iloc[0] == False
    assert result_df['buy_signal'].iloc[2] == False

    assert result_df['sell_signal'].iloc[0] == True
    assert result_df['sell_signal'].iloc[1] == False
    assert result_df['sell_signal'].iloc[2] == True
