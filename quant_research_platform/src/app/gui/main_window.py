import sys
import os
import json
import traceback
import pyqtgraph as pg

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QFileDialog, QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem
)

# Insert src path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.data.importer import DataImporter
from app.validation.validator import DataValidator
from app.indicators.engine import IndicatorEngine
from app.strategies.builder import StrategyBuilder
from app.backtesting.engine import BacktestEngine
from app.metrics.engine import MetricsEngine
from app.benchmark.engine import BenchmarkEngine
from app.reports.excel import ExcelReportEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quantitative Research Platform")
        self.resize(1200, 800)

        self.df = None
        self.results = None
        self.metrics = None

        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Top toolbar
        toolbar_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Project")
        self.save_btn.clicked.connect(self.save_project)
        self.load_proj_btn = QPushButton("Load Project")
        self.load_proj_btn.clicked.connect(self.load_project)
        toolbar_layout.addWidget(self.save_btn)
        toolbar_layout.addWidget(self.load_proj_btn)
        toolbar_layout.addStretch()
        self.layout.addLayout(toolbar_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Setup specific tabs
        self.setup_data_tab()
        self.setup_backtest_tab()
        self.setup_charts_tab()
        self.setup_reports_tab()

    def setup_data_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.load_btn = QPushButton("Load Data File (CSV/XLSX/Parquet)")
        self.load_btn.clicked.connect(self.load_data)
        layout.addWidget(self.load_btn)

        self.data_log = QTextEdit()
        self.data_log.setReadOnly(True)
        layout.addWidget(QLabel("Logs & Validation:"))
        layout.addWidget(self.data_log)

        self.tabs.addTab(tab, "1. Data")

    def setup_backtest_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        desc = QLabel("Phase 1: Runs a basic SMA Crossover Strategy (SMA 50 vs Close).")
        layout.addWidget(desc)

        self.run_btn = QPushButton("Run Backtest & Benchmark")
        self.run_btn.clicked.connect(self.run_backtest)
        layout.addWidget(self.run_btn)

        self.bt_log = QTextEdit()
        self.bt_log.setReadOnly(True)
        layout.addWidget(QLabel("Backtest Results:"))
        layout.addWidget(self.bt_log)

        self.tabs.addTab(tab, "2. Backtest")

    def setup_charts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.plot_widget = pg.PlotWidget(title="Equity Curve")
        self.plot_widget.setLabel('left', 'Equity')
        self.plot_widget.setLabel('bottom', 'Time')
        self.plot_widget.addLegend()

        layout.addWidget(self.plot_widget)
        self.tabs.addTab(tab, "3. Charts")

    def setup_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.export_btn = QPushButton("Export Excel Report")
        self.export_btn.clicked.connect(self.export_report)
        layout.addWidget(self.export_btn)

        self.tabs.addTab(tab, "4. Reports")

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Data File", "", "Data Files (*.csv *.xlsx *.parquet)")
        if not file_name:
            return

        self.data_log.append(f"Loading file: {file_name}...")
        QApplication.processEvents() # Keep UI responsive

        try:
            self.df = DataImporter.load_file(file_name)
            self.data_log.append(f"Loaded {len(self.df)} rows.")

            # Validation
            self.data_log.append("Running validation...")
            report = DataValidator.validate(self.df)

            if not report['is_valid']:
                self.data_log.append("VALIDATION FAILED:")
                for err in report['errors']:
                    self.data_log.append(f"- {err}")
                self.df = None # Clear data so we don't backtest invalid data
            else:
                self.data_log.append("Validation passed.")
                for warn in report['warnings']:
                    self.data_log.append(f"Warning: {warn}")

        except Exception as e:
            self.data_log.append(f"Error loading data: {e}")
            self.data_log.append(traceback.format_exc())

    def run_backtest(self):
        if self.df is None:
            QMessageBox.warning(self, "Error", "Please load valid data first.")
            return

        self.bt_log.clear()
        self.bt_log.append("Calculating indicators (SMA_50)...")
        QApplication.processEvents()

        # In a real app we'd copy df, here we'll just modify it
        try:
            df_bt = self.df.copy()
            IndicatorEngine.calculate_indicators(df_bt, [{"name": "sma", "length": 50}])

            self.bt_log.append("Building strategy signals...")
            builder = StrategyBuilder(df_bt)
            buy_rules = [{"type": "cross_above", "series1": "close", "series2": "SMA_50"}]
            sell_rules = [{"type": "cross_below", "series1": "close", "series2": "SMA_50"}]
            df_bt = builder.generate_signals(buy_rules, sell_rules)

            self.bt_log.append("Executing backtest...")
            engine = BacktestEngine(initial_capital=100000.0, brokerage_pct=0.001)
            self.results = engine.run(df_bt)

            self.bt_log.append("Calculating metrics...")
            self.metrics = MetricsEngine.calculate_metrics(self.results['data'], 100000.0)

            self.bt_log.append("Calculating benchmark (Buy & Hold)...")
            bm_metrics = BenchmarkEngine.calculate_buy_and_hold(df_bt, 100000.0)

            # Combine metrics
            for k, v in bm_metrics.items():
                if k != "B&H Equity Curve":
                    self.metrics[k] = v

            # Display metrics
            self.bt_log.append("\n--- RESULTS ---")
            for k, v in self.metrics.items():
                if k != "Drawdown Curve":
                    self.bt_log.append(f"{k}: {v}")

            self.plot_charts(bm_metrics.get("B&H Equity Curve"))

        except Exception as e:
            self.bt_log.append(f"Error running backtest: {e}")
            self.bt_log.append(traceback.format_exc())

    def plot_charts(self, bh_curve=None):
        self.plot_widget.clear()

        if self.results and 'data' in self.results:
            df = self.results['data']
            if 'equity' in df.columns:
                # We plot against index for simplicity if dates are tricky with pyqtgraph
                x = list(range(len(df)))

                self.plot_widget.plot(x, df['equity'].values, pen='g', name="Strategy Equity")

                if bh_curve is not None:
                    self.plot_widget.plot(x, bh_curve.values, pen='b', name="B&H Equity")

    def export_report(self):
        if not self.results or not self.metrics:
            QMessageBox.warning(self, "Error", "No backtest results to export. Run a backtest first.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Excel Report", "report.xlsx", "Excel Files (*.xlsx)")
        if file_name:
            try:
                # Remove non-serializable objects from metrics for excel export
                export_metrics = {k: v for k, v in self.metrics.items() if k != "Drawdown Curve"}
                ExcelReportEngine.generate(file_name, self.results, export_metrics)
                QMessageBox.information(self, "Success", f"Report saved to {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export report: {e}")

    def save_project(self):
        # Basic save project feature using JSON
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Project", "project.json", "JSON Files (*.json)")
        if file_name:
            try:
                data = {
                    "version": "1.0",
                    "notes": "Basic Phase 1 Project Save"
                }
                with open(file_name, 'w') as f:
                    json.dump(data, f)
                QMessageBox.information(self, "Success", "Project saved.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {e}")

    def load_project(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "JSON Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    data = json.load(f)
                QMessageBox.information(self, "Success", f"Project loaded (Version: {data.get('version')})")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
