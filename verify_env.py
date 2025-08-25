#!/usr/bin/env python
"""Verify environment setup."""

import sys
from pathlib import Path


def main():
    """Check environment configuration."""
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[:3]}...")

    # Check if pytest is importable
    try:
        import pytest

        print(f"[OK] pytest {pytest.__version__} is installed")
    except ImportError:
        print("[FAIL] pytest is NOT installed")

    # Check if project modules are importable
    try:
        import scrap_e  # noqa: F401

        print("[OK] scrap_e module is importable")
    except ImportError:
        print("[FAIL] scrap_e module is NOT importable")

    # Check virtual environment
    venv_path = Path(sys.executable).parent.parent
    if ".venv" in str(venv_path):
        print(f"[OK] Running in virtual environment: {venv_path}")
    else:
        print("[FAIL] Not running in a virtual environment")


if __name__ == "__main__":
    main()
