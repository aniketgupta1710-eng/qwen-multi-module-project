import pandas as pd
import numpy as np
import re

class DataImporter:
    """Handles importing OHLCV data from various file formats and standardizing columns."""

    EXPECTED_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']

    COLUMN_SYNONYMS = {
        'open': ['open', 'opening price', 'o'],
        'high': ['high', 'h', 'high price'],
        'low':  ['low', 'l', 'low price'],
        'close': ['close', 'c', 'closing price', 'adjusted close', 'adj close', 'adj_close'],
        'volume': ['volume', 'v', 'vol'],
        'date': ['date', 'datetime', 'timestamp', 'time', 'd', 't']
    }

    @staticmethod
    def load_file(filepath: str) -> pd.DataFrame:
        """Loads a CSV or Excel file into a DataFrame."""
        if filepath.lower().endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(filepath)
        elif filepath.lower().endswith('.parquet'):
            df = pd.read_parquet(filepath)
        else:
            raise ValueError("Unsupported file format. Supported: .csv, .xlsx, .parquet")

        return DataImporter.standardize_columns(df)

    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Detects and renames columns to standard OHLCV format."""
        # Convert existing columns to lowercase, stripped
        original_cols = df.columns
        cleaned_cols = [str(c).strip().lower() for c in original_cols]
        df.columns = cleaned_cols

        rename_map = {}
        for expected_col, synonyms in DataImporter.COLUMN_SYNONYMS.items():
            # Try exact synonym match first
            found = False
            for col in df.columns:
                if col in synonyms:
                    rename_map[col] = expected_col
                    found = True
                    break

            # If not found, try a looser match (e.g., contains the word)
            if not found:
                for col in df.columns:
                    if expected_col in col and col not in rename_map:
                        rename_map[col] = expected_col
                        break

        df = df.rename(columns=rename_map)

        # Ensure 'date' is datetime
        if 'date' in df.columns:
            try:
                # Need timezone-aware conversion where possible, but for generic
                # import we convert to datetime first.
                df['date'] = pd.to_datetime(df['date'], utc=True)
            except Exception as e:
                pass # Will be caught by validator if invalid

        return df
