"""Package a separately composed HF-01 maintenance illustration as WebP.

This view must come from its own source composition, not a crop of the hero.
The transformation is deterministic given that source; provenance is recorded
in reports/phase17d_hf01_final_production_notes.md.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_hf01_glass_city_hero import ROOT, export_webp


OUTPUT = ROOT / "assets/phase17d/hf01/hf01_glass_city_2075_maintenance.webp"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Maintenance source illustration")
    parser.add_argument("--focal-x", type=float, default=0.5, help="Horizontal crop center, 0–1")
    parser.add_argument("--focal-y", type=float, default=0.5, help="Vertical crop center, 0–1")
    parser.add_argument("--quality", type=int, default=86, help="WebP quality, 0–100")
    args = parser.parse_args()
    export_webp(args.source, OUTPUT, (1600, 1200), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
