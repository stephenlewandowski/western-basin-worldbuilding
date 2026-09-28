"""Package HF-03's separately composed gate-maintenance image as an Atlas WebP."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_hf01_glass_city_hero import ROOT, export_webp


OUTPUT = ROOT / "assets/phase17d/hf03/hf03_maumee_bio_ag_2075_maintenance.webp"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--focal-x", type=float, default=0.5)
    parser.add_argument("--focal-y", type=float, default=0.5)
    parser.add_argument("--quality", type=int, default=86)
    args = parser.parse_args()
    export_webp(args.source, OUTPUT, (1600, 1200), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
