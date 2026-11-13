"""A small standard-library client for a user-supplied inference server."""

import argparse
import ipaddress
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_RESPONSE_BYTES = 16 * 1024 * 1024


def request(base_url, route, *, payload=None, api_key=None, timeout=300):
    url = urllib.parse.urlsplit(base_url)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ValueError("Use an HTTP(S) base URL without embedded credentials")
    if url.query or url.fragment:
        raise ValueError("The base URL must not contain a query or fragment")
    loopback = url.hostname.lower() == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(url.hostname).is_loopback
    except ValueError:
        pass
    if api_key and url.scheme != "https" and not loopback:
        raise ValueError("Authenticated remote connections require HTTPS")
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be positive and finite")
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    data = None if payload is None else json.dumps(payload, allow_nan=False).encode("utf-8")
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url.rstrip("/") + route, data=data, headers=headers)

    class NoRedirects(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None

    try:
        with urllib.request.build_opener(NoRedirects()).open(req, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"Server returned HTTP {error.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("Could not reach the server within the timeout; check the endpoint and server") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise RuntimeError("Response exceeded the 16 MiB limit")
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError):
        raise RuntimeError("Server did not return valid JSON") from None
    if not isinstance(result, dict):
        raise RuntimeError("Expected a JSON object from the server")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:1234/v1")
    parser.add_argument("--model")
    parser.add_argument("--prompt")
    parser.add_argument("--list-models", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=1536)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.list_models and (not args.model or not args.prompt):
        parser.error("Chat requires --model and --prompt")
    if args.max_tokens < 1:
        parser.error("--max-tokens must be positive")
    try:
        options = {"api_key": os.environ.get("COMRAD_API_KEY"), "timeout": args.timeout}
        if args.list_models:
            result = request(args.base_url, "/models", **options)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                for row in result["data"]:
                    print(row["id"])
            return 0
        payload = {"model": args.model, "messages": [{"role": "user", "content": args.prompt}],
                   "temperature": 0, "max_tokens": args.max_tokens, "stream": False}
        result = request(args.base_url, "/chat/completions", payload=payload, **options)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            choice = result["choices"][0]
            content = choice["message"].get("content")
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("The server returned no final text; inspect --json and the generation budget")
            print(content)
            if choice.get("finish_reason") == "length":
                print("Generation reached its token limit; the answer may be incomplete.", file=sys.stderr)
        return 0
    except (ValueError, RuntimeError, KeyError, IndexError, TypeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
