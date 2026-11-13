"""Check a local checkpoint against the published release identity."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def verify(path, expected_size, expected_sha256):
    path = Path(path)
    if path.stat().st_size != expected_size:
        return False, "File size differs from the release manifest"
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            result.update(block)
    if result.hexdigest() != expected_sha256:
        return False, "SHA-256 differs from the release manifest"
    return True, "Verified: size and SHA-256 match the released checkpoint"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    manifest = Path(__file__).resolve().parents[1] / "models" / "comrad-200b.json"
    try:
        expected = json.loads(manifest.read_text(encoding="utf-8"))
        ok, message = verify(args.checkpoint, expected["bytes"], expected["sha256"])
        print(message)
        return 0 if ok else 1
    except (OSError, ValueError, KeyError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
