import pandas as pd

class StrategyBuilder:
    """Builds and applies simple trading logic (Phase 1)."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def generate_signals(self, buy_rules: list, sell_rules: list) -> pd.DataFrame:
        """
        Generates 'buy_signal' and 'sell_signal' boolean columns based on rules.
        A rule is a dictionary like:
        {"type": "cross_above", "series1": "close", "series2": "SMA_50"}
        or
        {"type": "less_than", "series1": "RSI_14", "value": 30}
        """
        self.df['buy_signal'] = False
        self.df['sell_signal'] = False

        # In a real system, these would be combined with AND/OR logic.
        # For Phase 1, we treat multiple rules in a list as AND.

        if buy_rules:
            buy_mask = self._evaluate_rules(buy_rules)
            self.df.loc[buy_mask, 'buy_signal'] = True

        if sell_rules:
            sell_mask = self._evaluate_rules(sell_rules)
            self.df.loc[sell_mask, 'sell_signal'] = True

        return self.df

    def _evaluate_rules(self, rules: list) -> pd.Series:
        """Evaluates a list of rules (AND) and returns a boolean mask."""
        combined_mask = pd.Series(True, index=self.df.index)

        for rule in rules:
            mask = self._evaluate_rule(rule)
            combined_mask = combined_mask & mask

        return combined_mask

    def _evaluate_rule(self, rule: dict) -> pd.Series:
        rtype = rule.get("type")
        s1 = rule.get("series1")

        if rtype == "cross_above":
            s2 = rule.get("series2")
            return (self.df[s1] > self.df[s2]) & (self.df[s1].shift(1) <= self.df[s2].shift(1))
        elif rtype == "cross_below":
            s2 = rule.get("series2")
            return (self.df[s1] < self.df[s2]) & (self.df[s1].shift(1) >= self.df[s2].shift(1))
        elif rtype == "less_than":
            val = rule.get("value")
            if val is not None:
                return self.df[s1] < val
            s2 = rule.get("series2")
            return self.df[s1] < self.df[s2]
        elif rtype == "greater_than":
            val = rule.get("value")
            if val is not None:
                return self.df[s1] > val
            s2 = rule.get("series2")
            return self.df[s1] > self.df[s2]
        else:
            raise ValueError(f"Unknown rule type: {rtype}")
