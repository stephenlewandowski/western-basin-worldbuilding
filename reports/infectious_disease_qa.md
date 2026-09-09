# Phase 13A Infectious Disease System Baseline QA

The package contains 38 nodes, 40 relationships, 25 observations, 17 surveillance records, 27 source records, and 18 uncertainty records.[1][2]
Map 41 PNG/SVG is included as the geographic/schematic product.[24]

The Phase 13A Python validator checks exact row schemas and widths, unique IDs, source references, relationship endpoints, system-category vocabulary, surveillance reporting-basis fields, numerator/denominator semantics, residence-versus-exposure fields, vector/water/respiratory/healthcare boundaries, scale limits, explicit uncertainty, active holds, no scoring fields, no individual cases, no future rows, Map 41 text/raster integrity, phase-local manifest hashes, and Phase 1–12 freeze integrity.[1][7][13]

The independent R validator re-reads the generated CSVs through an independent code path, checks the same counts and references, recomputes artifact hashes, checks Map 41 PNG/SVG presence and required text, verifies negative scope and active holds, and checks that Phase 13B/13C products are not implemented.[23][24]

Semantic checks explicitly reject: ecological suitability as disease burden; case counts as transmission rates; residence as exposure location; surveillance intensity as incidence; non-reporting as absence; environmental contamination as illness; positive vector/pathogen detection as human infection; incompatible diseases combined into a composite score; unsupported local downscaling; and unsupported future inference.[3][7][13]

Accepted/frozen Phase 1–12 artifacts are checked through their existing manifests and are not rewritten by this phase.[20][21][22]
Great Black Swamp remains C — HOLD / noncanonical, the Toledo intake-coordinate discrepancy remains UNRESOLVED, and deferred historical metadata maintenance remains unchanged.[21]

No vulnerability score, individual risk field, disease-risk index, outbreak forecast, Phase 13B/13C implementation, release, or tag is included.[13][15][25]

## Source coverage

National case surveillance and reported occurrence are documented by [1][2][3].

Vector, Lyme, and Legionella system context is documented by [4][5][6].

Waterborne, NORS, and enteric surveillance structure is documented by [7][8][9].

FoodNet, FluView, and influenza methods are documented by [10][11][12].

Wastewater, rabies, and healthcare surveillance are documented by [13][14][15].

Antimicrobial-resistance, Indiana reporting, and Ohio vector context are documented by [16][17][18].

Michigan vector context and accepted Phase 7/9 layers are documented by [19][20][21].

Accepted Phase 11/12/4 context is documented by [22][23][24].

Accepted Phase 10 governance context is documented by [25].
Indiana WNV context is documented by [26].
The fixed Phase 12A findings reference is documented by [27].

## Sources

[1] https://www.cdc.gov/nndss/about/index.html
[2] https://wonder.cdc.gov/nndss.html
[3] https://www.cdc.gov/west-nile-virus/data-maps
[4] https://www.cdc.gov/lyme/data-research/facts-stats/index.html
[5] https://www.cdc.gov/legionella/php/surveillance/index.html
[6] https://www.cdc.gov/legionella/about/index.html
[7] https://www.cdc.gov/healthy-water-data/about/index.html
[8] https://www.cdc.gov/nors/about/index.html
[9] https://www.cdc.gov/national-enteric-surveillance/about/index.html
[10] https://www.cdc.gov/foodnet/about/index.html
[11] https://www.cdc.gov/fluview/index.html
[12] https://www.cdc.gov/fluview/overview/index.html
[13] https://www.cdc.gov/wastewater/about-data
[14] https://www.cdc.gov/rabies/about/index.html
[15] https://www.cdc.gov/nhsn/about-nhsn/index.html
[16] https://www.cdc.gov/antimicrobial-resistance/data-research/threats/index.html
[17] https://www.in.gov/health/idepd/communicable-disease-reporting
[18] https://odh.ohio.gov/know-our-programs/zoonotic-disease-program/news/vectorborne-disease-update
[19] https://www.michigan.gov/emergingdiseases/-/media/Project/Websites/emergingdiseases/EZID_Annual_Surveillance_Summary.pdf
[20] reports/phase7a_exposure_environmental_health_freeze_manifest.json
[21] reports/phase9a_climate_natural_hazards_freeze_manifest.json
[22] reports/phase11a_population_settlement_freeze_manifest.json
[23] reports/phase12a_vector_ecology_freeze_manifest.json
[24] reports/phase4b_information_freeze_manifest.json
[25] reports/phase10a_governance_jurisdiction_freeze_manifest.json
[26] https://events.in.gov/event/idoh-news-release-indianas-first-west-nile-virus-case-of-2026-reported-in-allen-county
[27] reports/vector_ecology_findings.md
