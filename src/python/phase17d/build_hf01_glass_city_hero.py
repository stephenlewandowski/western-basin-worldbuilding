"""Deterministically package the approved HF-01 illustration as the site hero.

The source illustration and its prompt/provenance are recorded in
reports/phase17d_hf01_final_production_notes.md. This builder makes the final
crop, dimensions, color mode, and WebP encoding reproducible from that source.
Image pixels are delivery dimensions, not physical measurements of a site.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[3]
HERO_OUTPUT = ROOT / "assets/phase17d/hf01/hf01_glass_city_2075_hero_wide.webp"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def export_webp(
    source: Path,
    output: Path,
    size: tuple[int, int],
    centering: tuple[float, float] = (0.5, 0.5),
    quality: int = 88,
) -> None:
    source = source.resolve(strict=True)
    output = output.resolve()
    if source == output:
        raise ValueError("Source and output must be different files")
    if not all(0 <= value <= 1 for value in centering):
        raise ValueError("Crop centering values must be between 0 and 1")

    with Image.open(source) as raw:
        raw.load()
        corrected = ImageOps.exif_transpose(raw)
        if corrected.mode in ("RGBA", "LA") or "transparency" in corrected.info:
            rgba = corrected.convert("RGBA")
            background = Image.new("RGBA", rgba.size, "#f6f2e9")
            background.alpha_composite(rgba)
            rgb = background.convert("RGB")
        else:
            rgb = corrected.convert("RGB")
        final = ImageOps.fit(rgb, size, method=Image.Resampling.LANCZOS, centering=centering)
        output.parent.mkdir(parents=True, exist_ok=True)
        final.save(output, format="WEBP", quality=quality, method=6)

    with Image.open(output) as check:
        check.load()
        if check.format != "WEBP" or check.size != size:
            raise RuntimeError("Final WebP did not decode at the requested dimensions")
    print(f"HF-01 WebP PASS: {output} | {size[0]} x {size[1]} | {output.stat().st_size:,} bytes")
    print(f"source_sha256={digest(source)}")
    print(f"output_sha256={digest(output)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="Approved source illustration")
    parser.add_argument("--focal-x", type=float, default=0.5, help="Horizontal crop center, 0–1")
    parser.add_argument("--focal-y", type=float, default=0.5, help="Vertical crop center, 0–1")
    parser.add_argument("--quality", type=int, default=88, help="WebP quality, 0–100")
    args = parser.parse_args()
    export_webp(args.source, HERO_OUTPUT, (2400, 1350), (args.focal_x, args.focal_y), args.quality)


if __name__ == "__main__":
    main()
