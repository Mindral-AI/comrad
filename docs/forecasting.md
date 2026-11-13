# ComRAD Forecast

ComRAD Forecast is Mindral's experimental time-series forecasting project, derived from Mistral AI's Timestral. Development focuses on point forecasts, uncertainty estimates, and checking whether improvements transfer across different kinds of series.

## Public release scope

This repository provides a small, model-independent evaluation utility, a synthetic input example, and project results. It does not currently distribute a forecasting checkpoint or an inference package. The development methodology and internal tooling are not released here.

The evaluated reference version has 209,312,256 parameters. Earlier smaller prototypes and later experimental candidates are separate versions and should not be conflated with its results.

## Reported M4 Weekly comparison

The following maintainer-reported comparison covers the 359 M4 Weekly series with a 13-week forecast horizon. Lower values are better.

| Metric | ComRAD reference version | Timestral-209M |
|---|---:|---:|
| MASE | 1.854629 | 1.876681 |
| sMAPE (%) | 5.802690 | 5.892677 |
| OWA | 0.650587 | 0.659469 |

These values come from local development records; this is not an official leaderboard submission or independent reproduction. The Timestral comparator is the published result matched to the same M4 Weekly observations. This dataset has been used during development, so the comparison is not a fresh, untouched holdout.

The most recent saved coverage audit before this repository was prepared covered 89 of 98 TIME tasks, 66 of 97 GIFT-Eval configurations, and 84 of 100 FEV-Bench tasks. Coverage was incomplete, and some reference values came from published runs. Those partial comparisons do not justify a full-benchmark score or a claim that ComRAD outperforms Timestral everywhere. Some uncertainty metrics and weekly tasks remained worse.

## Evaluate your own forecast

```bash
python3 tools/evaluate_forecast.py examples/forecast.json
```

The input is one univariate series represented as JSON:

- `history`: observations strictly before the forecast origin.
- `actual`: observed values over the forecast horizon.
- `quantile_levels`: increasing probabilities between zero and one, including 0.5.
- `quantiles`: one ordered quantile vector per forecast step.
- `seasonality`: positive integer lag used for the MASE denominator.

The tool reports median MAE, MASE, and mean weighted quantile loss. MASE uses the mean absolute seasonal difference in `history`. The quantile metric averages the normalized pinball losses at the supplied levels. It is a finite-quantile score, not an exact continuous-distribution CRPS integral. Undefined normalizations are returned as `null`.

This utility is intentionally limited to one series and one forecast window. Its aggregation is not a replacement for the official TIME, GIFT-Eval, FEV-Bench, or M4 evaluators. The bundled example is synthetic and is not a model result.

## Contribute

Useful contributions include tests for metric edge cases, adapters for public forecast formats, and carefully documented external evaluations. State the checkpoint, data split, horizon, aggregation, and baseline. Keep any test targets separate from model selection and include regressions.

References: [Timestral](https://github.com/mistralai/timestral), [M4](https://github.com/Mcompetitions/M4-methods), [GIFT-Eval](https://github.com/SalesforceAIResearch/gift-eval), [FEV](https://github.com/autogluon/fev).
