import pandas as pd
import pandas_ta as ta

class IndicatorEngine:
    """Wrapper around pandas-ta for calculating technical indicators."""

    @staticmethod
    def add_indicator(df: pd.DataFrame, indicator: str, **kwargs) -> pd.DataFrame:
        """
        Adds a single indicator to the dataframe.
        Modifies df in place but also returns it.
        """
        if not hasattr(df.ta, indicator):
            raise ValueError(f"Indicator '{indicator}' not found in pandas-ta.")

        # Call the indicator method
        getattr(df.ta, indicator)(append=True, **kwargs)
        return df

    @staticmethod
    def calculate_indicators(df: pd.DataFrame, indicators_config: list) -> pd.DataFrame:
        """
        Calculates a list of indicators based on config.
        Example config:
        [
            {"name": "sma", "length": 50},
            {"name": "rsi", "length": 14}
        ]
        """
        for config in indicators_config:
            name = config.pop("name")
            IndicatorEngine.add_indicator(df, name, **config)
        return df
