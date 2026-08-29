"""Validate repository-relative Markdown links without accessing the network."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[3]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:")


def main() -> None:
    missing: list[str] = []
    checked = 0
    markdown_files = [ROOT / "README.md", ROOT / "PROJECT_STATUS.md"]
    markdown_files.extend((ROOT / "docs").rglob("*.md"))
    markdown_files.extend((ROOT / "reports").rglob("*.md"))

    for document in sorted(set(markdown_files)):
        text = document.read_text(encoding="utf-8")
        for raw_target in LINK.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and ">" in target:
                target = target[1 : target.index(">")]
            else:
                target = target.split(" ", 1)[0]
            if not target or target.startswith("#") or target.lower().startswith(EXTERNAL_PREFIXES):
                continue
            path_text = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not path_text:
                continue
            resolved = (document.parent / path_text).resolve()
            checked += 1
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                missing.append(f"{document.relative_to(ROOT)} -> outside repository: {target}")
                continue
            if not resolved.exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")

    if missing:
        raise AssertionError("Missing repository-relative Markdown links:\n" + "\n".join(missing))
    print(f"Repository-relative Markdown link validation: PASS ({checked} links)")


if __name__ == "__main__":
    main()
