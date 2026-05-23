import pandas as pd
import numpy as np
from typing import Dict, Any

class BacktestEngine:
    """Executes trades based on signals without lookahead bias."""

    def __init__(self, initial_capital: float = 100000.0, brokerage_pct: float = 0.001):
        self.initial_capital = initial_capital
        self.brokerage_pct = brokerage_pct

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Runs the backtest loop.
        Assumes signals are generated on close, and execution happens on next open.
        """
        # Ensure we don't modify the original dataframe
        df = df.copy()

        # Shift signals by 1 to execute on the next candle
        df['execute_buy'] = df['buy_signal'].shift(1).fillna(False)
        df['execute_sell'] = df['sell_signal'].shift(1).fillna(False)

        cash = self.initial_capital
        position = 0

        equity_curve = []
        trade_log = []

        for index, row in df.iterrows():
            price = row['open'] # Execute on next open
            date = row['date'] if 'date' in row else index

            # Sell logic
            if row['execute_sell'] and position > 0:
                revenue = position * price
                cost = revenue * self.brokerage_pct
                cash += (revenue - cost)

                trade_log.append({
                    "type": "SELL",
                    "date": date,
                    "price": price,
                    "quantity": position,
                    "cost": cost,
                    "cash": cash
                })
                position = 0

            # Buy logic
            elif row['execute_buy'] and position == 0:
                # Calculate how many shares we can buy
                # Subtract estimated cost to ensure we don't overdraft
                available_capital = cash * (1 - self.brokerage_pct)
                quantity = int(available_capital // price)

                if quantity > 0:
                    cost = quantity * price
                    brokerage = cost * self.brokerage_pct
                    cash -= (cost + brokerage)
                    position = quantity

                    trade_log.append({
                        "type": "BUY",
                        "date": date,
                        "price": price,
                        "quantity": position,
                        "cost": brokerage,
                        "cash": cash
                    })

            # Calculate daily equity
            current_equity = cash + (position * row['close'])
            equity_curve.append(current_equity)

        df['equity'] = equity_curve

        return {
            "data": df,
            "trade_log": pd.DataFrame(trade_log) if trade_log else pd.DataFrame(columns=["type", "date", "price", "quantity", "cost", "cash"]),
            "final_equity": equity_curve[-1] if equity_curve else self.initial_capital
        }
