"""Lossless, bounded receipt publication in release metadata; no long-note truncation."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import zlib

MAX_RECEIPT_BYTES = 4_000_000


def encode(content):
    if not content or len(content) > MAX_RECEIPT_BYTES:
        raise ValueError("Invalid/oversized source receipt")
    envelope = {
        "kind": "gems-s3-lossless-receipt-envelope",
        "codec": "base64-gzip",
        "uncompressed_bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "payload": base64.b64encode(gzip.compress(content, compresslevel=9, mtime=0)).decode(),
        "scope": "Lossless input-only receipt transport, NOT a scientific result or platform score",
    }
    if len(json.dumps(envelope)) > 100_000:
        raise ValueError("Compressed receipt still exceeds conservative GitHub release-note limit")
    return envelope


def decode(envelope):
    if envelope.get("kind") != "gems-s3-lossless-receipt-envelope" or envelope.get("codec") != "base64-gzip":
        raise ValueError("Unsupported receipt envelope")
    if not 0 < envelope.get("uncompressed_bytes", 0) <= MAX_RECEIPT_BYTES:
        raise ValueError("Oversized receipt declaration")
    if len(envelope.get("payload", "")) > 100_000:
        raise ValueError("Over-limit compressed receipt payload")
    compressed = base64.b64decode(envelope["payload"], validate=True)
    stream = zlib.decompressobj(16 + zlib.MAX_WBITS)
    content = stream.decompress(compressed, MAX_RECEIPT_BYTES + 1)
    if (
        not stream.eof
        or stream.unconsumed_tail
        or stream.unused_data
        or len(content) != envelope["uncompressed_bytes"]
    ):
        raise ValueError("Truncated/oversized/trailing compressed receipt data")
    if hashlib.sha256(content).hexdigest() != envelope["sha256"]:
        raise ValueError("Receipt content hash mismatch")
    json.loads(content)
    return content


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--decode", action="store_true")
    args = parser.parse_args()
    if args.decode:
        args.output.write_bytes(decode(json.loads(args.input.read_text())))
    else:
        content = args.input.read_bytes()
        envelope = encode(content)
        if decode(envelope) != content:
            raise ValueError("Lossless receipt round-trip failed")
        args.output.write_text(json.dumps(envelope, indent=2) + "\n")


if __name__ == "__main__":
    main()
