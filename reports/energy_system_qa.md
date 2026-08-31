# Phase 3A QA — energy / grid / compute baseline

## Result

The baseline passes structural, provenance, scientific-claim, regression, and render checks. It contains 18 nodes and 17 qualified edges: 9 generation, 2 grid interfaces, 2 storage, 4 major loads, and 1 planned compute project.

## Scientific and classification review

- Nuclear: Davis-Besse and Fermi 2 are current NRC-licensed operating assets.
- Fossil: Monroe is operating in 2026 but carries an explicit planned-retirement status; Oregon, Troy, and Fremont are operating gas assets.
- Renewable: Bowling Green solar, Bowling Green wind, and Temperance solar are operating EIA assets.
- Storage: Bowling Green (12 MW) and Slocum (14 MW) are present; storage duration and dispatch are unknown.
- Loads: no unreported electrical demand is invented.
- Compute: the 5 MW value comes from the municipal plan title; operation is unverified.
- Grid: only in-service public EIA/HIFLD geometry at 230 kV or higher is displayed; no system-state conclusion is made.

## Regression and visual review

The Python validator compares all pre-existing PNG maps (01–10b) to preflight SHA-256 hashes. The Phase 1 GeoPackage remains Git-LFS-managed and unchanged. Map 11 was reviewed at full render for clipping, label collisions, category legibility, source-basis notes, and absence of scenario content. The right-hand panel exposes node counts and qualification rules without implying a solved network.

The Great Black Swamp candidate geometry remains under the existing human C-HOLD; Phase 3A neither promotes nor modifies it.
