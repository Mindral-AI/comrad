# Evaluation notes

ComRAD 200B is an experimental preview. The evidence below is limited; it does not establish quality parity with GLM-5.3-Flash or a general coding-agent success rate.

## Functional checks

The [published model card](https://huggingface.co/Mindral/ComRAD-200B-GGUF) records one generated C++17 program that compiled and passed 12 functional cases. Those cases exercise one program, not 12 independent programming tasks. Informal conversational checks are reported separately in that card.

## SWE-bench Verified development pilot — 13 November 2026

The pilot used the frozen ComRAD checkpoint identified in this repository, mini-SWE-agent 2.4.6, and SWE-bench harness 4.1.0. It used official task images and test specifications under PRoot. It was **not an official Docker leaderboard submission** and did not run the full 500-task benchmark.

Dataset: `princeton-nlp/SWE-bench_Verified`, test split, revision `c104f840cc67f8b6eec6f759ebc8b2693d585d4a`.

| Cohort | Budget | Outcome |
|---|---|---|
| Initial pilot | 30 agent steps; up to 720 seconds per case | 1 of 5 cases resolved |
| Expanded-step pilot | 250 agent steps; up to 720 seconds per case | 1 of 1 case resolved |
| Final time-limited case | 250-step cap; approximately 401 seconds available | No submitted patch before the time budget expired |

The expanded-step budget was declared before those later cases ran. The cohorts must not be combined into one standardized score. The samples are too small for broad conclusions.

Resolved cases were `astropy__astropy-14995` and `matplotlib__matplotlib-26113`. The first passed its one required failure-to-pass test and preserved 179 pass-to-pass tests; the second passed its one required failure-to-pass test and preserved 812 pass-to-pass tests.

The initial pilot did not resolve `django__django-11848`, `scikit-learn__scikit-learn-25232`, `pytest-dev__pytest-5262`, or `sympy__sympy-24443`. The final time-limited case was `pylint-dev__pylint-4661`. Several runs exhausted their agent budget without a submitted patch; two pytest responses reached the per-response generation limit.

A separate, earlier Astropy diagnostic succeeded but is excluded from these cohorts. Infrastructure failures were also separated from valid model attempts. No human-authored patch fixes were inserted into the scored submissions.

Per-response generation limit was 8,192 tokens. The server was configured with a 456,192-token context limit; this setting is **not** a long-context accuracy measurement. Sampling was deterministic with temperature zero and seed 42.

Raw execution artifacts are retained by the maintainer and are not bundled here. This is a maintainer-reported pilot, not an independently reproduced result.

## What would strengthen the evidence

Use a fixed agent configuration and budget, a larger predeclared sample, exact checkpoint hashes, and reproducible execution logs. Report unsuccessful and interrupted runs as well as successful ones. Evaluate the model and the agent/runtime configuration together rather than attributing every failure directly to model weights.
