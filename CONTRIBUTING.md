# Contributing

Contributions to the client, integrity checker, documentation, and reproducible evaluations are welcome.

Before proposing a change, run:

```bash
python3 -m unittest discover -s tests -v
```

For a model or runtime issue, include the checkpoint SHA-256, runtime version, hardware, sampling settings, generation limit, prompt, and complete response when you have permission to share them. Distinguish incomplete output from a completed but incorrect answer.

For benchmark results, identify the dataset revision, split, sample selection, agent or harness, budget, and grading procedure. Include failures and interrupted cases. Do not present a small pilot as a full benchmark score.

Keep changes focused and explain how they were tested. Never commit credentials, private conversations, model weights, or confidential files. The public tools are the contribution surface for this repository; model development internals are outside its scope.
