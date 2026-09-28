"""Package HF-04's distinct maintenance composition as an Atlas WebP.

Requires the selected maintenance source PNG documented in the HF-04 notes;
this view is not a crop of the wide hero. The shared Phase 17D WebP exporter
ensures the same color handling and decode check as the accepted HF-01 set.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_hf01_glass_city_hero import ROOT, export_webp


OUTPUT = ROOT / "assets/phase17d/hf04/hf04_industrial_metabolism_2075_maintenance.webp"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Selected maintenance source PNG")
    parser.add_argument("--focal-x", type=float, default=0.5, help="Horizontal crop center, 0–1")
    parser.add_argument("--focal-y", type=float, default=0.5, help="Vertical crop center, 0–1")
    parser.add_argument("--quality", type=int, default=86, help="WebP quality, 0–100")
    args = parser.parse_args()
    export_webp(args.source, OUTPUT, (1600, 1200), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
