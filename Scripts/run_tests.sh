#!/usr/bin/env bash
# vault pytest wrapper — hermes venv 명시 호출
# Usage: ./run_tests.sh
set -e
VENV_PY="C:/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
VAULT="D:/HB/P.RAPA_DEV/_obsidian_vault"

"$VENV_PY" -m pytest "$VAULT/Scripts/tests/" -v "$@"
