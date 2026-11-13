import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


chat, checker = module("chat"), module("verify_checkpoint")


class Handler(BaseHTTPRequestHandler):
    received = []

    def log_message(self, *args):
        pass

    def respond(self, value):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(value).encode())

    def do_GET(self):
        if self.path == "/v1/models":
            self.respond({"data": [{"id": "comrad-test"}]})
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/v1/models")
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.received.append((self.path, data))
        self.respond({"choices": [{"message": {"content": "Ciao, sono ComRAD Boreale."}, "finish_reason": "stop"}]})


class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_list_models_and_chat_cli(self):
        common = [sys.executable, str(ROOT / "tools/chat.py"), "--base-url", self.base + "/v1"]
        result = subprocess.run(common + ["--list-models"], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "comrad-test")
        result = subprocess.run(common + ["--model", "comrad-test", "--prompt", "Ciao"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), "Ciao, sono ComRAD Boreale.")
        path, body = Handler.received[-1]
        self.assertEqual(path, "/v1/chat/completions")
        self.assertEqual(body["messages"], [{"role": "user", "content": "Ciao"}])
        self.assertEqual(body["model"], "comrad-test")

    def test_http_failure_and_no_redirect(self):
        for route, status in (("/missing", "404"), ("/redirect", "302")):
            with self.assertRaisesRegex(RuntimeError, status):
                chat.request(self.base, route, api_key="local-test-only")

    def test_sensitive_url_and_transport_validation(self):
        for base in ("http://example.com/v1", "https://user:password@example.com/v1",
                     "https://example.com/v1?key=example", "file:///tmp/model"):
            with self.assertRaises(ValueError):
                chat.request(base, "/models", api_key="test-only")

    def test_timeout_validation(self):
        for timeout in (0, -1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                chat.request(self.base, "/models", timeout=timeout)


class IntegrityTests(unittest.TestCase):
    def test_correct_changed_and_truncated_file(self):
        data = b"small checkpoint fixture"
        expected = hashlib.sha256(data).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.bin"
            path.write_bytes(data)
            self.assertTrue(checker.verify(path, len(data), expected)[0])
            path.write_bytes(b"X" + data[1:])
            self.assertFalse(checker.verify(path, len(data), expected)[0])
            path.write_bytes(data[:-1])
            self.assertFalse(checker.verify(path, len(data), expected)[0])

    def test_missing_file_cli_fails(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/verify_checkpoint.py"), "/nonexistent/model.gguf"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
