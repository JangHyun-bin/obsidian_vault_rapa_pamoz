#!/usr/bin/env bash
# vault intelligent sync wrapper
# hermes venv Python을 명시적으로 호출 (uv python 충돌 방지)

set -e
VENV_PY="C:/Users/user/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"
SCRIPT="D:/HB/P.RAPA_DEV/_obsidian_vault/Scripts/sync_intelligent.py"
WORKDIR="D:/HB/P.RAPA_DEV"

cd "$WORKDIR" || exit 1
"$VENV_PY" "$SCRIPT" "$@"
