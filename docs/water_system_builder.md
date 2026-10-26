# Water System builder reruns

The Phase 1 water reports, maps, network tables, and historical layers are
preserved artifacts. A rerun writes a separate build, so it cannot replace the
released files or current project GeoPackage. From the repository root, after
installing the dependencies in `requirements-systems.txt`, choose a new or
empty directory for each build:

```powershell
python src/python/systems/build_water_system.py --output-root temp/water-rebuild
```

`--output-root` is required. A directory under the project's ignored `temp/`
or `tmp/`, or outside a Git checkout, is accepted. The output directory must
be new or empty. Resolve and review its location before running. The builder
reads existing source caches in `data/raw` and copies the current
`data/processed/glasspunk_base.gpkg` as its seed. Pass `--source-gpkg PATH` to
use a separate current-development GeoPackage copy instead. Builds from a Git
LFS checkout need the actual GeoPackage, not its pointer file.
`--source-raw PATH` can point to a read-only cache directory from an earlier
build; the new build still writes any missing downloads under its own output.

The original five caches are recognized by their exact content, source URL and
query, and retain their documented 2026-08-29 retrieval date. New downloads
receive a hash-bound provenance sidecar with the query and actual retrieval
date. An unrecognized cache without a sidecar has an unknown date; a sidecar
that disagrees with the cache or query causes the build to fail. The output
manifest and source report record per-source dates separately from rebuild
time. Conceptual records retain their original source-review date, since their
references are not fetched again.

The build's GeoPackage is under `data/processed` inside the output directory.
The builder updates its seven water layers on a staged copy, checks that other
layer metadata and row counts are unchanged, then replaces the output copy only
after success. The original seed is left intact. Other build products and new
raw downloads also belong to the output directory; they are not replacements
for the protected release or an automatic change to project canon. In
particular, the newer `hydrography_physical`,
`hydrography_network_connectors`, and `routing_inferred_unresolved` layers
remain separate from the legacy WBD routing layer.

The optional `--historical-swamp-image PATH` supplies the non-georeferenced
historical illustration; it does not create a historical geometry. The
existing released maps and reports record later review and must not be
overwritten by the historical builder's generated text.
