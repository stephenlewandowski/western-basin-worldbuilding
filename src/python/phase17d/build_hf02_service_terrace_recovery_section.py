"""Build the accepted Option C HF-02 system inset for local production.

SVG coordinates control the drawing only; they do not describe a measured coast.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

from build_atlas_system_inset_style_study import option_c


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "assets/phase17d/hf02/hf02_service_terrace_recovery_section.svg"


def build() -> None:
    svg = option_c().replace(
        "How the lake-edge service terrace works — style C study",
        "How the lake-edge service terrace works",
    )
    ET.fromstring(svg)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg + "\n", encoding="utf-8")
    print(f"HF-02 Option C SVG PASS: {OUT} | {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
