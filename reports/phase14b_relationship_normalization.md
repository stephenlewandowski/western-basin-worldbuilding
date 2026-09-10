# Phase 14B Relationship Normalization

Status: additive normalized crosswalk; Phase 14A relationship inventory and all local edge tables remain unchanged.

Local relationship observations normalized: **367** (Phase 14A inventory baseline: 367).

| Normalized class | Rows |
|---|---:|
| `ecological relationship` | 64 |
| `energy flow` | 3 |
| `exposure pathway` | 21 |
| `governance / authority` | 36 |
| `high-level association` | 16 |
| `information / observation` | 31 |
| `material flow` | 16 |
| `operational dependency` | 58 |
| `physical flow` | 9 |
| `population / mobility interface` | 7 |
| `scenario influence` | 47 |
| `surveillance / detection` | 20 |
| `unresolved / unclassified` | 39 |

The crosswalk preserves local term, field, phase, artifact, count, directionality, causal semantics, flow semantics, Atlas join role, mapping status, and information-loss caveat.

Association is not causation; dependency is not risk; observation is not authority; mobility is not transmission; exposure pathway is not illness; and scenario influence is not observed dependency.

## Energy disposition

Phase 3 energy terms are normalized without semantic collapse: generation/grid/storage interface terms remain `energy flow`; electricity/grid-serves/cooling/thermal/storage-support terms remain operational dependencies; fuel is a material input; communications is information/control; and no control or information term is classified as energy flow.
