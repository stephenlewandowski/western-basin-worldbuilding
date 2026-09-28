"""Package the separately composed HF-04 wide illustration for the Atlas.

The source image and generation brief are recorded in the HF-04 production
notes. The crop and WebP encoding are deterministic given those source pixels.
Display pixels are not physical dimensions or engineering geometry.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from build_hf01_glass_city_hero import ROOT, export_webp


OUTPUT = ROOT / "assets/phase17d/hf04/hf04_industrial_metabolism_2075_hero_wide.webp"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Selected wide source PNG")
    parser.add_argument("--focal-x", type=float, default=0.5, help="Horizontal crop center, 0–1")
    parser.add_argument("--focal-y", type=float, default=0.5, help="Vertical crop center, 0–1")
    parser.add_argument("--quality", type=int, default=88, help="WebP quality, 0–100")
    args = parser.parse_args()
    export_webp(args.source, OUTPUT, (2400, 1350), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
