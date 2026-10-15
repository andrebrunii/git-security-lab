#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
lab_python="${LAB_PYTHON:-python}"

bash scripts/validate.sh
"$lab_python" scripts/package_release.py
