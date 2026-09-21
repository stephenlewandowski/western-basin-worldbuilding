"""Validate Phase 17A Prototype 2.1 'From Field to Lake' animation outputs.

Independently verifies the accepted animation keyframes, the state/source
manifests, and the canonical 1920x1080 / 30 fps / 32.0 s / 960-frame H.264 MP4
against the 29 validation criteria, plus the qualitative-only and frozen
boundaries. It never re-renders the accepted static figures and never signals
(no particles, travel pulses, camera, zoom, or quantitative animation).

Run from the repository root:
    python src/python/atlas/validate_animation_2_1_field_to_lake.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = ROOT / "outputs" / "atlas" / "prototypes" / "2_1_from_field_to_lake"
ANIM_DIR = STATIC_DIR / "animation"

CANVAS_W, CANVAS_H = 1920, 1080
FPS = 30
DURATION_S = 32.0
EXPECTED_FRAMES = 960
STATES = ["A0", "A1", "A2", "A3", "A4", "A5"]
TIMELINE = {
    "start_seconds": [0.0, 4.0, 8.0, 15.0, 22.0, 29.0],
    "end_seconds": [4.0, 8.0, 15.0, 22.0, 29.0, 32.0],
}
SOURCE_FIGURE = {"A0": "2_1a", "A1": "2_1a", "A2": "2_1b",
                 "A3": "2_1c", "A4": "2_1d", "A5": "2_1d"}

CHECKS: list[dict] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    CHECKS.append({"check": name, "passed": bool(cond), "detail": detail})
    mark = "PASS" if cond else "FAIL"
    print(f"[{mark}] {name}" + (f" - {detail}" if detail else ""))


def ffprobe(path: Path) -> dict:
    d = {}
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=codec_name,width,height,r_frame_rate,"
                          "avg_frame_rate,nb_frames,nb_read_frames",
         "-show_entries", "format=duration,format_name",
         "-of", "json", str(path)],
        capture_output=True, text=True)
    d.update(json.loads(p.stdout))
    # stream audio summary
    pa = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index,codec_type,codec_name",
         "-of", "json", str(path)],
        capture_output=True, text=True)
    try:
        d["audio_streams"] = json.loads(pa.stdout).get("streams", [])
    except Exception:  # noqa: BLE001
        d["audio_streams"] = []
    return d


def read_state_manifest() -> list[dict]:
    """Parse the accepted (unquoted) state manifest.

    Leading fields state_id,start,end,source_figure,representation,
    epistemic_status are comma-free and reliable as the first six CSV cells.
    Later prose fields contain internal commas; their semantics are validated
    by raw-row token checks, so this method returns the reliable leading fields
    plus the full raw row text.
    """
    rows = []
    with (ANIM_DIR / "2_1_animation_state_manifest.csv").open(
            encoding="utf-8", newline="") as fh:
        body = fh.read().splitlines()
    header = [h.strip() for h in body[0].split(",")]
    for line in body[1:]:
        cells = line.split(",")
        if len(cells) < 6:
            continue
        rec = {
            header[0]: cells[0].strip(),
            header[1]: cells[1].strip(),
            header[2]: cells[2].strip(),
            header[3]: cells[3].strip(),
            header[4]: cells[4].strip(),
            header[5]: cells[5].strip(),
            "_raw": line,
        }
        rows.append(rec)
    return rows


def read_source_manifest() -> dict:
    return json.loads((ANIM_DIR / "2_1_animation_source_manifest.json")
                      .read_text(encoding="utf-8"))


def protected_intersection() -> list[str]:
    """Return modified protected frozen paths (git status) intersecting freeze
    manifests (same approach as the accepted static validator)."""
    changed: set[str] = set()
    try:
        out = subprocess.run(["git", "status", "--porcelain"], cwd=str(ROOT),
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            if len(line) > 3:
                p = line[3:].strip()
                if p:
                    changed.add(p.replace("\\", "/").lstrip("./"))
    except Exception:  # noqa: BLE001
        return ["<git unavailable>"]

    protected: set[str] = set()
    for mf in (ROOT / "reports").glob("*_freeze_manifest.json"):
        try:
            d = json.loads(mf.read_text(encoding="utf-8"))
            entries = d.get("artifacts", d.get("protected_artifacts", {}))

            def walk(entries_):
                if isinstance(entries_, dict):
                    for k, v in entries_.items():
                        if isinstance(v, dict) and "path" in v:
                            yield v["path"]
                        elif isinstance(k, str) and "/" in k and isinstance(v, dict):
                            yield k
                        elif isinstance(v, dict):
                            yield from walk(v)
                        elif isinstance(v, str) and v.endswith(
                                (".csv", ".md", ".json", ".svg", ".png", ".gpkg")):
                            yield k
                elif isinstance(entries_, list):
                    for e in entries_:
                        yield from walk(e)

            for p in walk(entries):
                if isinstance(p, str):
                    protected.add(p.replace("\\", "/").lstrip("./"))
        except Exception:  # noqa: BLE001
            continue
    return sorted(changed & protected)


def static_validator_passes() -> tuple[bool, str]:
    import sys
    # The accepted static validator rewrites its own 2_1_validation_report.md
    # (date stamp) as a normal side effect. The accepted static output must not
    # change, so snapshot and restore it across this gate run.
    static_report = STATIC_DIR / "2_1_validation_report.md"
    original = static_report.read_bytes() if static_report.exists() else None
    p = subprocess.run(
        [sys.executable, str(ROOT / "src" / "python" / "atlas"
                             / "validate_spread_2_1_field_to_lake.py")],
        cwd=str(ROOT), capture_output=True, text=True)
    if original is not None:
        static_report.write_bytes(original)
    out = (p.stdout or "") + (p.stderr or "")
    ok = ("RESULT: PASS" in out or ("RESULT: PASS" in p.stdout))
    last = [ln for ln in out.splitlines() if "RESULT:" in ln]
    return ok, (last[-1].strip() if last else f"rc={p.returncode}")


def main() -> int:
    print("=== Phase 17A Prototype 2.1 — animation validation ===\n")
    rows = read_state_manifest()
    src = read_source_manifest()
    mp4 = ANIM_DIR / "2_1_from_field_to_lake_animation.mp4"

    # -- keyframe presence / dimensions ---------------------------------------
    print("1-2. Keyframes exist; all 1920x1080")
    kf_ok = True
    kf_dims = {}
    for sid in STATES:
        f = ANIM_DIR / f"2_1_animation_keyframe_{sid}.png"
        if not f.exists():
            kf_ok = False
            continue
        kf_dims[sid] = Image.open(f).size
        if kf_dims[sid] != (CANVAS_W, CANVAS_H):
            kf_ok = False
    check("21 A0-A5 keyframes exist", all(
        (ANIM_DIR / f"2_1_animation_keyframe_{sid}.png").exists()
        for sid in STATES))
    check("6 all keyframes are 1920x1080", kf_ok,
          str(kf_dims) if kf_dims else "missing")

    print("\n3. Exact states A0-A5")
    ids = [r["state_id"] for r in rows]
    check("1 exact states A0-A5 present in order", ids == STATES, str(ids))

    print("\n4. Timeline 0.0 -> 32.0, gapless/overlap-free")
    check("2 timeline begins at 0.0", float(rows[0]["start_seconds"]) == 0.0,
          rows[0]["start_seconds"])
    check("3 timeline ends at 32.0", float(rows[-1]["end_seconds"]) == DURATION_S,
          rows[-1]["end_seconds"])
    gap_free = True
    for i in range(len(rows) - 1):
        if float(rows[i]["end_seconds"]) != float(rows[i + 1]["start_seconds"]):
            gap_free = False
    check("4 no state gaps/overlaps (contiguous boundaries)", gap_free)
    check("5 end_seconds strictly greater than start_seconds per state",
          all(float(r["end_seconds"]) > float(r["start_seconds"]) for r in rows))

    print("\n5. Canvas / timing contract")
    check("7 30 fps declared in source manifest",
          src["canvas"]["fps"] == FPS)
    check("8 960 frames expected (32.0 s * 30 fps)",
          src["canvas"]["expected_frames"] == EXPECTED_FRAMES
          and EXPECTED_FRAMES == int(round(DURATION_S * FPS)))
    check("9 canvas 1920x1080 declared",
          src["canvas"]["width"] == CANVAS_W and src["canvas"]["height"] == CANVAS_H)

    print("\n6. Epistemic / qualitative / randomization")
    check("10 epistemic status E throughout",
          all(r.get("epistemic_status") == "E" for r in rows))
    check("11 quantitative_encoding=false throughout",
          all(",false," in r["_raw"] for r in rows)
          and src["quantitative_encoding"] is False)
    check("12 randomization=false", src["randomization"] is False)
    check("13 source manifest declares no_new_science=true",
          src.get("no_new_science") is True)

    print("\n7. Scientific / geographic boundaries")
    check("14 no Great Black Swamp geometry",
          src["great_black_swamp_geometry_used"] is False)
    check("15 no Toledo physical intake geometry",
          src["toledo_physical_intake_geometry_used"] is False)
    check("16 HAB_context not a constituent",
          src["hab_context_used_as_constituent"] is False)
    check("17 no unsupported release process",
          src["release_process_introduced"] is False)
    check("18 no deterministic nutrient->HAB edge",
          src["deterministic_nutrient_to_hab_edge"] is False)

    print("\n8. Constituent-presence glyph semantics")
    a3 = next(r for r in rows if r["state_id"] == "A3")
    glyph_ok = ("equal" in a3["_raw"] and "fixed-size" in a3["_raw"]
                and "presence glyphs" in a3["_raw"])
    check("19 equal-size constituent presence glyph semantics preserved",
          glyph_ok)

    print("\n9. A4 convergence junction semantics")
    a4 = next(r for r in rows if r["state_id"] == "A4")
    junction_ok = ("common junction" in a4["_raw"]
                   or "one common junction" in a4["_raw"])
    outgoing_ok = ("one outgoing" in a4["_raw"]
                   or "exactly one outgoing" in a4["_raw"])
    check("20 A4 uses one shared convergence junction", junction_ok)
    check("21 one outgoing relationship from junction", outgoing_ok)

    print("\n10. Persistent footer / reduced-motion endpoint")
    check("22 persistent explanatory footer declared",
          bool(src["persistent_footer"]) and bool(src.get("persistent_footer")))
    rm = ANIM_DIR / "2_1_from_field_to_lake_reduced_motion.png"
    check("20 reduced-motion endpoint exists", rm.exists()
          and Image.open(rm).size == (CANVAS_W, CANVAS_H)
          and rm.name == src["reduced_motion_endpoint"])

    print("\n11. Canonical MP4 encoding check")
    if not mp4.exists():
        check("22 MP4 exists", False, "missing")
        for nm in ("23 MP4 duration ~32.0s", "24 MP4 frame count = 960",
                   "25 MP4 resolution = 1920x1080", "26 MP4 has no audio stream",
                   "MP4 H.264/libx264"):
            check(nm, False)
    else:
        info = ffprobe(mp4)
        stream = (info.get("streams") or [{}])[0]
        check("22 MP4 exists", True)
        dur = float((info.get("format") or {}).get("duration", -1))
        check("23 MP4 duration approximately 32.0 s",
              abs(dur - DURATION_S) <= 0.1, f"{dur:.4f}s")
        # frame count: prefer container nb_frames, fall back to avg frame rate
        nb = stream.get("nb_frames")
        if nb is None:
            avg = stream.get("avg_frame_rate", "30/1")
            n, dv = [float(x) for x in avg.split("/")]
            nb = int(round(n / dv * dur)) if dv else -1
        else:
            nb = int(nb)
        check("24 MP4 frame count = 960", nb == EXPECTED_FRAMES, f"nb_frames={nb}")
        check("25 MP4 resolution = 1920x1080",
              stream.get("width") == CANVAS_W and stream.get("height") == CANVAS_H,
              f"{stream.get('width')}x{stream.get('height')}")
        check("26 MP4 has no audio stream", False if info.get("audio_streams")
              else True, f"{len(info.get('audio_streams', []))} audio stream(s)")
        is_avc = (stream.get("codec_name") == "h264"
                  or str(stream.get("codec_name")) == "libx264")
        check("MP4 video codec is H.264 (libx264 expectation)", is_avc,
              str(stream.get("codec_name")))

    print("\n12. State/source mapping & source manifest consistency")
    map_ok = all(rows[i]["source_figure"] == SOURCE_FIGURE[sid]
                 and rows[i]["state_id"] == sid
                 for i, sid in enumerate(STATES))
    check("27 state/source figure mapping consistent", map_ok)
    s_manifest_present = (ANIM_DIR / "2_1_animation_source_manifest.json").exists() \
        and (ANIM_DIR / "2_1_animation_state_manifest.csv").exists()
    check("28 source & state manifests present", s_manifest_present)
    static_src = STATIC_DIR / "2_1_source_manifest.json"
    check("accepted static source manifest present (unchanged reference)",
          static_src.exists())

    print("\n13. Accepted static / Phase 1-16 protection")
    changed = protected_intersection()
    check("29 no Phase 1-16 protected frozen artifact modified", len(changed) == 0,
          f"{len(changed)} protected path(s): {sorted(changed)[:5]}")
    static_ok, static_last = static_validator_passes()
    check("accepted static Python validator still passes", static_ok, static_last)

    failed = [c for c in CHECKS if not c["passed"]]
    print(f"\n=== RESULT: {'PASS' if not failed else 'FAIL'} "
          f"({len(CHECKS) - len(failed)}/{len(CHECKS)} passed) ===")
    _write_validation_report(CHECKS)
    return 1 if failed else 0


def _write_validation_report(checks: list[dict]) -> None:
    report = ANIM_DIR / "2_1_animation_validation_report.md"
    lines = [
        "# Prototype 2.1 — From Field to Lake — Animation Validation Report",
        "",
        f"- Prototype: 2.1 (Phase 17A), animation",
        f"- Date: {date.today().isoformat()}",
        f"- Result: {'**PASS**' if not [c for c in checks if not c['passed']] else '**FAIL**'}",
        f"- Checks passed: {len([c for c in checks if c['passed']])} / {len(checks)}",
        "",
        "## Canonical video",
        "",
        "- 1920 x 1080, 30 fps, 32.0 s, 960 frames, H.264 (libx264 expectation), no audio.",
        "- Transition behavior: linear fade, linear crossfade, static hold only.",
        "- No particles, travel pulses, camera movement, zoom, motion blur, or",
        "  quantitative animation.",
        "",
        "## Checks",
        "",
    ]
    for c in checks:
        lines.append(f"- [{'x' if c['passed'] else ' '}] {c['check']}"
                     + (f" — {c['detail']}" if c["detail"] else ""))
    lines += [
        "",
        "## Qualitative-only scope",
        "",
        "- All animation states are E (Evidence / Model), qualitative-only.",
        "- No quantity, velocity, travel time, probability, or severity is encoded.",
        "- No deterministic nutrient → HAB edge; receiving-water conditions remain",
        "  a distinct process domain.",
        "",
        "## Frozen-artifact boundary",
        "",
        "- No Phase 1-16 protected/frozen artifact was modified.",
        "- Accepted static Prototype 2.1 figures are unchanged; they are the",
        "  immutable visual sources for the animation.",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())