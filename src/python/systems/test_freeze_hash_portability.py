"""Focused regression test for LF/CRLF freeze-hash portability."""
from __future__ import annotations

import json
from pathlib import Path

from freeze_hash import assert_portability_self_check

ROOT = Path(__file__).resolve().parents[3]
TARGET = "data/processed/networks/energy_system_nodes.csv"


if __name__ == "__main__":
    manifest = json.loads((ROOT / "reports/phase3a_freeze_manifest.json").read_text(encoding="utf-8"))
    assert_portability_self_check(ROOT, TARGET, manifest["files"][TARGET]["sha256"])
    print("Freeze-hash portability self-test passed: LF/CRLF equivalent; semantic mutation rejected")
