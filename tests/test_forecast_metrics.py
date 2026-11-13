import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evaluate_forecast", ROOT / "tools/evaluate_forecast.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


class ForecastTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples/forecast.json").read_text())

    def test_hand_calculated_scores(self):
        result = metrics.evaluate(self.data)
        self.assertEqual(result["median_MAE"], 0)
        self.assertEqual(result["MASE"], 0)
        self.assertAlmostEqual(result["mean_weighted_quantile_loss"], .8 / 30)
        self.data["actual"] = [5, 7]
        result = metrics.evaluate(self.data)
        self.assertEqual(result["median_MAE"], 1)
        self.assertEqual(result["MASE"], 1)

    def test_zero_denominators_are_explicit(self):
        self.data["history"] = [1, 1, 1]
        self.data["actual"] = [0, 0]
        result = metrics.evaluate(self.data)
        self.assertIsNone(result["MASE"])
        self.assertIsNone(result["mean_weighted_quantile_loss"])

    def test_seasonal_scale(self):
        self.data["history"] = [1, 10, 3, 12]
        self.data["seasonality"] = 2
        self.assertEqual(metrics.evaluate(self.data)["mase_scale"], 2)

    def test_invalid_forecasts_are_rejected(self):
        cases = [("quantile_levels", [.5, .1, .9]), ("quantile_levels", [.1, .1, .9]),
                 ("actual", [1, float("nan")]), ("actual", [True, 2]),
                 ("quantiles", [[5, 4, 3], [5, 6, 7]]), ("quantiles", [[3, 4, 5]]),
                 ("seasonality", 0), ("seasonality", True), ("history", [])]
        for key, value in cases:
            with self.subTest(key=key, value=value):
                data = copy.deepcopy(self.data)
                data[key] = value
                with self.assertRaises(ValueError):
                    metrics.evaluate(data)

    def test_example_command(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/evaluate_forecast.py"),
                                 str(ROOT / "examples/forecast.json")],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["horizon"], 2)


if __name__ == "__main__":
    unittest.main()
