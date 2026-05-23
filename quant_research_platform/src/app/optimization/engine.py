import itertools
from typing import Dict, List, Any, Callable
import pandas as pd

class OptimizationEngine:
    """Runs grid search optimization on strategy parameters."""

    @staticmethod
    def generate_parameter_grid(params: Dict[str, Dict[str, float]]) -> List[Dict[str, float]]:
        """
        Generates all combinations for given parameters.
        params format: {"sma_length": {"min": 10, "max": 50, "step": 10}}
        """
        keys = []
        values_lists = []

        for key, limits in params.items():
            keys.append(key)
            if 'step' in limits and limits['step'] > 0:
                # generate range
                # Use int for range if they are integers to avoid float issues,
                # but generic enough for floats if needed (numpy arange would be better for floats)
                import numpy as np
                vals = np.arange(limits['min'], limits['max'] + limits['step'], limits['step']).tolist()
                values_lists.append(vals)
            else:
                # fixed value
                values_lists.append([limits.get('value', limits.get('min'))])

        combinations = list(itertools.product(*values_lists))

        grid = []
        for combo in combinations:
            grid.append(dict(zip(keys, combo)))

        return grid

    @staticmethod
    def run_grid_search(
        data: pd.DataFrame,
        params: Dict[str, Dict[str, float]],
        backtest_func: Callable[[pd.DataFrame, Dict[str, float]], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Runs backtest_func for every parameter combination.
        backtest_func should take (data, current_params) and return a dict of metrics.
        """
        grid = OptimizationEngine.generate_parameter_grid(params)
        results = []

        for current_params in grid:
            metrics = backtest_func(data, current_params)
            # Combine params and metrics for result
            result_row = {**current_params, **metrics}
            results.append(result_row)

        return results
