#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
lab_python="${LAB_PYTHON:-python}"

echo "[1/2] Analisi statica Bandit: app/, severita e confidenza >= medium"
"$lab_python" -m bandit -r app --severity-level medium --confidence-level medium --ignore-nosec

echo "[2/2] Test funzionali"
"$lab_python" -m unittest discover -s tests -v
echo "GATE PASSATO"
