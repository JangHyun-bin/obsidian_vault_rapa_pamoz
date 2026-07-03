"""pytest config for vault scripts tests.

Tests run against the hermes venv site-packages (chromadb, httpx).
Run with:
    <venv>\\python.exe -m pytest _obsidian_vault/Scripts/tests/ -v
"""
import sys
from pathlib import Path

# Add Scripts/ to path so we can import the modules under test
VAULT = Path(__file__).resolve().parent.parent
SCRIPTS = VAULT / "Scripts"
sys.path.insert(0, str(SCRIPTS))
