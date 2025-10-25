#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
PYTHON_BIN="${PYTHON:-python3}"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

FRONTEND_DIR="${ROOT_DIR}/ArcaneOS/ui"

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Error: python executable '${PYTHON_BIN}' not found. Set PYTHON env var if needed." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is required to run the frontend. Please install Node.js/npm and try again." >&2
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "Creating Python virtual environment at ${VENV_DIR}"
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

echo "Upgrading pip and installing backend dependencies..."
"${VENV_DIR}/bin/python" -m pip install --upgrade pip >/dev/null
"${VENV_DIR}/bin/python" -m pip install -r "${ROOT_DIR}/requirements.txt"

echo "Installing frontend dependencies..."
(cd "${FRONTEND_DIR}" && npm install)

BACKEND_CMD=(
  "${VENV_DIR}/bin/uvicorn"
  "app.main:app"
  "--host" "${BACKEND_HOST}"
  "--port" "${BACKEND_PORT}"
  "--reload"
)

BACKEND_PUBLIC_HOST="${BACKEND_PUBLIC_HOST:-localhost}"
BACKEND_URL_FOR_FRONTEND="http://${BACKEND_PUBLIC_HOST}:${BACKEND_PORT}"

FRONTEND_CMD=(npm start)

echo "Starting backend on http://${BACKEND_HOST}:${BACKEND_PORT} ..."
(
  cd "${ROOT_DIR}"
  "${BACKEND_CMD[@]}"
) &
BACKEND_PID=$!

echo "Starting frontend dev server (default http://localhost:3000) ..."
(
  cd "${FRONTEND_DIR}"
  REACT_APP_BACKEND_URL="${BACKEND_URL_FOR_FRONTEND}" "${FRONTEND_CMD[@]}"
) &
FRONTEND_PID=$!

cleanup() {
  echo
  echo "Shutting down servers..."
  kill "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
  wait "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
}

trap cleanup INT TERM EXIT

wait -n "${BACKEND_PID}" "${FRONTEND_PID}"
wait "${BACKEND_PID}" "${FRONTEND_PID}" 2>/dev/null || true
