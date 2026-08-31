# Physical Hydrography Reconciliation

# Executive Finding

The Phase 1 follow-up replaces representative-point reasoning with authoritative USGS network evidence for current-development use while preserving the historical v0.1 release. Of 251 inferred WBD connectors, the final connector-by-connector review found the following:

| QA outcome | count |
| --- | --- |
| ALREADY_REDUNDANT | 31 |
| INVALID_BASELINE_INFERENCE | 0 |
| REPLACED_AUTHORITATIVE_CONNECTOR | 115 |
| REPLACED_PHYSICAL | 93 |
| UNRESOLVED | 12 |

Human decision after source, topology, full-geometry, provenance, and visual review: **B — ACCEPT WITH QUALIFICATION**.

# Released Phase 1 Method

Water System v0.1 contains 864 NHDPlus HR order ≥3 physical flowlines in Lower Maumee and 251 straight representative-point edges derived from authoritative WBD `tohuc`. The latter are abstract graph edges, not waterways. The released GeoPackage SHA-256 remains `555D23D076638E69942C9BB5D6B1043D00A152A945788BDB7C988EE72C576882`.

# Problem With Representative-Point Routing

The v0.1 edges correctly preserve an abstract HUC routing relationship, but their straight geometry can be misread as mapped hydrography and omits physical class, lower-order drainage, waterbody passage, and official network-connector semantics.

# Authoritative Hydrography Source

See [Water Hydrography Source Review](water_hydrography_source_review.md). This QA uses USGS `3DHP_all` Flowline layer 50, refreshed August 5, 2026, from the hash-verified retrieval snapshot. The large reproducible extract is not stored in Git.

# 3DHP Versus Legacy NHD Provenance

The extract is mixed: 102,525 migrated NHD features, 232 EDH work-unit features, and 0 records without a work-unit value. The EDH records belong to work unit 300290, whose missing derivatives are a documented USGS July 2026 issue. The extract is not labeled uniformly as new EDH.

# Retrieval Method

The reproducible extractor uses the full HUC polygon extent plus a 500 m buffer, paginated FeatureServer queries, exact post-filtering, raw snapshot hashing, and preserved service/layer metadata. It does not use representative points to retrieve data.

# Flowline Feature Classes

| featuretype | featuretypelabel | physicality | count |
| --- | --- | --- | --- |
| 1 | Channel Line | physical_channel | 45894 |
| 2 | Canal | canal | 6087 |
| 3 | Drainageway | drainageway | 34429 |
| 4 | Surface Connector | authoritative_network_connector | 3060 |
| 5 | Waterbody Connector | authoritative_network_connector | 9738 |
| 6 | Elevation Breaching Connector | authoritative_network_connector | 45 |
| 7 | Hydro Unenforced Connector | authoritative_network_connector | 3504 |

# Physical Versus Network-Connector Semantics

Channel Line, Canal, and Drainageway are candidate physical hydrography classes. Surface, Waterbody, Elevation Breaching, and Hydro Unenforced connectors remain separately classified `authoritative_network_connector`. No connector class is called a stream.

# CRS and Geometry Validation

- Storage CRS: EPSG:4326; metric analysis CRS: EPSG:26917
- Valid/empty/null geometry failures: 0 / 0 / 0
- Duplicate OBJECTID / id3dhp / exact geometry: 0 / 0 / 0
- Bounds in EPSG:4326: [-85.338361, 40.385779, -83.347683, 42.055249]
- Projected/report length relative-error p95: 0.008918
- Lines assigned to a HUC-12 by representative point: 98,695; outside/boundary: 4,062
- Service declares Z and M. GeoJSON/Shapely retained Z on 102,757 geometries; M is not relied on by this QA.

# Topology Method

Inter-feature direction is controlled by native `hydrosequence → dnhydrosequence`. A second intersection audit handles the special case where one directed 3DHP feature spans both HUC polygons; it uses coordinate order only when `flowdirectionlabel` explicitly confirms digitized downstream direction. The buffered extract yields 102,387 topology nodes, 101,730 native edges, 657 weak components, 57 native terminal records, 600 missing downstream references, and 0 self-loops. Downstream `pathlength` reversals: 0. The Maumee named-flowline terminal trace passes: **True** (300/300), and its terminal Waterbody Connector intersects the accepted western Lake Erie polygon: **True**. Saint Joseph, Saint Marys, Auglaize, Tiffin, and Blanchard named-flowline traces are recorded in the machine-readable QA summary.

# Connector-by-Connector Reconciliation

The authoritative evidence and retained gaps are in [wbd_connector_reconciliation.csv](wbd_connector_reconciliation.csv). Status priority is: invalid WBD identity/tohuc evidence; already represented in released physical topology; native or confirmed same-feature 3DHP physical crossing; native or confirmed same-feature crossing involving an official connector; otherwise unresolved. The full-geometry crossing audit corrected the preliminary aggregate because native derivatives alone cannot expose a boundary crossing within one feature.

# Baseline Comparison

| metric | released_v0_1 | qa_candidate | difference | interpretation |
| --- | --- | --- | --- | --- |
| physical flowline count | 864 | 86410.0 | 85546 | Full 3DHP study extent; not count-optimized to v0.1. |
| total physical length km | 927.359 | 30047.277 |  | 3DHP includes lower-order full-basin hydrography. |
| authoritative network connector count | 0 | 16347.0 | 16347 | Kept separate from mapped watercourses. |
| project-inferred connector count | 251 | 12.0 | -239 | Only UNRESOLVED project edges would remain after approval. |
| HUC-12s with observed downstream routing | not evaluated | 251.0 |  | Native cross-HUC transitions only. |
| HUC-12s unresolved | not evaluated | 1.0 |  | Includes terminal HUCs and extract/boundary limitations. |
| directed network weak components | not evaluated | 657.0 |  | Native hydrosequence network within buffered extract. |
| network outlets | not evaluated | 57.0 |  | Native terminal flags/downstream sequence 0; includes regional terminal networks. |
| divergent flowlines | not evaluated | 698.0 |  | Native divergence attribute (main and minor paths). |
| replaced physical | 0 | 93.0 |  | 3DHP physical-class transition. |
| replaced authoritative connector | 0 | 115.0 |  | 3DHP topology uses a connector class. |
| already redundant | 0 | 31.0 |  | Released physical topology already carried the transition. |
| invalid baseline inference | 0 | 0.0 |  | WBD identity/tohuc validation. |

# Remaining Unresolved Routing

`UNRESOLVED` rows remain explicitly project-inferred analytical edges with `source_method=project_inference` and `physical_geometry=false`. Their evidence is preserved in [unresolved_routing_summary.csv](unresolved_routing_summary.csv).

| unresolved_category | count |
| --- | --- |
| ambiguous_huc_outlet | 7 |
| complex_divergence | 4 |
| direction_conflict | 1 |

The review-only HUC routing table contains 1 HUC-12s without an observed authoritative downstream relationship; that figure includes terminal units and is not proof of absent drainage.

# Limitations

National hydrography does not fully encode agricultural tile drainage in Black Swamp Country. Migrated NHD dominates this snapshot. Direct cross-HUC transition matching is conservative and may leave a defensible WBD relationship unresolved when local topology, waterbody geometry, HUC boundary placement, or an unpopulated EDH derivative prevents a direct match.

# Current-Development Representation

The accepted current-development GeoPackage uses three separate layers: `hydrography_physical` (86,410 features), `hydrography_network_connectors` (16,347 features), and `routing_inferred_unresolved` (12 abstract relationships). Integrated geometry is portable 2D EPSG:4326; a locally reconstructed raw 3DHP snapshot retains source Z coordinates. The derived GeoPackage is tracked through a path-specific Git LFS rule, while historical v0.1 commits are not migrated. The current routing table is [huc12_routing_current.csv](../data/processed/networks/huc12_routing_current.csv). Preserve feature provenance and never render all three with homogeneous stream symbology.

# Human Review Decision

**B — ACCEPT WITH QUALIFICATION.**

The USGS 3DHP-based hydrography and network topology are approved as the preferred routing architecture for future Phase 1-derived work. Physical channels and authoritative USGS network connectors must remain separate semantic classes. The remaining unresolved project-derived HUC-12 routing relationships are retained explicitly as abstract analytical edges and are not mapped or described as waterways.

Visual review passed for both QA maps: physical classes use solid blue/teal symbology, official connector classes use gray dashed symbology and explicit non-stream labeling, and project-inferred unresolved edges use red dashed symbology with the required not-a-waterway note. HUC context, western Lake Erie, north arrows, and metric scale bars are present.

Qualifications:

1. Most extracted 3DHP features are migrated NHD rather than new EDH.
2. Official 3DHP network connectors are authoritative topology features but are not necessarily physical channels.
3. Agricultural tile drainage is incompletely represented.
4. Unresolved project-derived analytical routing relationships remain pending local outlet review.
5. Acceptance does not retroactively modify the released `v0.1-water-system` artifact.

Current-development integration uses separate `hydrography_physical`, `hydrography_network_connectors`, and `routing_inferred_unresolved` layers. The legacy v0.1 layers remain preserved for backward compatibility and historical interpretation. The [transition manifest](development_gpkg_transition_manifest.json) records the historical v0.1 GeoPackage SHA-256 (`555D23D076638E69942C9BB5D6B1043D00A152A945788BDB7C988EE72C576882`) and current-development SHA-256 (`88D7D3D26C8FB746D4AE2502088C906893B8C438A3F255AE0783C24F9EACA8C8`). Released Map 01–05 artifacts were not regenerated or modified; a future map release should use new versioned filenames.
