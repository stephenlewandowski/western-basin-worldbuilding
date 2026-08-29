# Water System v0.1 — Phase 1 Handoff

Built: 2026-08-29

## Datasets used

- USGS WBD: seven Maumee basin HUC-8s and 252 HUC-12 subwatersheds.
- USGS NHDPlus HR: 864 Lower Maumee physical flowlines and Lake Erie waterbody geometry.
- USFWS NWI: 608 freshwater emergent/forested-shrub wetland polygons after the documented 25-acre display threshold.
- US EPA / NOAA / City of Toledo / GLOS / Ohio EPA: nutrient-HAB relationship, treatment dependency, public capacity figures, and facility/monitor coordinates.
- User-supplied Great Black Swamp image: non-georeferenced visual reference only.

## Processing performed

- Cached bounded public-service responses; retained original source attributes and stable identifiers.
- Created WBD `tohuc` routing connectors for full-basin topology; these are marked inferred and are not physical waterways.
- Generalized NWI display geometry at 0.00025 degrees and map-only render copies at documented tolerances.
- Built the GeoPackage, node/edge CSVs, five PNG/SVG map pairs, Python network diagram, and independent R QA render.

## Factual / inferred / fictional separation

- **Real / verified:** WBD polygons, NHDPlus Lower Maumee flowlines, NWI wetland polygons, Lake Erie, GLOS intake observation location, Collins Park co-located monitor location, City treatment figures.
- **Real / inferred structure:** WBD representative-point routing connectors, wetland interception relationship, nutrient-to-HAB response chain.
- **Fictional / scenario:** all 2050 nodes and dashed scenario edges; all have null coordinates.
- **Historical:** the Great Black Swamp reference image; no spatial geometry was created from it.

## Unresolved issues and recommended changes before Phase 2

1. Reconcile the GLOS station with historic crib/light and raw-water pipeline records.
2. Locate an authoritative historical Great Black Swamp polygon before any spatial historical layer is added.
3. Replace upstream WBD connectors with physical NHD/3DHP flow geometry through a reliable bulk download/service path.
4. Add defensible HUC-12 land-cover metrics, point sources, monitoring gages, and lower-order drainage only after source review.
5. Obtain local hydrology/GIS review of direction, labels, thresholds, and facility interpretation.

Major QA gates remain, so detailed Phase 2 modeling has not been started.
