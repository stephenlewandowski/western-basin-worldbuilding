# Phase 14A Evidence Vocabulary Crosswalk

Normalized classes: **8**; explicit local mappings: **17**.

| Class | Meaning | Information preserved | Information lost or caveat |
|---|---|---|---|
| `OBSERVED_DOCUMENTED` | Direct observation, documented record, authoritative program record, or explicitly documented relationship at the source scale. | source observation, documented fact, native scale, temporal basis | A single class does not distinguish a measurement from a legal/program record; local evidence field and source role must remain visible. |
| `DERIVED_CALCULATED` | Value calculated or transformed from documented observations or administrative inputs. | derivation status, input provenance, method requirement | The normalized class does not encode formula, denominator, completeness, or uncertainty; those remain in the local artifact. |
| `INFERRED` | Project interpretation or system relationship not directly documented as the full local claim. | interpretive status, source/basis pointer, uncertainty requirement | The class does not distinguish physical plausibility, accepted-layer reuse, or analytical reasoning; basis and notes remain required. |
| `CONTEXT_REUSED` | Accepted or documented context reused from another system or phase without importing its claim as a new observation. | source phase, source artifact, reuse boundary | Reuse can look like independent evidence if source identity is hidden; duplicate-evidence inflation is prohibited. |
| `SCENARIO_ASSUMPTION` | Explicit premise used to construct a qualitative future state. | horizon, scenario family, assumption identity, fictional/qualitative status | Normalization cannot express plausibility or scenario mechanics; assumption and horizon fields remain mandatory. |
| `SCENARIO_STATE` | Qualitative future state or consequence produced within a named scenario, not an observation or forecast. | scenario family, horizon, consequence/state distinction, basis | The class can conceal whether the row is a delta, state, or comparison unless local field names remain available. |
| `UNRESOLVED` | Evidence or identity question remains open; absence of resolution is not absence of the entity or effect. | open question, uncertainty, source gap, required follow-up | Normalization does not indicate whether the issue is geographic, provenance, status, or substantive evidence uncertainty. |
| `NONCANONICAL_HOLD` | Candidate or interpretation is explicitly retained outside current canon pending a human or source decision. | hold decision, candidate status, noncanonical boundary | A compact class can hide the reason for the hold; the exact hold text and artifact pointer remain mandatory. |

The vocabulary does not treat fact, inference, scenario, observation, derived value, dependency, or risk as interchangeable. Local field, source artifact, temporal basis, scale, and caveat remain required lineage fields.
