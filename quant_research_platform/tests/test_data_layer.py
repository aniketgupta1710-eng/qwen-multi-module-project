import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from app.data.importer import DataImporter
from app.validation.validator import DataValidator

def test_column_standardization():
    df = pd.DataFrame({
        'Date': ['2023-01-01'],
        'OPENING PRICE': [100],
        'H': [105],
        'L': [95],
        'Adjusted Close': [102],
        'Vol': [1000]
    })

    std_df = DataImporter.standardize_columns(df)

    expected_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
    for col in expected_cols:
        assert col in std_df.columns

def test_data_validation_clean():
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'open': [100, 102],
        'high': [105, 106],
        'low': [95, 100],
        'close': [102, 105],
        'volume': [1000, 1200]
    })

    report = DataValidator.validate(df)
    assert report['is_valid'] is True
    assert len(report['errors']) == 0

def test_data_validation_errors():
    df = pd.DataFrame({
        'date': pd.to_datetime(['2023-01-01', '2023-01-01']), # Duplicate
        'open': [100, 102],
        'high': [90, 106], # High lower than low (low=95)
        'low': [95, 100],
        'close': [102, -5], # Negative close
        'volume': [1000, 1200]
    })

    report = DataValidator.validate(df)
    assert report['is_valid'] is False
    assert len(report['errors']) >= 3 # Duplicate date, high<low, negative price
