#!/usr/bin/env bash
set -euo pipefail

./.venv/bin/uvicorn app.api.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

cleanup() {
  kill "$API_PID" >/dev/null 2>&1 || true
}
trap cleanup EXIT

./.venv/bin/streamlit run app/ui/streamlit_app.py

