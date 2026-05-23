import pandas as pd
from typing import Dict, Any

class BenchmarkEngine:
    """Compares strategy performance against Buy and Hold."""

    @staticmethod
    def calculate_buy_and_hold(df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """Calculates buy and hold performance using the first and last close price."""
        if df.empty or 'close' not in df.columns:
            return {}

        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]

        # How many shares could we buy at the start?
        quantity = initial_capital / first_price
        final_value = quantity * last_price

        total_return = (final_value / initial_capital) - 1

        # Calculate B&H Drawdown
        equity_curve = df['close'] * quantity
        roll_max = equity_curve.cummax()
        drawdown = (equity_curve - roll_max) / roll_max
        max_drawdown = drawdown.min()

        days = (df['date'].iloc[-1] - df['date'].iloc[0]).days if 'date' in df.columns else len(df)
        years = days / 365.25

        if years > 0:
            cagr = (final_value / initial_capital) ** (1 / years) - 1
        else:
            cagr = 0.0

        return {
            "B&H Total Return": total_return,
            "B&H CAGR": cagr,
            "B&H Max Drawdown": max_drawdown,
            "B&H Final Equity": final_value,
            "B&H Equity Curve": equity_curve
        }
