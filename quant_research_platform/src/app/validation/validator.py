import pandas as pd
from typing import List, Dict, Any

class DataValidator:
    """Validates OHLCV data to detect anomalies and quality issues."""

    @staticmethod
    def validate(df: pd.DataFrame) -> Dict[str, Any]:
        """Runs all validation checks and returns a report."""
        report = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }

        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            report["is_valid"] = False
            report["errors"].append(f"Missing required columns: {missing_cols}")
            return report # Can't proceed safely without required columns

        # Basic stats
        report["stats"]["total_rows"] = len(df)
        report["stats"]["start_date"] = str(df['date'].min())
        report["stats"]["end_date"] = str(df['date'].max())

        # Check for missing values
        null_counts = df[required_cols].isnull().sum()
        if null_counts.sum() > 0:
            report["warnings"].append(f"Found missing values: {null_counts.to_dict()}")

        # Check for duplicate dates
        duplicate_dates = df.duplicated(subset=['date']).sum()
        if duplicate_dates > 0:
            report["is_valid"] = False
            report["errors"].append(f"Found {duplicate_dates} duplicate rows based on date.")

        # Negative prices
        for col in ['open', 'high', 'low', 'close']:
            neg_count = (df[col] < 0).sum()
            if neg_count > 0:
                report["is_valid"] = False
                report["errors"].append(f"Found {neg_count} negative prices in column '{col}'.")

        # Zero prices or volume (often a warning)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            zero_count = (df[col] == 0).sum()
            if zero_count > 0:
                report["warnings"].append(f"Found {zero_count} zero values in column '{col}'.")

        # Logical OHLC relationships
        # High lower than low
        invalid_hl = (df['high'] < df['low']).sum()
        if invalid_hl > 0:
            report["is_valid"] = False
            report["errors"].append(f"Found {invalid_hl} rows where High is lower than Low.")

        # Open outside high-low range
        invalid_open = ((df['open'] > df['high']) | (df['open'] < df['low'])).sum()
        if invalid_open > 0:
            report["is_valid"] = False
            report["errors"].append(f"Found {invalid_open} rows where Open is outside High-Low range.")

        # Close outside high-low range
        invalid_close = ((df['close'] > df['high']) | (df['close'] < df['low'])).sum()
        if invalid_close > 0:
            report["is_valid"] = False
            report["errors"].append(f"Found {invalid_close} rows where Close is outside High-Low range.")

        return report
