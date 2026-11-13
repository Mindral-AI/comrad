"""Score one univariate probabilistic forecast from JSON, without external dependencies."""

import argparse
import json
import math
from pathlib import Path
import sys


def numbers(value, name):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a nonempty numeric list")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in value):
        raise ValueError(f"{name} must contain finite numbers")
    return value


def evaluate(document):
    history = numbers(document["history"], "history")
    actual = numbers(document["actual"], "actual")
    levels = numbers(document["quantile_levels"], "quantile_levels")
    if not all(0 < q < 1 for q in levels) or any(a >= b for a, b in zip(levels, levels[1:])) or .5 not in levels:
        raise ValueError("Quantile levels must increase strictly, lie inside (0, 1), and include 0.5")
    quantiles = document["quantiles"]
    if not isinstance(quantiles, list) or len(quantiles) != len(actual):
        raise ValueError("Quantiles must have one row per actual observation")
    for row in quantiles:
        numbers(row, "quantile row")
        if len(row) != len(levels) or any(a > b for a, b in zip(row, row[1:])):
            raise ValueError("Each quantile row must be ordered and match the quantile levels")
    lag = document.get("seasonality", 1)
    if type(lag) is not int or not 1 <= lag < len(history):
        raise ValueError("Seasonality must be a positive integer smaller than history length")
    center = levels.index(.5)
    mae = math.fsum(abs(y - row[center]) for y, row in zip(actual, quantiles)) / len(actual)
    scale = math.fsum(abs(history[t] - history[t - lag]) for t in range(lag, len(history))) / (len(history) - lag)
    total_absolute = math.fsum(abs(y) for y in actual)
    loss = math.fsum(2 * max(level * (y - predicted), (level - 1) * (y - predicted))
                     for y, row in zip(actual, quantiles) for level, predicted in zip(levels, row))
    return {"horizon": len(actual), "quantile_count": len(levels), "median_MAE": mae,
            "MASE": mae / scale if scale > 0 else None,
            "mean_weighted_quantile_loss": loss / (len(levels) * total_absolute) if total_absolute > 0 else None,
            "mase_scale": scale}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        print(json.dumps(evaluate(document), indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, OverflowError, KeyError, TypeError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
