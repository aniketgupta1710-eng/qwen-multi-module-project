import pandas as pd
import numpy as np
from typing import Dict, Any

class MetricsEngine:
    """Calculates performance metrics from backtest results."""

    @staticmethod
    def calculate_metrics(df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """Calculates standard metrics like CAGR, Drawdown, etc."""
        if df.empty or 'equity' not in df.columns:
            return {}

        equity = df['equity']
        final_equity = equity.iloc[-1]

        # Total Return
        total_return = (final_equity / initial_capital) - 1

        # Calculate Drawdown
        roll_max = equity.cummax()
        drawdown = (equity - roll_max) / roll_max
        max_drawdown = drawdown.min()

        # Calculate CAGR (Assuming daily data for this basic calculation)
        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days if 'date' in df.columns else len(df)
        years = days / 365.25

        if years > 0:
            cagr = (final_equity / initial_capital) ** (1 / years) - 1
        else:
            cagr = 0.0

        return {
            "Total Return": total_return,
            "CAGR": cagr,
            "Max Drawdown": max_drawdown,
            "Final Equity": final_equity,
            "Drawdown Curve": drawdown
        }
