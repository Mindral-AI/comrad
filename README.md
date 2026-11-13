# ComRAD

**Open tools for Mindral's language-model and time-series forecasting projects.**

ComRAD 200B, also known as **ComRAD Boreale**, is an experimental Mixture-of-Experts language model derived from Z.ai's GLM-5.3-Flash. It is published by **Federico Alessandro**, the 17-year-old creator of Mindral.

[Model and weights on Hugging Face](https://huggingface.co/Mindral/ComRAD-200B-GGUF) · [Getting started](docs/getting-started.md) · [Evaluation notes](docs/evaluation.md) · [Contributing](CONTRIBUTING.md)

Mindral also develops **ComRAD Forecast**, an experimental forecasting model derived from Timestral. Its public section currently contains evaluation tools and documented results; a forecasting checkpoint is not included in this release. See [forecasting](docs/forecasting.md).

## What is available

| Component | Location |
|---|---|
| Released GGUF checkpoint | [Mindral/ComRAD-200B-GGUF](https://huggingface.co/Mindral/ComRAD-200B-GGUF) |
| Minimal chat client | [`tools/chat.py`](tools/chat.py) |
| Checkpoint integrity checker | [`tools/verify_checkpoint.py`](tools/verify_checkpoint.py) |
| Release identity | [`models/comrad-200b.json`](models/comrad-200b.json) |
| Reproducible client tests | [`tests/test_tools.py`](tests/test_tools.py) |
| Forecast evaluation utility | [`tools/evaluate_forecast.py`](tools/evaluate_forecast.py) |
| Forecasting project and results | [`docs/forecasting.md`](docs/forecasting.md) |

This repository contains the source code for these tools and documentation. The model's development pipeline is not part of this release. The released GGUF runs independently in a compatible inference runtime.

## Quick start

Use Python 3.12 or newer. The tools require only the Python standard library.

Load the GGUF in a compatible runtime and start its OpenAI-compatible API server. With an LM Studio server running locally:

```bash
python3 tools/chat.py --base-url http://localhost:1234/v1 --list-models
python3 tools/chat.py --base-url http://localhost:1234/v1 \
  --model YOUR_LOADED_MODEL_ID --prompt "Ciao! Presentati in italiano."
```

Use the model ID returned by the first command. This client does not start a server, download weights, or send requests to OpenAI. It contacts only the endpoint you specify.

Check a downloaded checkpoint:

```bash
python3 tools/verify_checkpoint.py /path/to/ComRAD-Boreale-195B-Q4_K.gguf
```

## Model at a glance

| Property | Released checkpoint |
|---|---|
| Public name | ComRAD 200B |
| Exact parameter count | 194,927,503,582 |
| Format | GGUF, Q4_K |
| File size | 114,333,049,568 bytes, about 114.33 GB |
| Languages listed in the model card | English and Italian |
| Status | Experimental preview |

Memory needed at runtime exceeds the weight file size. Hardware and context settings are documented in the [model card](https://huggingface.co/Mindral/ComRAD-200B-GGUF). A configured context limit is not a demonstration of quality at that length.

## Evaluation and limitations

The model has passed some functional checks, including compilation and execution of a generated C++ program. Coding-agent trials also exposed failures. These results do **not** establish broad reliability or parity with the source model.

See the [evaluation notes](docs/evaluation.md) for the scope and limitations of the available evidence. Contributions that reproduce failures, test runtime compatibility, or improve the tools are welcome.

## Development

```bash
python3 -m unittest discover -s tests -v
```

Tests run locally with a temporary HTTP server. They require neither model weights nor GPU access nor API credentials.

The forecasting utility can be tried immediately with synthetic example data:

```bash
python3 tools/evaluate_forecast.py examples/forecast.json
```

## License

The code and documentation in this repository are licensed under [Apache 2.0](LICENSE).

Model weights are distributed separately. Consult their [license](https://huggingface.co/Mindral/ComRAD-200B-GGUF/blob/main/LICENSE), [upstream notice](https://huggingface.co/Mindral/ComRAD-200B-GGUF/blob/main/LICENSE.upstream), and [model card](https://huggingface.co/Mindral/ComRAD-200B-GGUF) for the terms and attribution applying to that artifact.
