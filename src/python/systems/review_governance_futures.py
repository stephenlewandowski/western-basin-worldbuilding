"""Independent bounded review of the actual Phase 10C working package.

This is intentionally a separate review path from the Phase 10C validators: it
re-reads the final artifacts and emits the structured review gate record.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
S = ROOT / "data/processed/scenarios"
A = ROOT / "data/processed/analysis"
F = ROOT / "outputs/figures"
M = ROOT / "outputs/maps/systems"
R = ROOT / "reports"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def portable_match(rel: str, expected: str) -> bool:
    path = ROOT / rel
    if digest(path) == expected:
        return True
    if path.suffix.lower() not in {".csv", ".json", ".md", ".txt", ".yml", ".yaml", ".svg"}:
        return False
    accepted = subprocess.check_output(["git", "show", f"HEAD:{rel}"], cwd=ROOT)
    normalize = lambda b: b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    if normalize(path.read_bytes()) != normalize(accepted):
        return False
    return expected in {digest_bytes(accepted), digest_bytes(accepted.replace(b"\n", b"\r\n"))}


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_paths(path: Path) -> dict[str, dict[str, object]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return manifest.get("artifacts", manifest.get("files", {}))


def review() -> dict[str, object]:
    security: list[str] = []
    logic: list[str] = []
    provenance: list[str] = []
    scenario: list[str] = []
    authority: list[str] = []
    suggestions: list[str] = []
    assumptions = read(S / "governance_scenario_assumptions.csv")
    actors = read(S / "governance_actor_states_scenario.csv")
    authorities = read(S / "governance_authority_states_scenario.csv")
    dependencies = read(S / "governance_dependency_states_scenario.csv")
    coordination = read(S / "governance_coordination_states_scenario.csv")
    uncertainty = read(S / "governance_uncertainty_states_scenario.csv")
    comparison = read(F / "governance_scenario_comparison.csv")
    all_rows = assumptions + actors + authorities + dependencies + coordination + uncertainty + comparison
    text = " ".join(" ".join(row.values()) for row in all_rows).lower()
    states = {"A2050", "A2075", "B2050", "B2075", "C2050", "C2075"}
    if {r["scenario_id"] for r in assumptions} != states:
        logic.append("Assumption state set is not exactly A/B/C at 2050/2075.")
    for frame, label in ((assumptions, "assumptions"), (actors, "actors"), (authorities, "authorities"), (dependencies, "dependencies"), (coordination, "coordination"), (uncertainty, "uncertainty")):
        if any(r["reality_status"] != "fictional" or r["canon_status"] != "scenario" for r in frame):
            scenario.append(f"{label} contains a non-fictional or non-scenario row.")
        if any(not r["assumption_id"] for r in frame):
            scenario.append(f"{label} contains a missing assumption reference.")
        if label != "assumptions" and any(not r["current_fact"].startswith("CURRENT FACT (2026 baseline):") or not r["scenario_assumption"].startswith("SCENARIO ASSUMPTION:") or not r["scenario_consequence"].startswith("SCENARIO CONSEQUENCE:") for r in frame):
            scenario.append(f"{label} does not separate current fact, assumption, and consequence.")
    if len(assumptions) != 48 or len(actors) != 120 or len(authorities) != 90 or len(dependencies) != 150 or len(coordination) != 84 or len(uncertainty) != 96 or len(comparison) != 6:
        logic.append("One or more final package counts differ from the reviewed package.")
    if not {r["actor_id"] for r in actors} >= {"GA-021", "GA-022", "GA-023", "GA-030", "GA-035"}:
        authority.append("Required intertribal, nation-specific, private, and public/private actors are not all represented.")
    if any(r["legal_status"] != "CURRENT AUTHORITY RETAINED; SCENARIO COORDINATION CHANGE" for r in authorities):
        authority.append("A future authority state changes legal status rather than coordination only.")
    if any("final human decision authority" not in r["human_decision_boundary"].lower() for r in authorities):
        authority.append("An authority state lacks an explicit final human decision boundary.")
    if "glifwc remains an intertribal" not in text or "distinct sovereign" not in text:
        authority.append("Tribal sovereignty boundary is not explicit in the reviewed material.")
    if "regulation" not in text or "operation" not in text or "ownership" not in text or "public finance" not in text:
        authority.append("Public/private role distinctions are not explicit.")
    if "ai recommendation ≠ legal authority" not in text or "automated monitoring ≠ automatic enforcement" not in text or "sensor coverage ≠ institutional capacity" not in text:
        authority.append("Technology governance boundary is incomplete.")
    if any(word in text for word in ("partisan", "election", "candidate", "voter", "party control", "ideological")):
        # The actual data package must not contain political material, including caveats.
        scenario.append("Political or election language appears in future data products.")
    # Positive overreach is rejected; explicit negative boundary statements are allowed.
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if re.search(r"(?:creates?|creating|establishes?|assigns?|grants?|transfers?)\s+(?:a\s+)?(?:new\s+)?(?:sovereign territory|permit jurisdiction|enforcement authority|single basin government|tribal territory|land transfer|treaty settlement)", sentence):
            if not re.search(r"\b(?:no|not|without|does not|do not|never|cannot)\b", sentence):
                authority.append("Unsupported future jurisdiction or sovereignty claim detected.")
    if "issue-specific" not in " ".join(r["assumption"] for r in assumptions if r["scenario_id"].startswith("B")).lower() or "friction" not in " ".join(r["assumption"] for r in assumptions if r["scenario_id"].startswith("B")).lower():
        scenario.append("Scenario B lacks distinct issue-specific network/friction logic.")
    if any(not r["notes"] for r in comparison):
        logic.append("Comparison row lacks a note describing qualitative non-ranking use.")
    # Verify actual protected manifests and map labels independently of the phase validator.
    for manifest_name in ("phase10a_governance_jurisdiction_freeze_manifest.json", "phase10b_governance_dependencies_coordination_freeze_manifest.json"):
        for rel, meta in manifest_paths(R / manifest_name).items():
            if not portable_match(rel, str(meta["sha256"])):
                provenance.append(f"Protected Phase 10 artifact mismatch: {rel}")
    for manifest_path in sorted(R.glob("phase*_freeze_manifest.json")):
        if manifest_path.name.startswith("phase10"):
            continue
        for rel, meta in manifest_paths(manifest_path).items():
            expected = meta["sha256"] if isinstance(meta, dict) else meta
            if not portable_match(rel, str(expected)):
                provenance.append(f"Prior protected artifact mismatch: {rel}")
    for base, label in (("34_governance_futures_2050", "map 34"), ("34b_governance_futures_2075", "map 34b")):
        svg = M / f"{base}.svg"
        if not svg.exists():
            logic.append(f"Missing {label} SVG.")
            continue
        svg_text = " ".join(ET.parse(svg).getroot().itertext()).lower()
        for term in (label, "integrated basin", "federated / networked", "fragmented / contested", "not jurisdiction boundaries"):
            if term not in svg_text:
                logic.append(f"{label} is missing required label: {term}.")
    if any("single basin government" in r["assumption"].lower() and "without" not in r["assumption"].lower() for r in assumptions):
        authority.append("Scenario text may represent centralization as a legal outcome.")
    passed = not any((security, logic, provenance, scenario, authority))
    if passed:
        suggestions.append("Retain the explicit three-part fact/assumption/consequence fields and rerun this review after any content edit.")
    return {
        "passed": passed,
        "security_concerns": security,
        "logic_errors": logic,
        "provenance_errors": provenance,
        "scenario_boundary_errors": scenario,
        "authority_classification_errors": authority,
        "suggestions": suggestions,
        "summary": "Fresh independent bounded review of the actual Phase 10C worktree passed." if passed else "Fresh independent bounded review found blocking issues in the actual Phase 10C worktree.",
    }


def main() -> None:
    result = review()
    report = "# Phase 10C Independent Review\n\n```json\n" + json.dumps(result, indent=2) + "\n```\n"
    (R / "governance_scenario_independent_review.md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
