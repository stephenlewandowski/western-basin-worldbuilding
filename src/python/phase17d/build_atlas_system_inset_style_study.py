"""Build three reproducible HF-02 Atlas inset style studies.

The coast architecture and information are shared. Only annotation language
changes. All coordinates are graphic layout, not measured shore geometry.
Pass --render when CairoSVG is available to write 1440 x 900 PNG previews.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "temp/phase17d-hf02-inset-style"

NAMES = {
    "a": "hf02_inset_style_a_editorial_section",
    "b": "hf02_inset_style_b_margin_annotations",
    "c": "hf02_inset_style_c_key_strip",
}

DESCRIPTION = (
    "Qualitative composite Lake Erie working-coast section, from landward service "
    "and staffed access through external utility and an isolated-capable energy bay, "
    "a protected comparison gallery with a removable sacrificial weather screen, "
    "a dry cradle holding a stopped civilian environmental survey craft, an exposed "
    "working quay with biological fouling, and open Lake Erie. Workers service the "
    "screen and craft; a returned sensor case reaches a comparison bench. This is a "
    "scenario and design concept, not surveyed geometry or proof of observation, "
    "calibration, security, energy, treatment, capacity, or continuity. No new canon."
)


def opening(option: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" role="img" aria-labelledby="title desc">
<title id="title">How the lake-edge service terrace works — style {option.upper()} study</title>
<desc id="desc">{DESCRIPTION}</desc>
<defs>
 <pattern id="concrete" width="30" height="26" patternUnits="userSpaceOnUse"><rect width="30" height="26" fill="#d4d1c6"/><path d="M0 15l7-2m11 9l8-2" stroke="#b5b1a7" stroke-width="1" opacity=".55"/></pattern>
 <pattern id="screen" width="15" height="15" patternUnits="userSpaceOnUse"><rect width="15" height="15" fill="#d8e9e6" fill-opacity=".7"/><path d="M3 0V15" stroke="#8eb9bb" stroke-width="2" opacity=".7"/></pattern>
 <pattern id="unavailable" width="13" height="13" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><path d="M0 0V13" stroke="#a58d68" stroke-width="3" opacity=".65"/></pattern>
 <pattern id="water" width="56" height="24" patternUnits="userSpaceOnUse"><rect width="56" height="24" fill="#8baeb9"/><path d="M0 9q14-10 28 0t28 0M0 21q14-10 28 0t28 0" fill="none" stroke="#e7f0ed" stroke-width="2" opacity=".75"/></pattern>
 <style>
  text{{fill:#23383b;font-family:Arial,Helvetica,sans-serif}}
  .kicker{{font-size:15px;letter-spacing:2.5px;font-weight:700;fill:#547276}}
  .title{{font-family:Georgia,serif;font-size:44px;letter-spacing:-1.1px}}
  .subtitle{{font-size:18px;fill:#56676a}}
  .label{{font-size:19px;font-weight:700}}
  .micro{{font-size:16px;fill:#4e6468}}
  .footer{{font-size:15px;fill:#54676a}}
  .leader{{fill:none;stroke:#71898b;stroke-width:1.5}}
  .major{{fill:none;stroke:#3e5357;stroke-width:6;stroke-linejoin:round;stroke-linecap:round}}
  .middle{{fill:none;stroke:#52696d;stroke-width:3;stroke-linejoin:round;stroke-linecap:round}}
  .fine{{fill:none;stroke:#789194;stroke-width:1.5;stroke-linejoin:round}}
  .num{{font-size:30px;font-weight:700;fill:#fff;text-anchor:middle;dominant-baseline:central}}
 </style>
</defs>
<rect width="1440" height="900" fill="#f3f1e9"/>
<text x="70" y="54" class="kicker">WESTERN BASIN ATLAS  /  SYSTEM INSET</text>
<text x="70" y="108" class="title">How the lake-edge service terrace works</text>
<text x="70" y="141" class="subtitle">A composite 2075 working-coast scenario, drawn from service approach to open lake.</text>
<path d="M70 163H1370" stroke="#9baaaa" stroke-width="1"/>
'''


def worker(x: int, y: int, scale: float = 1.0, raised: bool = False) -> str:
    arm = '<path d="M-11-36L-30-55l-5 6 24 24M10-37l14-9 5 7-19 18" fill="#394f52"/>' if raised else '<path d="M-12-36l-17 15 6 7 17-13M11-36l15 17-5 6-17-13" fill="#394f52"/>'
    return f'''<g transform="translate({x} {y}) scale({scale})" aria-hidden="true">
 <circle cx="0" cy="-57" r="9" fill="#a47a5b"/><path d="M-14-45Q0-52 14-45L17-17H-17Z" fill="#394f52"/>
 <path d="M-12-16l-4 22h9l8-20m11-2l4 22H7L0-14" fill="#34494d"/>
 {arm}<path d="M-17-43h34" stroke="#d7a465" stroke-width="4" opacity=".75"/>
 </g>'''


def scene() -> str:
    return '''<g id="coast-section">
<!-- Air and lake exposure remain visibly separate from the protected gallery. -->
<path d="M1218 444H1370V728H1218Z" fill="#e7edeb"/>
<path d="M1248 614H1370V728H1248Z" fill="url(#water)"/>
<path d="M1250 609q28-10 52 0t68-3" stroke="#5c8b99" stroke-width="4" fill="none"/>
<path d="M1265 405l22 13m13-26l22 12m7 26l24 12" stroke="#c6dce1" stroke-width="3" opacity=".7"/>

<!-- Principal retained and added coast section; textured mass, not a stack of cards. -->
<path d="M74 590H850V675H1087V617H1248V728H74Z" fill="url(#concrete)" stroke="#526268" stroke-width="5" stroke-linejoin="round"/>
<path d="M74 590H850V675H1087V617H1248" class="major"/>
<path d="M85 662H780M89 695H780M1114 685H1212" stroke="#b5b1a7" stroke-width="2" opacity=".65"/>
<path d="M90 590l-15-14h164M260 590l18-13h133" class="middle"/>
<path d="M930 682l-20 20m35-19l-20 20m35-19l-20 20m35-19l-20 20" stroke="#aaa79c" stroke-width="1.5"/>

<!-- A long weather roof, with depth and separate working rooms below. -->
<path d="M228 361H845l25 21H228Z" fill="#aeb9b5" stroke="#40565a" stroke-width="4"/>
<path d="M234 388H843" stroke="#6d8284" stroke-width="4"/>
<path d="M244 382V590M408 382V590M611 382V590M845 382V590" class="middle"/>
<path d="M244 398H843" stroke="#8da3a1" stroke-width="2"/>
<path d="M258 399H403V590H258Z" fill="#e5e3d9"/>
<path d="M420 400H606V590H420Z" fill="#aeb8b4"/>
<path d="M618 400H840V590H618Z" fill="#d8e8e4" fill-opacity=".86"/>
<path d="M404 400V590M610 400V590" stroke="#4f666a" stroke-width="4"/>

<!-- Staffed boundary and external utility: no directional or capacity claim. -->
<path d="M94 553h112v-28h39" stroke="#a78c56" stroke-width="4" fill="none"/>
<circle cx="94" cy="553" r="5" fill="#a78c56"/><circle cx="207" cy="553" r="5" fill="#a78c56"/>
<rect x="286" y="435" width="75" height="155" fill="#d0d8d1"/>
<path d="M290 438h71v152" class="middle"/>
<path d="M370 407V594" stroke="#ac8e59" stroke-width="2.5" stroke-dasharray="8 7"/>
<path d="M311 496h28v20h-28Z" fill="#f0ede3" stroke="#79918e" stroke-width="1.5"/>
''' + worker(351, 585, 0.88) + '''

<!-- Opaque utility service; one hatched, unavailable/isolated bay. -->
<path d="M430 428h167M430 442h167" stroke="#dae1db" stroke-width="4"/>
<path d="M441 474h61v116h-61Z" fill="#d0d2c9" stroke="#546a6c" stroke-width="2"/>
<path d="M513 474h74v116h-74Z" fill="url(#unavailable)" stroke="#546a6c" stroke-width="2"/>
<path d="M526 490h48m-48 10h48" stroke="#66817f" stroke-width="2"/>
<path d="M443 416h146" stroke="#7c9694" stroke-width="5"/>

<!-- Sacrificial outer screen and protected comparison bench. -->
<rect x="627" y="409" width="42" height="181" fill="url(#screen)" stroke="#7faaaa" stroke-width="2"/>
<path d="M637 426l17 23m-13 7l14 19m-17 15l16 20" stroke="#a5babb" stroke-width="1" opacity=".7"/>
<path d="M678 545h143m-135-11h128" class="middle"/>
<path d="M716 511h50v23h-50Z" fill="#859da0" stroke="#526d70" stroke-width="2"/>
<circle cx="731" cy="520" r="5" fill="#d4e5e2"/><circle cx="748" cy="520" r="5" fill="#d4e5e2"/>
<path d="M794 530v60m-65-45v45" class="fine"/>
<path d="M813 552h35v24h-35Z" fill="#a7b9b5" stroke="#526d70" stroke-width="2"/>
<circle cx="820" cy="581" r="4" fill="#586e6f"/><circle cx="843" cy="581" r="4" fill="#586e6f"/>
''' + worker(690, 587, 1.0, raised=True) + '''

<!-- Dry U-cut and blunt civilian survey craft on chocks; no hanging object. -->
<path d="M865 600V667H1072V600" stroke="#496369" stroke-width="3" fill="none"/>
<path d="M887 635h166m-153 18h140" class="middle"/>
<path d="M920 585q4-15 21-17h86q18 0 22 17l-8 23H926Z" fill="#e3e8df" stroke="#4c696c" stroke-width="3"/>
<path d="M940 569v-11h75v11M1022 570v-21m-10 0h21" class="fine"/>
<circle cx="949" cy="590" r="9" fill="#9dbbc0" stroke="#5e8186" stroke-width="2"/>
<circle cx="980" cy="590" r="9" fill="#9dbbc0" stroke="#5e8186" stroke-width="2"/>
<rect x="920" y="612" width="29" height="17" fill="#758d8c"/><rect x="1029" y="612" width="29" height="17" fill="#758d8c"/>
<path d="M961 608v7m42-7v7" class="fine"/>
''' + worker(1082, 613, 0.88) + '''

<!-- Exposed quay, old hardware and restrained biological/weathering marks. -->
<path d="M1112 617h119m-109 0v-44m82 44v-44" class="fine"/>
<path d="M1136 616v-26h34v26m-31-25h28" class="middle"/>
<path d="M1193 651q8-7 16 0t17 0m-22 12q8-7 16 0t17 0" stroke="#688b88" stroke-width="2" fill="none"/>
<circle cx="1210" cy="677" r="4" fill="#536e6b"/><circle cx="1223" cy="682" r="3" fill="#536e6b"/>
<circle cx="1237" cy="665" r="3" fill="#536e6b"/><circle cx="1218" cy="696" r="3" fill="#536e6b"/>
<path d="M1170 556l13 17m6-23l11 16m11-27l10 16" stroke="#9db8bd" stroke-width="2" opacity=".55"/>
</g>'''


def marker(number: int, x: int, y: int, radius: int = 25) -> str:
    return f'<g class="callout"><circle cx="{x}" cy="{y}" r="{radius}" fill="#426d76"/><text x="{x}" y="{y+1}" class="num">{number}</text></g>'


def footer() -> str:
    return '''<path d="M70 833H1370" stroke="#a8b2af" stroke-width="1"/>
<text x="70" y="860" class="footer">Scenario / design concept · qualitative relationships only · no measured dimensions or performance.</text>
<text x="1370" y="860" class="footer" text-anchor="end">Composite coast; not a real facility or crib retrofit.</text>
</svg>'''


def option_a() -> str:
    labels = [
        (1, 96, 238, "Service arrival", "Outside utilities; staffed access", "M157 254L305 319L349 455"),
        (2, 426, 238, "Utility rooms", "Opaque service; isolation possible", "M487 255L525 307L525 454"),
        (3, 744, 238, "Inspection gallery", "Screen; case comparison", "M808 255L754 317L665 444"),
        (4, 1088, 248, "Dry recovery", "Stopped civilian survey craft", "M1144 264L1092 378L1030 570"),
        (5, 839, 791, "Working quay", "Wet-edge wear and fouling", "M894 773L1073 734L1215 663"),
        (6, 1167, 791, "Open Lake Erie", "Exposed water and wind", "M1227 773L1290 725L1305 641"),
    ]
    out = opening("A") + scene()
    for number, x, y, title, detail, leader in labels:
        out += f'<path d="{leader}" class="leader"/>' + marker(number, x, y)
        out += f'<text x="{x+36}" y="{y-3}" class="label">{title}</text><text x="{x+36}" y="{y+19}" class="micro">{detail}</text>'
    return out + footer()


def option_b() -> str:
    out = opening("B") + '<g transform="translate(150 28) scale(.80 1)">' + scene() + '</g>'
    left = [
        (1, 88, 280, "Service arrival", "Staffed threshold", "M189 294L250 349L430 512"),
        (2, 88, 468, "Utility volume", "Supply + hold", "M193 482L330 500L554 503"),
        (3, 88, 662, "Inspection", "Screen + bench", "M193 675L420 657L700 563"),
    ]
    right = [
        (4, 1237, 287, "Dry cradle", "Civilian survey craft", "M1222 303L1150 415L950 592"),
        (5, 1237, 482, "Working quay", "Wet-edge fouling", "M1222 497L1170 568L1128 673"),
        (6, 1280, 674, "Open lake", "Wind-exposed water", "M1264 688L1200 665L1162 638"),
    ]
    for number, x, y, title, detail, leader in left + right:
        out += f'<path d="{leader}" class="leader"/>' + marker(number, x, y, 24)
        if x < 700:
            out += f'<text x="{x}" y="{y+48}" class="label">{title}</text><text x="{x}" y="{y+69}" class="micro">{detail}</text>'
        else:
            out += f'<text x="{x-8}" y="{y+48}" class="label">{title}</text><text x="{x-8}" y="{y+69}" class="micro">{detail}</text>'
    return out + footer()


def option_c() -> str:
    out = opening("C") + '<g transform="translate(0 -70)">' + scene() + '</g>'
    for n, x, y in [(1, 330, 399), (2, 505, 380), (3, 750, 386), (4, 975, 460), (5, 1185, 509), (6, 1325, 463)]:
        out += marker(n, x, y, 27)
    out += '''<path d="M70 705H1370M70 770H1370" stroke="#9aa9a8" stroke-width="1"/>
<text x="80" y="745" class="micro"><tspan font-weight="700">01</tspan> Access + supply</text>
<text x="296" y="745" class="micro"><tspan font-weight="700">02</tspan> Utility / isolation</text>
<text x="532" y="745" class="micro"><tspan font-weight="700">03</tspan> Screen + comparison</text>
<text x="818" y="745" class="micro"><tspan font-weight="700">04</tspan> Survey recovery</text>
<text x="1070" y="745" class="micro"><tspan font-weight="700">05</tspan> Quay + fouling</text>
<text x="1252" y="745" class="micro"><tspan font-weight="700">06</tspan> Lake</text>
'''
    return out + footer()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Also create 1440 x 900 PNG previews with CairoSVG")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    render = None
    if args.render:
        import cairosvg
        render = cairosvg.svg2png
    for key, build in (("a", option_a), ("b", option_b), ("c", option_c)):
        content = build()
        ET.fromstring(content)
        svg = OUT / f"{NAMES[key]}.svg"
        svg.write_text(content + "\n", encoding="utf-8")
        print(f"SVG {key.upper()} PASS: {svg} | {svg.stat().st_size:,} bytes")
        if render:
            png = OUT / f"hf02_inset_style_{key}_preview.png"
            render(bytestring=content.encode("utf-8"), write_to=str(png), output_width=1440, output_height=900)
            print(f"PNG {key.upper()} PASS: {png} | {png.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
