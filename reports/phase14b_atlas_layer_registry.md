# Phase 14B Atlas Layer Registry

Status: IMPLEMENTED / VALIDATED / AWAITING SOL ACCEPTANCE.

Atlas registry entries: **213**.

| Physical format | Count |
|---|---:|
| CSV | 81 |
| GeoJSON | 2 |
| GeoPackage | 16 |
| JSON | 1 |
| PNG | 55 |
| SVG | 55 |
| YAML | 3 |

The registry keeps CSV, GeoPackage layer, YAML metadata, PNG, and SVG products separate. It does not move local tables into one GeoPackage or imply that nonspatial tables are geographic layers.

All registry records retain source artifact, source phase, native scale, status, identity namespace, provenance pointer, and limitations.
