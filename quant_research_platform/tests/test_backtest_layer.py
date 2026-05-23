import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app.backtesting.engine import BacktestEngine
from app.metrics.engine import MetricsEngine

def test_backtest_engine():
    # Signals are on Close. Executed on next Open.
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04']),
        'open': [100, 110, 120, 130],
        'close': [105, 115, 125, 135],
        'buy_signal': [True, False, False, False],
        'sell_signal': [False, False, True, False]
    })

    engine = BacktestEngine(initial_capital=1000.0, brokerage_pct=0.0)
    results = engine.run(df)

    assert len(results['trade_log']) == 2 # 1 buy, 1 sell

    # Buy on Day 1 (index 1) open = 110. Capital=1000. Qty = 9. Cost = 990.
    assert results['trade_log'].iloc[0]['type'] == 'BUY'
    assert results['trade_log'].iloc[0]['price'] == 110

    # Sell on Day 3 (index 3) open = 130. Qty = 9. Revenue = 1170.
    assert results['trade_log'].iloc[1]['type'] == 'SELL'
    assert results['trade_log'].iloc[1]['price'] == 130

def test_metrics_engine():
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2024-01-01']),
        'equity': [1000, 1100]
    })

    metrics = MetricsEngine.calculate_metrics(df, initial_capital=1000.0)

    assert metrics['Total Return'] == pytest.approx(0.1)
    assert metrics['CAGR'] == pytest.approx(0.1, abs=0.01) # Approx 10% for 1 year
    assert metrics['Final Equity'] == 1100
