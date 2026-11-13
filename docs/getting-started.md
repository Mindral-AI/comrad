# Getting started

## 1. Obtain the model

Download the released GGUF from [Mindral on Hugging Face](https://huggingface.co/Mindral/ComRAD-200B-GGUF). Read the model card and license before use. The file is approximately 114.33 GB; allow additional memory and disk space for your runtime.

Run the integrity checker after downloading. It reads the file sequentially and compares both its length and SHA-256 with the release manifest. Verification of a file this large can take several minutes, depending on storage speed.

```bash
python3 tools/verify_checkpoint.py /path/to/ComRAD-Boreale-195B-Q4_K.gguf
```

## 2. Start a compatible runtime

The published model card records testing with LM Studio's llama.cpp CUDA runtime 2.66.0. Compatibility with other runtimes must be tested separately. Import the GGUF, use its embedded chat template, and start the runtime's API server.

The chat client works with the `/v1/models` and `/v1/chat/completions` endpoints. An OpenAI-compatible protocol does not mean OpenAI hosts or runs this model.

## 3. Send a request

```bash
python3 tools/chat.py --list-models
python3 tools/chat.py --model YOUR_LOADED_MODEL_ID \
  --prompt "Explain why the sky appears blue." --max-tokens 1536
```

The default endpoint is `http://localhost:1234/v1`. The model ID is required for chat and must match your server's loaded model. The default temperature is zero. The server controls the chat template, context size, and other sampling settings; the client does not silently overwrite them.

For an authenticated remote server, set `COMRAD_API_KEY` in your local environment and use an HTTPS endpoint with `--base-url`. Do not put a key in the URL or commit it to a file. No key is needed by the client for an unauthenticated local server.

`--json` prints the complete response, including the finish reason. A `length` finish reason means the server reached its generation limit. Reasoning may consume part of that budget before a final answer appears.

## Troubleshooting

- Connection refused: check that the server is running and the URL/port match its settings.
- Unknown model: run `--list-models` and copy the exact ID.
- No final answer: inspect `--json`, the generation limit, and the runtime's model support.
- Checksum mismatch: keep the file separate from the verified release and check the download source.

These tools do not provide a hosted endpoint or persistent conversation memory.
