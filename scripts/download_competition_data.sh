#!/usr/bin/env bash
# Reconstruct supplied competition mirrors; never log in to or scrape DrivenData.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${ROOT}/.venv/bin/python"
[[ -x "$PY" ]] || PY=python3
exec "$PY" "$ROOT/scripts/download_data.py" "$@"
