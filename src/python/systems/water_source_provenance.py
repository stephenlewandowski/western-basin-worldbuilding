"""Retrieval provenance for the water builder's GeoJSON query caches.

The original Phase 1 source report documents retrieval on 2026-08-29.
Only the exact imported snapshot bytes inherit that date. Later downloads
record their own date and query in a hash-bound sidecar; an unrecorded cache
has an unknown retrieval date rather than a guessed one.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Any


_WBD = "https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer"
_NHD = "https://hydro.nationalmap.gov/arcgis/rest/services/NHDPlus_HR/MapServer"
_NWI = "https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer"
_LEGACY_SNAPSHOTS = {
    "4771b861a46d95f995662af906b33239be0fce4bfd19242655445ee00dcfe011": f"{_WBD}/4/query",
    "433c4c34d89e4708b1571fbf509d497a0fde75d51ef152699dd7dd1399e23292": f"{_WBD}/6/query",
    "f9ba00918e33489e7fe4de4a5fce390558b1d9e30dfc4da35e2a6ed55b4f45c2": f"{_NHD}/3/query",
    "9296a8e172690ddc3e0244fba58f3468afa4a46b4a90a7cf28a1044a431c7297": f"{_NHD}/9/query",
    "8a00f6f6b7c0f3f0f4961abc8f3a852059ac2be2bb053e7d99bce66beb35cb0c": f"{_NWI}/0/query",
}
_HUC8S = tuple(f"0410000{i}" for i in range(3, 10))
_LEGACY_QUERIES = {
    f"{_WBD}/4/query": {
        "where": "huc8 IN (" + ",".join(f"'{h}'" for h in _HUC8S) + ")",
        "out_fields": "huc8,name,areasqkm,states", "geometry": None,
        "page_size": 1000, "max_allowable_offset": None,
    },
    f"{_WBD}/6/query": {
        "where": " OR ".join(f"huc12 LIKE '{h}%'" for h in _HUC8S),
        "out_fields": "huc12,name,areasqkm,states,tohuc,hutype,humod", "geometry": None,
        "page_size": 1000, "max_allowable_offset": None,
    },
    f"{_NHD}/3/query": {
        "where": "reachcode LIKE '04100009%' AND streamorde >= 3",
        "out_fields": "permanent_identifier,gnis_name,lengthkm,reachcode,flowdir,streamorde,"
                      "fromnode,tonode,hydroseq,dnhydroseq,terminalfl,startflag",
        "geometry": None, "page_size": 2000, "max_allowable_offset": None,
    },
    f"{_NHD}/9/query": {
        "where": "gnis_name='Lake Erie'", "out_fields": "permanent_identifier,gnis_name,areasqkm,ftype,fcode",
        "geometry": None, "page_size": 1000, "max_allowable_offset": None,
    },
    f"{_NWI}/0/query": {
        "where": "Wetlands.ACRES >= 25",
        "out_fields": "Wetlands.ATTRIBUTE,Wetlands.WETLAND_TYPE,Wetlands.ACRES,Wetlands.GLOBALID",
        "geometry": "-84.0,40.9,-82.7,42.05", "page_size": 1000,
        "max_allowable_offset": 0.00025,
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sidecar_path(cache: Path) -> Path:
    """A sidecar is local to its cache and never changes the GeoJSON bytes."""
    return cache.with_name(cache.name + ".provenance.json")


def read_cache_provenance(cache: Path, source_url: str, query: dict[str, Any]) -> dict[str, Any]:
    """Return provenance for an existing cache, rejecting inconsistent sidecars.

    Unknown legacy/custom caches remain usable but have a null date and an
    explicit unknown status. A mismatched sidecar is an error, not unknown.
    """
    cache = Path(cache)
    digest = _sha256(cache)
    sidecar = sidecar_path(cache)
    if sidecar.exists():
        try:
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
            if not isinstance(metadata, dict) or set(metadata) != {
                "schema_version", "source_url", "query", "sha256", "retrieved_date"
            }:
                raise ValueError("unexpected fields")
            if metadata["schema_version"] != 1:
                raise ValueError("unknown schema version")
            if metadata["source_url"] != source_url or metadata["query"] != query:
                raise ValueError("source URL or query differs")
            if metadata["sha256"] != digest:
                raise ValueError("cache hash differs")
            retrieved = metadata["retrieved_date"]
            if not isinstance(retrieved, str) or date.fromisoformat(retrieved).isoformat() != retrieved:
                raise ValueError("invalid retrieval date")
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid cache provenance for {cache}: {exc}") from exc
        return {**metadata, "status": "recorded_retrieval"}

    if digest in _LEGACY_SNAPSHOTS:
        if _LEGACY_SNAPSHOTS[digest] != source_url or _LEGACY_QUERIES[source_url] != query:
            raise ValueError(f"Legacy cache {cache} does not match its documented source URL and query")
        return {"source_url": source_url, "query": query, "sha256": digest,
                "retrieved_date": "2026-08-29", "status": "documented_phase1_snapshot"}
    return {"source_url": source_url, "query": query, "sha256": digest,
            "retrieved_date": None, "status": "unknown"}


def record_retrieval(cache: Path, source_url: str, query: dict[str, Any],
                     retrieved_date: str | None = None) -> dict[str, Any]:
    """Record a just-completed download using its actual cache bytes and date."""
    cache = Path(cache)
    retrieved = retrieved_date if retrieved_date is not None else date.today().isoformat()
    if not isinstance(retrieved, str) or date.fromisoformat(retrieved).isoformat() != retrieved:
        raise ValueError("retrieved_date must be an ISO calendar date")
    metadata = {"schema_version": 1, "source_url": source_url, "query": query,
                "sha256": _sha256(cache), "retrieved_date": retrieved}
    sidecar = sidecar_path(cache)
    # A partial write is not accepted as provenance on a subsequent run.
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=sidecar.parent,
                                         prefix=sidecar.name + ".", suffix=".tmp", delete=False) as stream:
            temp_name = stream.name
            json.dump(metadata, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temp_name, sidecar)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)
    return {**metadata, "status": "recorded_retrieval"}
