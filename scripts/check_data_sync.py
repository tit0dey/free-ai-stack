#!/usr/bin/env python3
"""Fail if canonical and packaged provider data differ."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data" / "providers.json"
PACKAGED = ROOT / "free_ai_stack" / "data" / "providers.json"


def main() -> int:
    if not CANONICAL.exists():
        print(f"Missing canonical file: {CANONICAL}")
        return 1
    if not PACKAGED.exists():
        print(f"Missing packaged file: {PACKAGED}")
        return 1
    a = CANONICAL.read_text(encoding="utf-8")
    b = PACKAGED.read_text(encoding="utf-8")
    if a != b:
        print("ERROR: data/providers.json and free_ai_stack/data/providers.json differ.")
        print("Run: python scripts/build_readme.py (it syncs the packaged copy).")
        return 1
    print("OK: provider data files are in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
