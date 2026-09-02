"""Portable, newline-scoped hash checks for manifest-protected text files."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_text(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def manifest_matches(root: Path, relative: str, expected: str) -> bool:
    """Match raw bytes, or prove a text artifact differs only by newline style."""
    path = root / relative
    working = path.read_bytes()
    if sha256_bytes(working) == expected:
        return True
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        accepted = subprocess.check_output(
            ["git", "-C", str(root), "show", f"HEAD:{relative}"],
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return False
    if canonical_text(working) != canonical_text(accepted):
        return False
    accepted_hashes = {
        sha256_bytes(accepted),
        sha256_bytes(accepted.replace(b"\n", b"\r\n")),
    }
    return expected in accepted_hashes


def assert_portability_self_check(root: Path, relative: str, expected: str) -> None:
    """Exercise equivalent LF/CRLF content and reject a semantic mutation."""
    accepted = subprocess.check_output(
        ["git", "-C", str(root), "show", f"HEAD:{relative}"],
        stderr=subprocess.DEVNULL,
    )
    path = root / relative
    original = path.read_bytes()
    try:
        lf = canonical_text(accepted)
        path.write_bytes(lf)
        assert manifest_matches(root, relative, expected)
        path.write_bytes(lf.replace(b"\n", b"\r\n"))
        assert manifest_matches(root, relative, expected)
        mutated = lf.replace(b",", b";", 1)
        assert mutated != lf
        path.write_bytes(mutated)
        assert not manifest_matches(root, relative, expected)
    finally:
        path.write_bytes(original)
