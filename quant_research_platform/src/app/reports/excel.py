import pandas as pd
from typing import Dict, Any

class ExcelReportEngine:
    """Generates professional Excel reports for backtest results."""

    @staticmethod
    def generate(filepath: str, results: Dict[str, Any], metrics: Dict[str, Any]):
        """Exports data, trade log, and metrics to Excel."""
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:

            # 1. Summary Sheet
            summary_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # 2. Trade Log
            if 'trade_log' in results:
                results['trade_log'].to_excel(writer, sheet_name='Trade Log', index=False)

            # 3. Candle-Level Data
            if 'data' in results:
                # To prevent huge files during dev, we might limit this, but requirements
                # said to export candle level data.
                df_export = results['data'].copy()

                # Make dates timezone naive for excel
                if 'date' in df_export.columns:
                    df_export['date'] = df_export['date'].dt.tz_localize(None)

                df_export.to_excel(writer, sheet_name='Candle Data', index=False)
