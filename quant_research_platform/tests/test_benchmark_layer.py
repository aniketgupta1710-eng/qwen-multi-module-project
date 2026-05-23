import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app.benchmark.engine import BenchmarkEngine

def test_benchmark_engine():
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'close': [100, 110]
    })

    # Capital 1000. Price 100 -> 10 shares.
    # Day 2 price 110 -> 10 * 110 = 1100.

    metrics = BenchmarkEngine.calculate_buy_and_hold(df, initial_capital=1000.0)

    assert metrics['B&H Total Return'] == pytest.approx(0.1)
    assert metrics['B&H Final Equity'] == 1100
    assert 'B&H Equity Curve' in metrics
