"""Package the selected HF-02 coast wide source as a 2400 x 1350 Atlas WebP.

Pixel dimensions are delivery coordinates, not surveyed coast geometry.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_hf01_glass_city_hero import ROOT, export_webp


OUTPUT = ROOT / "assets/phase17d/hf02/hf02_lake_erie_energy_security_coast_2075_hero_wide.webp"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--focal-x", type=float, default=0.5)
    parser.add_argument("--focal-y", type=float, default=0.5)
    parser.add_argument("--quality", type=int, default=88)
    args = parser.parse_args()
    export_webp(args.source, OUTPUT, (2400, 1350), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
