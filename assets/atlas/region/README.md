# Public regional map derivative

The [Maps page](../../../maps/index.html) draws retained geography and real
landmarks, then links overlapping regional interpretations to existing futures
and encounters. It supplies no exact sites for those composite futures.

- `region_explorer.json`: generalized watershed/lake/physical-channel paths,
  eleven sourced landmarks and an exact copy of retained 2025 daily-flow values
  and flags for display.
- `basin_preview.svg`: lightweight homepage preview of the same drawing.
- [Source manifest](source_manifest.json): inputs, byte hashes, settings, credits
  and boundaries. No scientific source or accepted product is overwritten.
- [Landmark reading configuration](../../../src/atlas/landmarks.json): editorial
  text and source IDs. Municipal points, facility addresses, the observation
  station and the physical crib retain their different meanings.

Reproduce from the repository root with Python's standard library:

```sh
python src/python/atlas/build_region_explorer.py
```

The local equirectangular drawing uses a reference latitude of 41.2° and
generalized render copies. It is a reading map, without surveyed dimensions or
load-scaled channel widths. Physical waterways use stream order ≥5; analytical
connectors, inferred routing, much tile drainage and held swamp geometry are
excluded. Regional identity is interpretive and overlapping, without polygons.
Input hashes use exact GeoPackage bytes and LF-normalized text, so Windows Git
checkout line endings do not change text identity. Generated render hashes use
exact LF-authored output bytes.

The physical intake crib uses the resolved Coast Guard position,
41.699444, −83.259167, rather than the nearby legacy monitoring point. Toledo
uses its Census municipality representative, rather than a treatment-plant anchor.

The observation display preserves the [original CSV](../../../outputs/model_lab/observations/waterville_daily_flow_2025.csv)
and [manifest](../../../outputs/model_lab/observations/waterville_observation_manifest.json).
It converts units for display, without routing observations through Model Lab or
estimating nutrient loads. Approval/estimated flags describe the retained snapshot.

Earlier watershed, geology, energy and freight plates are imported directly by
the site, with their original notes and source records. They are not rewritten.
USGS, Census and other source-specific credits remain in those records;
third-party source terms remain applicable.
