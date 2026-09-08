"""Build Phase 11A/11B population, settlement, mobility, and dependency products.

The builder uses public Census/LEHD products at their native geography and
vintage. It deliberately avoids individual records, exact utility assignment,
protected-class ranking, vulnerability scoring, and future demographic rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import zipfile
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Patch
import pandas as pd
import requests
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "cache/phase11_source"
ANALYSIS = ROOT / "data/processed/analysis"
NETWORKS = ROOT / "data/processed/networks"
MAPS = ROOT / "outputs/maps/systems"
REPORTS = ROOT / "reports"
CENSUS_COUNTIES = ROOT / "data/raw/census/tigerweb_counties_oh_in_mi.geojson"
CENSUS_PLACES = ROOT / "data/raw/census/tigerweb_incorporated_places.geojson"
RETRIEVAL_DATE = "2026-09-08"
ACS_RELEASE = "acs2024_5yr"
LODES_YEAR = "2023"
LODES_PRODUCT_YEARS = {
    "OH": {"wac": "2023", "rac": "2023", "od": "2023"},
    "MI": {"wac": "2021", "rac": "2023", "od": "2021"},
    "IN": {"wac": "2023", "rac": "2023", "od": "2023"},
}
PEP_YEAR = "2024"

# An explicit analytical frame, not a new canonical region or jurisdiction.
COUNTIES = {
    "39039": ("OH", "Defiance"), "39051": ("OH", "Fulton"),
    "39063": ("OH", "Hancock"), "39069": ("OH", "Henry"),
    "39095": ("OH", "Lucas"), "39123": ("OH", "Ottawa"),
    "39125": ("OH", "Paulding"), "39137": ("OH", "Putnam"),
    "39143": ("OH", "Sandusky"), "39147": ("OH", "Seneca"),
    "39161": ("OH", "Van Wert"), "39171": ("OH", "Williams"),
    "39173": ("OH", "Wood"), "26091": ("MI", "Lenawee"),
    "26115": ("MI", "Monroe"), "18003": ("IN", "Allen"),
    "18033": ("IN", "DeKalb"), "18151": ("IN", "Steuben"),
}
STATES = {"OH": "oh", "MI": "mi", "IN": "in"}
STATE_FIPS = {"OH": "39", "MI": "26", "IN": "18"}
PL_ZIPS = {
    "OH": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Ohio/oh2020.pl.zip",
    "MI": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Michigan/mi2020.pl.zip",
    "IN": "https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/Indiana/in2020.pl.zip",
}
PEP_COUNTY_URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/counties/totals/co-est2024-alldata.csv"
PEP_PLACE_URL = "https://www2.census.gov/programs-surveys/popest/datasets/2020-2024/cities/totals/sub-est2024.csv"
ACS_ENDPOINT = "https://api.censusreporter.org/1.0/data/show/acs2024_5yr"
TIGER_COUNTY_URL = "https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html?layer=counties"
TIGER_PLACE_URL = "https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html?layer=places"
LODES_BASE = "https://lehd.ces.census.gov/data/lodes/LODES8"

SOURCE_COLUMNS = [
    "source_id", "title", "url", "source_type", "source_product", "reference_year",
    "release_year", "estimate_period", "geographic_scale", "observed_estimated_modeled",
    "retrieval_date", "use_limitations",
]
SOURCE_ROWS = [
    ["s11a_decennial_oh_pl", "2020 Census P.L. 94-171 Ohio summary file", PL_ZIPS["OH"], "federal_decennial", "2020 Decennial Census P.L. 94-171 legacy summary file", "2020", "2021", "2020-04-01 enumeration", "county/place", "observed", RETRIEVAL_DATE, "P1 population and H1 housing-unit geography records; no ACS households or current estimate."],
    ["s11a_decennial_mi_pl", "2020 Census P.L. 94-171 Michigan summary file", PL_ZIPS["MI"], "federal_decennial", "2020 Decennial Census P.L. 94-171 legacy summary file", "2020", "2021", "2020-04-01 enumeration", "county/place", "observed", RETRIEVAL_DATE, "P1 population and H1 housing-unit geography records; no ACS households or current estimate."],
    ["s11a_decennial_in_pl", "2020 Census P.L. 94-171 Indiana summary file", PL_ZIPS["IN"], "federal_decennial", "2020 Decennial Census P.L. 94-171 legacy summary file", "2020", "2021", "2020-04-01 enumeration", "county/place", "observed", RETRIEVAL_DATE, "P1 population and H1 housing-unit geography records; no ACS households or current estimate."],
    ["s11a_pep_county_2024", "Population Estimates Program county totals", PEP_COUNTY_URL, "federal_estimates", "2024 Vintage Population Estimates Program county totals", "2024", "2025", "July 1 annual estimates, 2020-2024", "county", "estimated", RETRIEVAL_DATE, "Annual estimates are not decennial enumeration and are not a complete 2026 Census."],
    ["s11a_pep_place_2024", "Population Estimates Program city and town totals", PEP_PLACE_URL, "federal_estimates", "2024 Vintage Population Estimates Program city/place totals", "2024", "2025", "July 1 annual estimates, 2020-2024", "place", "estimated", RETRIEVAL_DATE, "Annual place estimates are not decennial enumeration and may differ from 2020 Census counts."],
    ["s11a_acs_2024_5yr", "Census Reporter ACS 2024 5-year API mirror", ACS_ENDPOINT, "federal_survey_api_mirror", "ACS 2024 5-year detailed tables", "2024", "2025", "2020-2024 5-year estimate period", "county/place", "estimated", RETRIEVAL_DATE, "Census Reporter is a programmatic mirror of Census ACS tables; values are estimates, not 2026 observations."],
    ["s11a_tiger_counties", "Census TIGER/TIGERweb county geography", TIGER_COUNTY_URL, "federal_geography", "Census TIGER county boundaries used by repository", "2020", "2020", "2020 geography", "county", "observed", RETRIEVAL_DATE, "Boundary geometry is cartographic/statistical geography, not a utility service territory."],
    ["s11a_tiger_places", "Census TIGER/TIGERweb incorporated-place geography", TIGER_PLACE_URL, "federal_geography", "Census TIGER place geography used by repository", "2020", "2020", "2020 geography", "place", "observed", RETRIEVAL_DATE, "Place geography is not an urbanized-area or municipal utility-service assignment."],
    ["s11b_acs_commute_2024", "Census Reporter ACS commuting tables", ACS_ENDPOINT + "?tables=B08301,B08303", "federal_survey_api_mirror", "ACS 2024 5-year B08301/B08303 journey-to-work tables", "2024", "2025", "2020-2024 5-year estimate period", "county", "estimated", RETRIEVAL_DATE, "Residence-based survey commuting context; not migration or individual travel paths."],
]
for state, prefix in STATES.items():
    for product, suffix, scale in [("wac", "wac_S000_JT00", "workplace block/county aggregate"), ("rac", "rac_S000_JT00", "residence block/county aggregate"), ("od", "od_main_JT00", "origin-destination block/county aggregate"), ("xwalk", "xwalk", "block-to-geography crosswalk")]:
        year = LODES_PRODUCT_YEARS[state].get(product, LODES_YEAR)
        url = f"{LODES_BASE}/{prefix}/{product}/{prefix}_{suffix}_{year}.csv.gz" if product != "xwalk" else f"{LODES_BASE}/{prefix}/{prefix}_xwalk.csv.gz"
        source_id = f"s11b_lodes_{state.lower()}_{product}"
        source_year = year if product != "xwalk" else LODES_YEAR
        SOURCE_ROWS.append([source_id, f"LEHD LODES 8.4 {state} {product.upper()}", url, "federal_lehd", f"LODES 8.4 {product.upper()} {source_year}", source_year, "2025", source_year, scale, "modeled", RETRIEVAL_DATE, "LODES is tabulated/modelled administrative data with nonsampling error; aggregated here to generalized county interfaces, not individuals."])
# Accepted-system interfaces are reused as bounded references, not rebuilt.
SOURCE_ROWS.extend([
    ["phase10_s03_toledo_treatment", "Accepted Phase 10 Toledo water-treatment source", "reports/governance_baseline_sources.md?s03_toledo_treatment", "repository_accepted_source", "Phase 10A accepted institutional source registry", "2026", "2026", "current page context", "municipal/service context", "observed", RETRIEVAL_DATE, "Supports Toledo operator context only; does not assign every resident to the utility or resolve the intake-coordinate hold."],
    ["phase10_s05_ohio_npdes", "Accepted Phase 10 Ohio EPA permitting source", "reports/governance_baseline_sources.md?s05_ohio_npdes", "repository_accepted_source", "Phase 10A accepted institutional source registry", "2026", "2026", "current program context", "state/program", "observed", RETRIEVAL_DATE, "Supports wastewater/regulatory interface; permit context is not actual load or exact service territory."],
    ["phase10_s24_pjm", "Accepted Phase 10 PJM source", "reports/governance_baseline_sources.md?s24_pjm", "repository_accepted_source", "Phase 10A accepted institutional source registry", "2026", "2026", "current program context", "interstate/system", "observed", RETRIEVAL_DATE, "Supports wholesale/high-voltage system-operation context, not local distribution assignment."],
    ["phase10_s28_firstenergy", "Accepted Phase 10 private utility source", "reports/governance_baseline_sources.md?s28_firstenergy", "repository_accepted_source", "Phase 10A accepted institutional source registry", "2026", "2026", "current corporate context", "private/service context", "observed", RETRIEVAL_DATE, "Supports private utility interface only; no facility-specific Toledo service territory is inferred."],
    ["phase10_s39_odot", "Accepted Phase 10 Ohio transportation source", "reports/governance_baseline_sources.md?s39_odot", "repository_accepted_source", "Phase 10A accepted institutional source registry", "2026", "2026", "current program context", "state/transport", "observed", RETRIEVAL_DATE, "Supports public transport planning context; no route-level passenger movement is modeled."],
    ["phase9_hazard_context", "Accepted Phase 9 climate and hazard system", "reports/phase9a_climate_natural_hazards_freeze_manifest.json", "repository_accepted_layer", "Phase 9A/9B accepted hazard context", "2026", "2026", "2025-2026 observations and context", "station/county/regional", "observed", RETRIEVAL_DATE, "Reused interface only; physical hazard is not converted to exposure or health outcome."],
    ["phase7_exposure_context", "Accepted Phase 7 environmental-health pathway context", "reports/phase7a_exposure_environmental_health_freeze_manifest.json", "repository_accepted_layer", "Phase 7A accepted exposure-context layer", "2026", "2026", "current pathway context", "regional/pathway", "observed", RETRIEVAL_DATE, "Reused pathway interface only; population presence is not exposure, dose, or illness."],
    ["phase6_ecology_context", "Accepted Phase 6 ecology and wetland context", "reports/phase6a_ecology_freeze_manifest.json", "repository_accepted_layer", "Phase 6A accepted ecology layer", "2026", "2026", "current ecological context", "regional/wetland", "observed", RETRIEVAL_DATE, "Reused ecological interface only; no habitat quality or biodiversity score is created."],
    ["phase8_biogeochemical_context", "Accepted Phase 8 biogeochemical and nutrient context", "reports/phase8a_biogeochemical_nutrient_flux_freeze_manifest.json", "repository_accepted_layer", "Phase 8A accepted nutrient/flux layer", "2026", "2026", "current system context", "regional/watershed", "observed", RETRIEVAL_DATE, "Reused material-flow interface only; no new load or treatment performance is estimated."],
    ["phase10_governance_context", "Accepted Phase 10 governance and service-responsibility context", "reports/phase10b_governance_dependencies_coordination_freeze_manifest.json", "repository_accepted_layer", "Phase 10A/10B accepted governance layer", "2026", "2026", "current institutional context", "municipal/county/regional", "observed", RETRIEVAL_DATE, "Reused governance interface only; municipal boundary is not a universal service territory."],
])
for state in STATES:
    wac_year = LODES_PRODUCT_YEARS[state]["wac"]
    rac_year = LODES_PRODUCT_YEARS[state]["rac"]
    SOURCE_ROWS.append([f"s11b_lodes_{state.lower()}_wac_rac", f"LEHD LODES 8.4 {state} WAC/RAC comparison", f"{LODES_BASE}/{STATES[state]}/wac/{STATES[state]}_wac_S000_JT00_{wac_year}.csv.gz;{LODES_BASE}/{STATES[state]}/rac/{STATES[state]}_rac_S000_JT00_{rac_year}.csv.gz", "federal_lehd", f"LODES 8.4 WAC/RAC comparison {wac_year}/{rac_year}", f"{wac_year}/{rac_year}", "2025", f"{wac_year}/{rac_year}", "county", "modeled", RETRIEVAL_DATE, "Derived workplace-minus-resident-worker comparison; directly comparable only when WAC and RAC product years match. Michigan is intentionally not assigned a difference because WAC and RAC vintages differ."])
SOURCES = pd.DataFrame(SOURCE_ROWS, columns=SOURCE_COLUMNS)

NODE_COLUMNS = ["node_id", "node_type", "name", "state", "geoid", "geographic_unit", "geographic_scale", "latitude", "longitude", "settlement_class", "study_frame", "source_id", "confidence", "reality_status", "canon_status", "notes"]
OBS_COLUMNS = ["record_id", "metric", "value", "units", "reference_year", "release_year", "estimate_period", "geographic_unit", "geographic_scale", "node_id", "source_product", "observed_estimated_modeled", "source_id", "confidence", "reality_status", "canon_status", "notes"]
REL_COLUMNS = ["relationship_id", "module", "source_node_id", "target_node_id", "relationship_type", "value", "units", "reference_year", "release_year", "estimate_period", "origin_geography", "destination_geography", "geographic_scale", "source_product", "observed_estimated_modeled", "source_id", "evidence_strength", "relationship_basis", "confidence", "reality_status", "canon_status", "notes"]
MOB_COLUMNS = ["record_id", "metric", "value", "units", "reference_year", "release_year", "estimate_period", "geographic_unit", "geographic_scale", "origin_node_id", "destination_node_id", "source_product", "observed_estimated_modeled", "source_id", "confidence", "reality_status", "canon_status", "notes"]
DEP_COLUMNS = ["dependency_id", "population_or_settlement_object", "system", "interface", "relationship_type", "documented_or_inferred", "spatial_scale", "evidence_strength", "source_id", "confidence", "reality_status", "canon_status", "notes"]
UNC_COLUMNS = ["uncertainty_id", "subject_id", "category", "statement", "resolution_status", "source_id", "confidence", "notes"]


def download(url: str, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        return path
    with requests.get(url, headers={"User-Agent": "western-basin-worldbuilding/phase11"}, stream=True, timeout=120) as response:
        response.raise_for_status()
        with path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    return path


def source_url(source_id: str) -> str:
    row = SOURCES.loc[SOURCES.source_id == source_id]
    assert len(row) == 1, source_id
    return str(row.iloc[0].url)


def fetch_acs(geo_ids: list[str], tables: list[str]) -> tuple[dict, dict]:
    """Fetch exact ACS release, splitting unsupported place IDs without guessing."""
    if not geo_ids:
        return {}, {"id": ACS_RELEASE, "name": "ACS 2024 5-year", "years": "2020-2024"}
    params = {"table_ids": ",".join(tables), "geo_ids": ",".join(geo_ids)}
    response = requests.get(ACS_ENDPOINT, params=params, headers={"User-Agent": "western-basin-worldbuilding/phase11"}, timeout=120)
    if response.ok:
        payload = response.json()
        assert payload.get("release", {}).get("id") == ACS_RELEASE, payload.get("release")
        return payload["data"], payload["release"]
    if len(geo_ids) == 1:
        return {}, {"id": ACS_RELEASE, "name": "ACS 2024 5-year", "years": "2020-2024"}
    midpoint = len(geo_ids) // 2
    left, release_left = fetch_acs(geo_ids[:midpoint], tables)
    right, release_right = fetch_acs(geo_ids[midpoint:], tables)
    left.update(right)
    return left, release_left if left else release_right


def val(data: dict, table: str, key: int) -> float | None:
    values = data.get(table, {}).get("estimate", {})
    raw = values.get(f"{table}{key:03d}")
    if raw is None:
        return None
    return float(raw)


def safe_share(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def parse_decennial_geography() -> pd.DataFrame:
    rows: list[dict] = []
    for state, prefix in STATES.items():
        zip_path = download(PL_ZIPS[state], CACHE / f"{prefix}2020.pl.zip")
        with zipfile.ZipFile(zip_path) as archive:
            member = f"{prefix}geo2020.pl"
            for line in archive.open(member):
                fields = line.decode("latin1").rstrip("\r\n").split("|")
                if len(fields) < 94 or fields[0] != "PLST" or fields[2] not in {"050", "160"}:
                    continue
                raw_geoid = fields[8]
                if fields[2] == "050" and raw_geoid.replace("0500000US", "") not in COUNTIES:
                    continue
                geoid = raw_geoid.replace("0500000US", "") if fields[2] == "050" else raw_geoid
                rows.append({
                    "geoid": geoid,
                    "state": state,
                    "summary_level": fields[2],
                    "name": fields[86],
                    "namelsad": fields[87],
                    "population_2020": int(float(fields[90] or 0)),
                    "housing_units_2020": int(float(fields[91] or 0)),
                    "latitude": float(fields[92]),
                    "longitude": float(fields[93]),
                    "land_area_m2": float(fields[84] or 0),
                })
    return pd.DataFrame(rows)


def load_county_geometry() -> gpd.GeoDataFrame:
    counties = gpd.read_file(CENSUS_COUNTIES)
    if counties.crs is None:
        counties = counties.set_crs(4326)
    counties["GEOID"] = counties["GEOID"].astype(str)
    counties = counties[counties.GEOID.isin(COUNTIES)].copy()
    counties["area_sq_mi"] = counties.to_crs(5070).geometry.area / 2_589_988.110336
    projected_centroids = counties.to_crs(5070).centroid.to_crs(4326)
    counties["centroid"] = projected_centroids
    counties["centroid_lon"] = projected_centroids.x
    counties["centroid_lat"] = projected_centroids.y
    return counties


def load_places(decennial: pd.DataFrame, counties: gpd.GeoDataFrame) -> pd.DataFrame:
    places = decennial[decennial.summary_level == "160"].copy()
    g = gpd.GeoDataFrame(places, geometry=[Point(xy) for xy in zip(places.longitude, places.latitude)], crs=4326)
    joined = gpd.sjoin(g, counties[["GEOID", "geometry"]], how="left", predicate="within")
    joined["county_geoid"] = joined["GEOID"]
    joined = joined[joined.county_geoid.notna()].copy()
    joined = joined[joined.population_2020 >= 5000].copy()
    # Keep a representative hierarchy without claiming official urban/rural status.
    joined = joined.sort_values("population_2020", ascending=False).groupby("geoid", as_index=False).first()
    joined["settlement_class"] = joined.population_2020.map(lambda n: "urban_center" if n >= 50000 else ("suburban_center" if n >= 10000 else "rural_settlement"))
    return pd.DataFrame(joined.drop(columns=["geometry", "index_right"], errors="ignore"))


def pep_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    county_path = download(PEP_COUNTY_URL, CACHE / "co-est2024-alldata.csv")
    place_path = download(PEP_PLACE_URL, CACHE / "sub-est2024.csv")
    counties = pd.read_csv(county_path, dtype=str, encoding="latin1")
    counties = counties[counties.SUMLEV == "050"].copy()
    counties["geoid"] = counties.STATE.str.zfill(2) + counties.COUNTY.str.zfill(3)
    counties = counties[counties.geoid.isin(COUNTIES)]
    places = pd.read_csv(place_path, dtype=str, encoding="latin1")
    places = places[places.SUMLEV == "162"].copy()
    places["geoid"] = places.STATE.str.zfill(2) + places.PLACE.str.zfill(5)
    return counties, places


def lodes_url(state: str, product: str) -> str:
    prefix = STATES[state]
    year = LODES_PRODUCT_YEARS[state].get(product, LODES_YEAR)
    if product == "xwalk":
        return f"{LODES_BASE}/{prefix}/{prefix}_xwalk.csv.gz"
    return f"{LODES_BASE}/{prefix}/{product}/{prefix}_{product}_S000_JT00_{year}.csv.gz" if product in {"wac", "rac"} else f"{LODES_BASE}/{prefix}/od/{prefix}_od_main_JT00_{year}.csv.gz"


def lodes_aggregate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    jobs: dict[str, int] = {geoid: 0 for geoid in COUNTIES}
    workers: dict[str, int] = {geoid: 0 for geoid in COUNTIES}
    flows: dict[tuple[str, str], int] = {}
    for state in STATES:
        prefix = STATES[state]
        years = LODES_PRODUCT_YEARS[state]
        wac_path = download(lodes_url(state, "wac"), CACHE / f"{prefix}_wac_S000_JT00_{years['wac']}.csv.gz")
        rac_path = download(lodes_url(state, "rac"), CACHE / f"{prefix}_rac_S000_JT00_{years['rac']}.csv.gz")
        od_path = download(lodes_url(state, "od"), CACHE / f"{prefix}_od_main_JT00_{years['od']}.csv.gz")
        wac = pd.read_csv(wac_path, compression="gzip", dtype={"w_geocode": str}, usecols=["w_geocode", "C000"])
        wac["geoid"] = wac.w_geocode.str[:5]
        for geoid, value in wac.groupby("geoid").C000.sum().items():
            if geoid in jobs:
                jobs[geoid] += int(value)
        rac = pd.read_csv(rac_path, compression="gzip", dtype={"h_geocode": str}, usecols=["h_geocode", "C000"])
        rac["geoid"] = rac.h_geocode.str[:5]
        for geoid, value in rac.groupby("geoid").C000.sum().items():
            if geoid in workers:
                workers[geoid] += int(value)
        for chunk in pd.read_csv(od_path, compression="gzip", dtype={"w_geocode": str, "h_geocode": str}, usecols=["w_geocode", "h_geocode", "S000"], chunksize=250000):
            chunk["work_geoid"] = chunk.w_geocode.str[:5]
            chunk["home_geoid"] = chunk.h_geocode.str[:5]
            chunk = chunk[chunk.work_geoid.isin(COUNTIES) & chunk.home_geoid.isin(COUNTIES)]
            for (home, work), value in chunk.groupby(["home_geoid", "work_geoid"]).S000.sum().items():
                flows[(home, work)] = flows.get((home, work), 0) + int(value)
    jobs_df = pd.DataFrame({"geoid": list(jobs), "jobs_2023": list(jobs.values())})
    workers_df = pd.DataFrame({"geoid": list(workers), "resident_workers_2023": list(workers.values())})
    flow_df = pd.DataFrame([{"home_geoid": h, "work_geoid": w, "commuter_flow_2023": v} for (h, w), v in flows.items()])
    return jobs_df, workers_df, flow_df


def add_obs(rows: list[list], record_id: str, metric: str, value, units: str, ref_year: str, release_year: str, period: str, unit: str, scale: str, node_id: str, product: str, status: str, source_id: str, confidence: str, notes: str, reality: str = "real", canon: str = "verified") -> None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return
    rows.append([record_id, metric, value, units, ref_year, release_year, period, unit, scale, node_id, product, status, source_id, confidence, reality, canon, notes])


def build_11a() -> dict:
    decennial = parse_decennial_geography()
    counties_geom = load_county_geometry()
    places = load_places(decennial, counties_geom)
    pep_counties, pep_places = pep_data()
    jobs, workers, flows = lodes_aggregate()

    county_rows = decennial[(decennial.summary_level == "050") & decennial.geoid.isin(COUNTIES)].copy()
    county_rows = county_rows.merge(counties_geom[["GEOID", "area_sq_mi", "centroid_lat", "centroid_lon"]], left_on="geoid", right_on="GEOID", how="left")
    pep_county_map = pep_counties.set_index("geoid").to_dict("index")
    pep_place_map = pep_places.set_index("geoid").to_dict("index")
    jobs_map = jobs.set_index("geoid").jobs_2023.to_dict()
    workers_map = workers.set_index("geoid").resident_workers_2023.to_dict()

    node_rows: list[list] = []
    node_meta: dict[str, dict] = {}
    for _, row in county_rows.iterrows():
        node_id = f"POP-ZONE-{row['geoid']}"
        county_name = str(row["name"])
        state = str(row["state"])
        geoid = str(row["geoid"])
        node_rows.append([node_id, "population_zone", f"{county_name} County, {state}", state, geoid, "county", "county", row["centroid_lat"], row["centroid_lon"], "county_population_zone", "western_basin_core_county_frame", "s11a_decennial_" + state.lower() + "_pl", "high", "real", "verified", "Analytical county frame; not a new jurisdiction or utility service territory."])
        node_meta[node_id] = {"geoid": geoid, "name": f"{county_name} County", "state": state, "scale": "county", "population": row["population_2020"], "lat": row["centroid_lat"], "lon": row["centroid_lon"], "area": row["area_sq_mi"]}
    for row in places.itertuples():
        node_id = f"MUNI-{row.geoid.replace('1600000US', '')}"
        pep_state = row.state.lower()
        node_rows.append([node_id, "municipality", row.namelsad, row.state, row.geoid, "place", "place", row.latitude, row.longitude, row.settlement_class, "western_basin_core_county_frame", "s11a_decennial_" + pep_state + "_pl", "high", "real", "verified", "Generalized place-size context; not an official urban/rural classification or service assignment."])
        node_meta[node_id] = {"geoid": row.geoid, "name": row.namelsad, "state": row.state, "scale": "place", "population": row.population_2020, "lat": row.latitude, "lon": row.longitude, "area": row.land_area_m2 / 2_589_988.110336, "county": row.county_geoid}
    # Employment centers are created in 11A so the node table is immutable during 11B.
    top_jobs = jobs.sort_values("jobs_2023", ascending=False).head(10)
    for row in top_jobs.itertuples():
        meta = node_meta.get(f"POP-ZONE-{row.geoid}")
        if not meta:
            continue
        node_id = f"EMP-{row.geoid}"
        node_rows.append([node_id, "employment_center", f"{meta['name']} employment concentration", meta["state"], row.geoid, "county", "county", meta["lat"], meta["lon"], "employment_concentration", "western_basin_core_county_frame", "s11b_lodes_" + meta["state"].lower() + "_wac", "high", "real", "verified", "LODES workplace count aggregated to county; not a list of individual employers or jobs at a specific address."])
        node_meta[node_id] = {"geoid": row.geoid, "name": f"{meta['name']} employment concentration", "state": meta["state"], "scale": "county", "population": None, "lat": meta["lat"], "lon": meta["lon"], "area": meta["area"], "lodes_wac_year": LODES_PRODUCT_YEARS[meta["state"]]["wac"]}
    nodes = pd.DataFrame(node_rows, columns=NODE_COLUMNS)

    county_geo_ids = [f"05000US{g}" for g in COUNTIES]
    place_geo_ids = [g.replace("1600000US", "16000US") for g in places.geoid]
    acs_county, release = fetch_acs(county_geo_ids, ["B01001", "B01002", "B11001", "B25001", "B25002", "B25010", "B25035", "B08301", "B08303"])
    acs_place, _ = fetch_acs(place_geo_ids, ["B01001", "B01002", "B11001", "B25001", "B25002", "B25010", "B25035"])
    obs: list[list] = []
    for node_id, meta in node_meta.items():
        if node_id.startswith("EMP-"):
            year = meta.get("lodes_wac_year", LODES_YEAR)
            add_obs(obs, f"OBS-{node_id}-JOBS", "job_count", jobs_map.get(meta["geoid"]), "jobs", year, "2025", year, meta["geoid"], "county", node_id, f"LODES 8.4 WAC {year}", "modeled", f"s11b_lodes_{meta['state'].lower()}_wac", "high", "Workplace jobs are not resident persons, households, or commuter flows.")
            continue
        geoid = meta["geoid"]
        dec = decennial.loc[decennial.geoid == geoid].iloc[0]
        source_dec = f"s11a_decennial_{meta['state'].lower()}_pl"
        add_obs(obs, f"OBS-{node_id}-POP20", "population_count", dec.population_2020, "persons", "2020", "2021", "2020-04-01 enumeration", meta["geoid"], meta["scale"], node_id, "2020 Decennial Census P.L. 94-171 P1", "observed", source_dec, "high", "Enumerated 2020 person count.")
        add_obs(obs, f"OBS-{node_id}-HU20", "housing_unit_count", dec.housing_units_2020, "housing_units", "2020", "2021", "2020-04-01 enumeration", meta["geoid"], meta["scale"], node_id, "2020 Decennial Census P.L. 94-171 H1/geography", "observed", source_dec, "high", "Enumerated housing units; not households or occupied units.")
        area = meta.get("area")
        add_obs(obs, f"OBS-{node_id}-DENS20", "population_density", dec.population_2020 / area if area else None, "persons_per_square_mile", "2020", "2021", "2020-04-01 enumeration and 2020 geography", meta["geoid"], meta["scale"], node_id, "2020 Decennial Census P.L. 94-171 plus Census geography area", "observed", "s11a_tiger_counties" if meta["scale"] == "county" else source_dec, "high", "Density is a derived ratio and is not a block-level observation.")
        pep = pep_county_map.get(geoid) if meta["scale"] == "county" else pep_place_map.get(geoid)
        pep_source = "s11a_pep_county_2024" if meta["scale"] == "county" else "s11a_pep_place_2024"
        if pep:
            pop20 = float(pep["POPESTIMATE2020"]); pop24 = float(pep["POPESTIMATE2024"])
            add_obs(obs, f"OBS-{node_id}-PEP20", "population_estimate", pop20, "persons", "2020", "2025", "July 1 annual estimate", geoid, meta["scale"], node_id, "2024 Vintage Population Estimates Program", "estimated", pep_source, "high", "PEP estimate; distinct from 2020 Census enumeration.")
            add_obs(obs, f"OBS-{node_id}-PEP24", "population_estimate", pop24, "persons", "2024", "2025", "July 1 annual estimate", geoid, meta["scale"], node_id, "2024 Vintage Population Estimates Program", "estimated", pep_source, "high", "Latest available PEP point estimate in this package; not a 2026 Census observation.")
            add_obs(obs, f"OBS-{node_id}-PEPCHG", "population_change", pop24 - pop20, "persons", "2020-2024", "2025", "July 1 annual estimates", geoid, meta["scale"], node_id, "2024 Vintage Population Estimates Program", "estimated", pep_source, "high", "Difference between PEP estimates; not a causal migration finding.")
            add_obs(obs, f"OBS-{node_id}-PEPCHGPCT", "population_change_percent", (pop24 - pop20) / pop20 * 100 if pop20 else None, "percent", "2020-2024", "2025", "July 1 annual estimates", geoid, meta["scale"], node_id, "2024 Vintage Population Estimates Program", "estimated", pep_source, "high", "Percentage change in PEP estimates; not a causal explanation.")
        acs = acs_county.get(f"05000US{geoid}") if meta["scale"] == "county" else acs_place.get(meta["geoid"].replace("1600000US", "16000US"))
        if not acs:
            continue
        acs_id = "s11a_acs_2024_5yr"
        period = "2020-2024"
        product = "ACS 2024 5-year detailed tables"
        add_obs(obs, f"OBS-{node_id}-ACSP", "population_count", val(acs, "B01001", 1), "persons", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "ACS estimate; not an enumerated 2026 count.")
        add_obs(obs, f"OBS-{node_id}-HH", "household_count", val(acs, "B11001", 1), "households", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "Households are not persons or housing units.")
        add_obs(obs, f"OBS-{node_id}-HUACS", "housing_unit_count", val(acs, "B25001", 1), "housing_units", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "ACS housing-unit estimate; distinct from 2020 enumeration.")
        occupied = val(acs, "B25002", 2); vacant = val(acs, "B25002", 3); total_hu = val(acs, "B25002", 1)
        add_obs(obs, f"OBS-{node_id}-OCC", "occupied_housing_units", occupied, "housing_units", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "Occupied unit estimate; not a utility connection or household welfare measure.")
        add_obs(obs, f"OBS-{node_id}-VAC", "vacant_housing_units", vacant, "housing_units", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "Vacancy is descriptive housing context; no reason for vacancy is inferred.")
        add_obs(obs, f"OBS-{node_id}-VACSH", "vacancy_rate", safe_share(vacant, total_hu) * 100 if vacant is not None and total_hu else None, "percent", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "high", "Vacancy rate is not a neighborhood-quality or vulnerability score.")
        add_obs(obs, f"OBS-{node_id}-MEDAGE", "median_age", val(acs, "B01002", 1), "years", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "moderate", "Descriptive aggregate age context only.")
        under18 = sum((val(acs, "B01001", i) or 0) for i in list(range(3, 7)) + list(range(27, 31)))
        age65 = sum((val(acs, "B01001", i) or 0) for i in list(range(20, 26)) + list(range(44, 50)))
        total_pop = val(acs, "B01001", 1)
        add_obs(obs, f"OBS-{node_id}-UNDER18", "age_under_18_share", safe_share(under18, total_pop) * 100 if total_pop else None, "percent", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "moderate", "Descriptive aggregate age structure; no vulnerability ranking.")
        add_obs(obs, f"OBS-{node_id}-AGE65", "age_65_plus_share", safe_share(age65, total_pop) * 100 if total_pop else None, "percent", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "moderate", "Descriptive aggregate age structure; no vulnerability ranking.")
        add_obs(obs, f"OBS-{node_id}-HHSIZE", "average_household_size", val(acs, "B25010", 1), "persons_per_household", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "moderate", "Aggregate household-size estimate; no household-level inference.")
        add_obs(obs, f"OBS-{node_id}-HOUSAGE", "median_year_structure_built", val(acs, "B25035", 1), "year", "2024", "2025", period, geoid, meta["scale"], node_id, product, "estimated", acs_id, "moderate", "Descriptive housing-age context; not a condition or maintenance score.")
        if meta["scale"] == "county":
            commute_total = val(acs, "B08301", 1)
            commute_metrics = [("drive_alone_share", safe_share(val(acs, "B08301", 3), commute_total) * 100 if commute_total else None), ("carpool_share", safe_share(val(acs, "B08301", 4), commute_total) * 100 if commute_total else None), ("public_transit_share", safe_share(val(acs, "B08301", 10), commute_total) * 100 if commute_total else None), ("walk_share", safe_share(val(acs, "B08301", 19), commute_total) * 100 if commute_total else None), ("work_from_home_share", safe_share(val(acs, "B08301", 21), commute_total) * 100 if commute_total else None), ("commute_45_plus_share", safe_share(sum((val(acs, "B08303", i) or 0) for i in (11, 12, 13)), val(acs, "B08303", 1)) * 100 if val(acs, "B08303", 1) else None)]
            for metric, value in commute_metrics:
                add_obs(obs, f"OBS-{node_id}-{metric.upper()}", metric, value, "percent", "2024", "2025", period, geoid, meta["scale"], node_id, "ACS 2024 5-year B08301/B08303", "estimated", "s11b_acs_commute_2024", "moderate", "Residence-based commuting estimate; commuting is not migration or individual movement.")
    observations = pd.DataFrame(obs, columns=OBS_COLUMNS)

    rel: list[list] = []
    counties_by_place = {r.geoid: r.county_geoid for r in places.itertuples()}
    idx = 1
    for node_id in nodes.loc[nodes.node_type == "municipality", "node_id"]:
        geoid = node_meta[node_id]["geoid"]
        county = counties_by_place.get(geoid)
        if county in COUNTIES:
            rel.append([f"REL-{idx:04d}", "11A", f"POP-ZONE-{county}", node_id, "contains_settlement", "", "", "2020", "2021", "2020-04-01 geography", county, geoid, "county/place", "2020 Census TIGER/PL geography", "observed", f"s11a_decennial_{node_meta[node_id]['state'].lower()}_pl", "high", "point-in-county geographic containment", "high", "real", "verified", "Containment does not mean municipal residents equal county total."]); idx += 1
    for row in top_jobs.itertuples():
        employment_id = f"EMP-{row.geoid}"
        year = LODES_PRODUCT_YEARS[node_meta[f'POP-ZONE-{row.geoid}']['state']]['wac']
        rel.append([f"REL-{idx:04d}", "11A", f"POP-ZONE-{row.geoid}", employment_id, "employment_concentration", int(row.jobs_2023), "jobs", year, "2025", year, row.geoid, row.geoid, "county", f"LODES 8.4 WAC {year}", "modeled", f"s11b_lodes_{node_meta[f'POP-ZONE-{row.geoid}']['state'].lower()}_wac", "high", "aggregated workplace job concentration", "high", "real", "verified", "Jobs are not resident population or commuter flows."]); idx += 1
    relationships = pd.DataFrame(rel, columns=REL_COLUMNS)
    observations.to_csv(ANALYSIS / "population_settlement_observations.csv", index=False)
    nodes.to_csv(ANALYSIS / "population_settlement_nodes.csv", index=False)
    relationships.to_csv(NETWORKS / "population_settlement_relationships.csv", index=False)
    SOURCES.to_csv(ANALYSIS / "population_settlement_sources.csv", index=False)
    build_uncertainty()
    render_map35(nodes, observations, counties_geom)
    build_11a_reports(nodes, observations, relationships)
    artifacts = [ANALYSIS / "population_settlement_nodes.csv", ANALYSIS / "population_settlement_observations.csv", NETWORKS / "population_settlement_relationships.csv", ANALYSIS / "population_settlement_sources.csv", ANALYSIS / "population_settlement_uncertainty.csv", MAPS / "35_population_settlement_2026.png", MAPS / "35_population_settlement_2026.svg", REPORTS / "population_settlement_sources.md", REPORTS / "population_settlement_assumptions.md", REPORTS / "population_settlement_findings.md", REPORTS / "population_settlement_qa.md"]
    manifest = {"phase": "11A", "status": "implemented_validated_pending_sol_acceptance", "map_number": 35, "counts": {"nodes": len(nodes), "population_observations": len(observations), "relationships": len(relationships), "sources": len(SOURCES)}, "artifacts": artifact_metadata(artifacts), "protected_scope": "Phase 11A working baseline; Phase 1-10 accepted/frozen artifacts unchanged", "phase11c_implemented": False}
    (REPORTS / "population_settlement_baseline_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"nodes": nodes, "observations": observations, "relationships": relationships, "sources": SOURCES, "counties": counties_geom, "jobs": jobs, "workers": workers, "flows": flows, "node_meta": node_meta}


def build_uncertainty() -> None:
    rows = [
        ["UNC-001", "PROJECT", "spatial_frame", "The county frame is an analytical Western Basin core frame, not a canonical jurisdiction, watershed polygon, or mutually exclusive regional identity.", "open", "s11a_tiger_counties", "high", "Do not present the frame as the Western Basin's only valid boundary."],
        ["UNC-002", "PROJECT", "vintage", "No single complete 2026 Census exists; 2020 enumeration, 2024 PEP, and 2024 ACS 5-year estimates are combined with their actual periods preserved.", "qualified", "s11a_pep_county_2024", "high", "Older products are not relabeled as observed 2026 values."],
        ["UNC-003", "PROJECT", "scale", "County and place values do not represent block, tract, neighborhood, or household-level distributions.", "open", "s11a_tiger_counties", "high", "No small-area inference is made from county/place records."],
        ["UNC-004", "PROJECT", "household_person_unit", "Household, housing-unit, and person counts are distinct and are not converted into one another without an explicit source-derived metric.", "qualified", "s11a_acs_2024_5yr", "high", "No household-level profiles are created."],
        ["UNC-005", "PROJECT", "growth_interpretation", "PEP change indicates estimated change in resident population, not why people moved and not a causal migration explanation.", "open", "s11a_pep_county_2024", "high", "Migration causation is outside this phase."],
        ["UNC-006", "PROJECT", "employment_scale", "LODES job and worker values are aggregated administrative/modelled tabulations; they are not individual workers, employers, or exact workplace addresses.", "qualified", "s11b_lodes_oh_wac", "high", "County aggregation is used for system interfaces."],
        ["UNC-007", "PROJECT", "utility_assignment", "Population presence does not assign each resident to a drinking-water, wastewater, electricity, or heating service territory.", "open", "phase10_s03_toledo_treatment", "high", "Exact service territories require separate authoritative data."],
        ["UNC-008", "PROJECT", "existing_hold", "Great Black Swamp remains C — HOLD / noncanonical and is not used as a population boundary.", "open", "phase6_ecology_context", "high", "No historical geometry is canonicalized."],
        ["UNC-009", "PROJECT", "existing_hold", "The Toledo intake-coordinate discrepancy remains unresolved and is not resolved by population or service analysis.", "open", "phase10_s03_toledo_treatment", "high", "No intake coordinate is selected by this phase."],
    ]
    pd.DataFrame(rows, columns=UNC_COLUMNS).to_csv(ANALYSIS / "population_settlement_uncertainty.csv", index=False)


def artifact_metadata(paths: list[Path]) -> dict:
    return {str(path.relative_to(ROOT)).replace("\\", "/"): {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths}


def source_block() -> str:
    return "\n".join(["## Sources", ""] + [f"[{i}] {row.url}" for i, row in enumerate(SOURCES.itertuples(), 1)]) + "\n"


def build_11a_reports(nodes: pd.DataFrame, obs: pd.DataFrame, rel: pd.DataFrame) -> None:
    county_obs = obs[obs.geographic_scale == "county"]
    pop = county_obs[(county_obs.metric == "population_count") & county_obs.source_id.str.contains("decennial")].sort_values("value", ascending=False)
    density = county_obs[county_obs.metric == "population_density"].sort_values("value", ascending=False)
    growth = county_obs[county_obs.metric == "population_change_percent"].sort_values("value", ascending=False)
    decline = growth.sort_values("value")
    age = county_obs[county_obs.metric == "age_65_plus_share"].sort_values("value", ascending=False)
    top_places = obs[(obs.metric == "population_count") & (obs.geographic_scale == "place") & obs.source_id.str.contains("decennial")].sort_values("value", ascending=False).head(10)
    label_map = dict(zip(nodes.node_id, nodes.name))
    def label(row) -> str:
        return label_map.get(row.node_id, str(row.geographic_unit))
    text_sources = """# Phase 11A Population & Settlement Sources

This package uses the 2020 Decennial Census P.L. 94-171 summary files for enumerated population and housing units at county/place scale.[1][2][3] Recent change uses the 2024 Vintage Population Estimates Program county and place files, whose annual July 1 estimates are not a 2026 Census.[4][5] Households, occupancy/vacancy, age structure, household size, housing age, and county commuting context use ACS 2024 5-year estimates retrieved through the Census Reporter programmatic mirror of Census tables.[6][9]

Census TIGER/TIGERweb county/place geography supports the analytical frame and map geometry.[7][8] LODES 8.4 WAC/RAC/OD products provide generalized workplace, residence, and origin-destination job tabulations, with Ohio and Indiana 2023 files and Michigan 2021 WAC/OD plus 2023 RAC in the current public release.[10][11][12][13][14][15][16][17][18][19][20][21] They are aggregated administrative/modelled products rather than individual movement records.

The cross-system dependency layer reuses accepted Phase 6–10 context without rebuilding those systems. It does not assign every resident to a utility territory, convert population presence to exposure or illness, or turn municipal boundaries into service territories.

""" + source_block()
    assumptions = f"""# Phase 11A Population & Settlement Assumptions

## Analytical frame

The package uses {len(COUNTIES)} selected counties in Ohio, Michigan, and Indiana as an explicit Western Basin core-county study frame. This frame is an analytical convenience for systems comparison, not a new canonical macroregion, jurisdiction, watershed boundary, or timeless cultural geography.

## Vintages and scales

2020 Decennial P.L. 94-171 values are enumerated 2020 counts. PEP 2024 values are July 1 annual estimates through 2024. ACS 2024 5-year values describe the 2020–2024 estimate period. LODES products retain their native years: Ohio and Indiana WAC/RAC/OD are 2023; Michigan WAC/OD are 2021 and RAC is 2023. The package never labels these as one homogeneous 2026 observation.

Person, household, housing-unit, density, worker, job, and commuter-flow metrics remain separate. County and place values are not tract, block-group, block, or household measurements. Place-size settlement classes are transparent generalized context labels, not official urban/rural classifications.

## Boundaries

Age and household composition are descriptive aggregate context only. No individual profiles, household-level inference, protected-class ranking, vulnerability/EJ composite, health outcome, dose, exposure, causal migration explanation, exact service territory, or future demographic record is created. Great Black Swamp remains C — HOLD / noncanonical; the Toledo intake-coordinate discrepancy remains unresolved.

## Package counts

The working baseline contains {len(nodes)} nodes and {len(obs)} population/settlement observations. Relationships are structural containment and employment-concentration interfaces; they do not sum place populations to county totals.
"""
    growth_rows = "\n".join(f"- {label(r)}: {r.value:.2f}%" for r in growth.head(5).itertuples())
    decline_rows = "\n".join(f"- {label(r)}: {r.value:.2f}%" for r in decline.head(5).itertuples())
    findings = f"""# Phase 11A Population & Settlement Findings, 2026 baseline

## Concentration and hierarchy

FACT: The largest enumerated county population zones in this frame are:
""" + "\n".join(f"- {label(r)}: {int(r.value):,} persons (2020 Census enumeration).[1][2][3]" for r in pop.head(8).itertuples()) + f"""

FACT: The largest selected place nodes are:
""" + "\n".join(f"- {label(r)}: {int(r.value):,} persons (2020 Census enumeration).[1][2][3]" for r in top_places.itertuples()) + f"""

INFERENCE: The settlement system is anchored by Toledo and its adjacent Lucas County urbanized interface, with Bowling Green/Wood County, Findlay/Hancock County, Fort Wayne/Allen County, Sandusky/Fremont and the western Lake Erie shoreline, and smaller county-seat/rural centers forming a nested urban–suburban–rural pattern. The place-size labels are generalized context, not an official urban/rural classification.[7][8]

## Recent change

FACT: PEP 2020–2024 percentage changes identify the following estimated growth cases in the selected county frame:
{growth_rows}

FACT: The following selected county zones show the largest estimated declines in the same PEP series:
{decline_rows}

INFERENCE: These changes describe estimated resident-population change between PEP vintages; the package does not infer causes, migration mechanisms, or residential relocation pathways.[4]

## Age and household context

FACT: ACS 2024 5-year age and household measures show substantial variation across county and place scales. The highest aggregate 65-plus shares among county zones are:
""" + "\n".join(f"- {r.geographic_unit}: {r.value:.1f}% age 65+ (ACS estimate period 2020–2024).[6]" for r in age.head(6).itertuples()) + f"""

INFERENCE: Aging is a regional demographic context relevant to settlement and service planning, but it is not a vulnerability score and is not used to rank communities.[6]

## Housing

FACT: ACS records distinguish households, total housing units, occupied units, and vacant units. Vacancy and housing age vary by county/place; vacancy is not assigned a cause, condition, desirability, or risk meaning.[6]

INFERENCE: Housing-unit concentration and older housing stock provide context for energy, maintenance, stormwater, and transport interfaces in Phase 11B. These are system interfaces, not automatic causal claims.

## Employment concentration

FACT: LODES WAC identifies county-level workplace job concentrations distinct from resident population. Employment-center nodes are generalized county concentrations, not lists of employers or individual jobs.[10][11][12][13][14][15][16][17][18][19][20][21]

## Limitations

UNCERTAINTY: No single 2026 Census exists; ACS is an estimate over 2020–2024, PEP is an annual estimate through July 1, 2024, and LODES is a modelled administrative tabulation. County/place geography cannot support neighborhood or household inference. The analytical county frame is not a canonical boundary. Exact utility service populations, residential relocation causes, seasonal populations, institutional populations, and modeled ambient population remain outside this package.

""" + source_block()
    qa = f"""# Phase 11A Population & Settlement QA

The builder produced {len(nodes)} nodes, {len(obs)} observations, and {len(rel)} structural/employment relationships for Map 35. Python validation checks exact columns, IDs, units, source references, vintages, geographic scales, person/household/housing/density/job distinctions, observed/estimated/modeled status, Census versus LODES separation, and absence of individual-level or vulnerability constructs.

The independent R validator re-reads the generated files and recomputes the principal counts, enum checks, source references, map artifact/text checks, working-manifest hashes, prior Phase 1–10 freeze integrity, active holds, and Phase 11C absence through a separate code path.

Negative scope: no social-vulnerability or EJ score, protected-class ranking, individual profile, individual movement, dose, illness, utility-territory assignment, unsupported demographic forecast, Indigenous-history/HGIS layer, or Phase 11C implementation.
"""
    (REPORTS / "population_settlement_sources.md").write_text(text_sources, encoding="utf-8")
    (REPORTS / "population_settlement_assumptions.md").write_text(assumptions, encoding="utf-8")
    (REPORTS / "population_settlement_findings.md").write_text(findings, encoding="utf-8")
    (REPORTS / "population_settlement_qa.md").write_text(qa, encoding="utf-8")


def render_map35(nodes: pd.DataFrame, obs: pd.DataFrame, counties: gpd.GeoDataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    county_pop = obs[(obs.metric == "population_count") & (obs.source_id.str.contains("decennial"))].set_index("geographic_unit")["value"]
    county_density = obs[(obs.metric == "population_density") & (obs.source_id == "s11a_tiger_counties")].set_index("geographic_unit")["value"]
    plot = counties.copy(); plot["density"] = plot.GEOID.map(county_density).fillna(0); plot["population"] = plot.GEOID.map(county_pop).fillna(0)
    fig = plt.figure(figsize=(16, 10), facecolor="#f2eadb")
    ax = fig.add_axes([0.04, 0.10, 0.62, 0.82], facecolor="#e8e0cf")
    plot.plot(ax=ax, column="density", cmap="YlOrRd", linewidth=0.55, edgecolor="#80745f", legend=True, legend_kwds={"label": "2020 Census persons per square mile (derived)", "shrink": 0.65})
    muni = nodes[nodes.node_type == "municipality"].copy()
    colors = {"urban_center": "#8b2f3d", "suburban_center": "#c77b30", "rural_settlement": "#3d6f63"}
    for cls, group in muni.groupby("settlement_class"):
        ax.scatter(group.longitude, group.latitude, s=(group.population_2020 if "population_2020" in group else 1), c=colors.get(cls, "#444"), alpha=0.82, edgecolor="#f2eadb", linewidth=0.5, label=cls.replace("_", " "))
    ax.set_xlim(-86.0, -82.2); ax.set_ylim(40.1, 42.6); ax.set_axis_off()
    side = fig.add_axes([0.70, 0.08, 0.27, 0.84]); side.axis("off")
    side.text(0.02, 0.98, "MAP 35 — WESTERN BASIN\nPOPULATION & SETTLEMENT, 2026", va="top", fontsize=13, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.02, 0.83, "2020 Census enumeration with 2024 PEP and ACS estimate context. County shading is generalized density; dots are selected Census places. This is an analytical frame, not a utility territory, jurisdiction, or canonical macroregion.", va="top", fontsize=8.3, color="#3f4645", linespacing=1.3)
    side.text(0.02, 0.60, "SETTLEMENT CONTEXT", fontsize=9.5, weight="bold", color="#17384b")
    for y, line in zip([0.56, 0.51, 0.46], ["dark red — urban center", "ochre — suburban center", "green — rural settlement"]): side.text(0.04, y, "• " + line, fontsize=8, color="#3f4645")
    side.text(0.02, 0.35, "BOUNDARIES", fontsize=9.5, weight="bold", color="#17384b")
    side.text(0.04, 0.31, "Person ≠ household ≠ housing unit ≠ density. ACS/PEP estimates retain their actual periods. No neighborhood inference, vulnerability score, protected-class ranking, exact utility assignment, or future population is shown. Great Black Swamp remains C — HOLD; Toledo intake-coordinate discrepancy remains unresolved.", va="top", fontsize=7.7, color="#3f4645", linespacing=1.3)
    ax.legend(loc="lower left", frameon=True, facecolor="#f2eadb", fontsize=7.5)
    base = MAPS / "35_population_settlement_2026"
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(base.with_suffix(".svg"))


def normalize_svg(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'id="p[0-9a-f]+"', 'id="p11population"', text)
    text = re.sub(r'url\(#p[0-9a-f]+\)', 'url(#p11population)', text)
    path.write_text("\n".join(line.rstrip() for line in text.splitlines()) + "\n", encoding="utf-8", newline="\n")


def build_11b(package: dict) -> dict:
    nodes = package["nodes"]; obs_a = package["observations"]; counties = package["counties"]; jobs = package["jobs"]; workers = package["workers"]; flows = package["flows"]; node_meta = package["node_meta"]
    baseline_path = REPORTS / "population_settlement_baseline_manifest.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    for rel, meta in baseline["artifacts"].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == meta["sha256"], rel
    mob: list[list] = []
    node_by_geoid = {v["geoid"]: k for k, v in node_meta.items() if k.startswith("POP-ZONE-")}
    for geoid in COUNTIES:
        node_id = node_by_geoid[geoid]; state = COUNTIES[geoid][0]
        year_wac = LODES_PRODUCT_YEARS[state]["wac"]
        year_rac = LODES_PRODUCT_YEARS[state]["rac"]
        add_mob(mob, f"MOB-{geoid}-JOBS", "job_count", jobs.loc[jobs.geoid == geoid, "jobs_2023"].iloc[0], "jobs", year_wac, "2025", year_wac, geoid, "county", node_id, "", f"LODES 8.4 WAC {year_wac}", "modeled", f"s11b_lodes_{state.lower()}_wac", "high", "Workplace job count; not resident population or commuter flow.")
        add_mob(mob, f"MOB-{geoid}-WORKERS", "worker_count", workers.loc[workers.geoid == geoid, "resident_workers_2023"].iloc[0], "workers", year_rac, "2025", year_rac, geoid, "county", node_id, "", f"LODES 8.4 RAC {year_rac}", "modeled", f"s11b_lodes_{state.lower()}_rac", "high", "Residence-based worker tabulation; not population count or migration.")
        jobs_n = int(jobs.loc[jobs.geoid == geoid, "jobs_2023"].iloc[0]); workers_n = int(workers.loc[workers.geoid == geoid, "resident_workers_2023"].iloc[0])
        if year_wac == year_rac:
            combined_year = f"{year_wac}/{year_rac}"
            add_mob(mob, f"MOB-{geoid}-BAL", "workplace_residence_difference", jobs_n - workers_n, "jobs_minus_workers", combined_year, "2025", combined_year, geoid, "county", node_id, "", f"LODES 8.4 WAC/RAC comparison {combined_year}", "modeled", f"s11b_lodes_{state.lower()}_wac_rac", "high", "Same-vintage workplace-minus-resident-worker comparison; not a causal employment-access or migration measure.")
    for row in obs_a[(obs_a.source_id == "s11b_acs_commute_2024")].itertuples():
        add_mob(mob, f"MOB-{row.geographic_unit}-{row.metric}", row.metric, row.value, row.units, row.reference_year, row.release_year, row.estimate_period, row.geographic_unit, row.geographic_scale, row.node_id, "", row.source_product, row.observed_estimated_modeled, row.source_id, row.confidence, row.notes)
    for row in flows.itertuples():
        if row.home_geoid == row.work_geoid:
            continue
        if int(row.commuter_flow_2023) < 25:
            continue
        year_od = LODES_PRODUCT_YEARS[COUNTIES[row.work_geoid][0]]["od"]
        add_mob(mob, f"MOB-FLOW-{row.home_geoid}-{row.work_geoid}", "commuter_flow", int(row.commuter_flow_2023), "jobs", year_od, "2025", year_od, row.home_geoid, "county_pair", node_by_geoid[row.home_geoid], node_by_geoid[row.work_geoid], f"LODES 8.4 OD county aggregation {year_od}", "modeled", f"s11b_lodes_{COUNTIES[row.work_geoid][0].lower()}_od", "high", "Aggregated residence-to-workplace interface; no individual path or employer inference.")
    mobility = pd.DataFrame(mob, columns=MOB_COLUMNS)
    rel_rows: list[list] = []
    flow_top = flows[(flows.home_geoid != flows.work_geoid) & (flows.commuter_flow_2023 >= 25)].sort_values("commuter_flow_2023", ascending=False)
    for i, row in enumerate(flow_top.itertuples(), 1):
        year_od = LODES_PRODUCT_YEARS[COUNTIES[row.work_geoid][0]]["od"]
        rel_rows.append([f"MREL-{i:04d}", "11B", node_by_geoid[row.home_geoid], node_by_geoid[row.work_geoid], "commuting_interface_with", int(row.commuter_flow_2023), "jobs", year_od, "2025", year_od, row.home_geoid, row.work_geoid, "county_pair", f"LODES 8.4 OD {year_od}", "modeled", f"s11b_lodes_{COUNTIES[row.work_geoid][0].lower()}_od", "high", "generalized residence-to-workplace relationship", "high", "real", "verified", "Commuting is not migration, passenger surveillance, or a route model."])
    mobility_rel = pd.DataFrame(rel_rows, columns=REL_COLUMNS)
    mobility.to_csv(ANALYSIS / "population_mobility_observations.csv", index=False)
    mobility_rel.to_csv(NETWORKS / "population_mobility_relationships.csv", index=False)
    deps = build_dependencies(nodes, obs_a, mobility, node_by_geoid)
    deps.to_csv(ANALYSIS / "population_system_dependency_register.csv", index=False)
    matrix = build_matrix(nodes, obs_a, mobility, node_by_geoid, deps)
    matrix.to_csv(ANALYSIS / "population_system_dependency_matrix.csv", index=False)
    render_map36(nodes, mobility_rel, counties)
    build_11b_reports(nodes, obs_a, mobility, mobility_rel, deps, matrix)
    artifacts = [ANALYSIS / "population_mobility_observations.csv", NETWORKS / "population_mobility_relationships.csv", ANALYSIS / "population_system_dependency_register.csv", ANALYSIS / "population_system_dependency_matrix.csv", MAPS / "36_population_mobility_dependencies_2026.png", MAPS / "36_population_mobility_dependencies_2026.svg", REPORTS / "population_mobility_sources.md", REPORTS / "population_mobility_assumptions.md", REPORTS / "population_mobility_findings.md", REPORTS / "population_mobility_qa.md"]
    working = {"phase": "11A/11B", "status": "implemented_validated_pending_sol_acceptance", "maps": [35, 36], "counts": {"settlement_nodes": len(nodes), "population_observations": len(obs_a), "settlement_relationships": len(pd.read_csv(NETWORKS / "population_settlement_relationships.csv")), "mobility_observations": len(mobility), "mobility_relationships": len(mobility_rel), "dependencies": len(deps), "matrix_rows": len(matrix), "sources": len(SOURCES)}, "baseline_manifest": "reports/population_settlement_baseline_manifest.json", "artifacts": artifact_metadata(artifacts), "phase10_protected": True, "phase11c_implemented": False, "active_holds_preserved": True}
    (REPORTS / "phase11_working_manifest.json").write_text(json.dumps(working, indent=2) + "\n", encoding="utf-8")
    return {"mobility": mobility, "mobility_rel": mobility_rel, "deps": deps, "matrix": matrix}


def add_mob(rows: list[list], record_id: str, metric: str, value, units: str, ref: str, release: str, period: str, geographic_unit: str, scale: str, origin: str, destination: str, product: str, status: str, source_id: str, confidence: str, notes: str) -> None:
    rows.append([record_id, metric, value, units, ref, release, period, geographic_unit, scale, origin, destination, product, status, source_id, confidence, "real", "verified", notes])


def build_dependencies(nodes: pd.DataFrame, obs: pd.DataFrame, mobility: pd.DataFrame, node_by_geoid: dict[str, str]) -> pd.DataFrame:
    rows = []
    systems = [
        ("water", "drinking-water service dependence", "functional_service_dependence", "inferred", "county/place", "limited", "phase10_governance_context", "Generalized service-responsibility context only; no state-specific operator or exact resident-to-utility assignment."),
        ("wastewater", "wastewater collection/treatment interface", "functional_service_dependence", "inferred", "county/place", "limited", "phase10_governance_context", "Generalized service-responsibility context only; no state-specific permit, sewer territory, or load claim."),
        ("energy", "electricity/heating dependence", "functional_service_dependence", "inferred", "county/place", "moderate", "phase10_s24_pjm", "Regional wholesale/high-voltage context only; no local distribution assignment, demand model, or outage probability."),
        ("transport", "residence/workplace mobility interface", "functional_service_dependence", "inferred", "county/county_pair", "moderate", "state_lodes_od", "State-matched LODES OD supports generalized commuting context; the dependency is inferred and exposes no individual paths or passenger surveillance."),
        ("climate_hazard", "settlement to physical hazard interface", "physical_hazard_interface", "inferred", "county/regional", "limited", "phase9_hazard_context", "Hazard interface is not exposure, dose, or health outcome."),
        ("environmental_health", "settlement to accepted pathway context", "pathway_interface", "reused_context", "county/regional", "limited", "phase7_exposure_context", "Population presence is not exposure, dose, illness, or risk."),
        ("ecology_land", "settlement and land/wetland interface", "land_cover_interface", "inferred", "county/regional", "limited", "phase6_ecology_context", "No habitat quality, biodiversity, or ecological-risk score."),
        ("biogeochemical", "stormwater/wastewater/nutrient interface", "material_flow_interface", "inferred", "county/watershed", "limited", "phase8_biogeochemical_context", "No new nutrient load, concentration, or treatment outcome."),
        ("housing_infrastructure", "housing age/units and maintenance/energy context", "contextual_interface", "inferred", "county/place", "limited", "s11a_acs_2024_5yr", "Housing context is not a condition, desirability, or vulnerability score."),
        ("governance", "municipal boundary/service-responsibility interface", "institutional_interface", "inferred", "municipal/county", "moderate", "phase10_governance_context", "Boundary, operator, service territory, and population served remain distinct."),
    ]
    node_state = dict(zip(nodes.node_id, nodes.state))
    objects = nodes[nodes.node_type.isin(["population_zone", "municipality"])].node_id.tolist()
    for idx, obj in enumerate(objects, 1):
        for system, interface, rel_type, basis, scale, strength, source, note in systems:
            row_source = source
            if system == "transport":
                row_source = f"s11b_lodes_{str(node_state[obj]).lower()}_od"
            row_note = note
            if system == "wastewater" and node_state[obj] == "OH":
                row_source = "phase10_s05_ohio_npdes"
                row_note = "Ohio regulatory program context only; no exact sewer territory, treatment load, or resident assignment."
            if system == "water" and obj in {"POP-ZONE-39095", "MUNI-3977000"}:
                row_source = "phase10_s03_toledo_treatment"
                row_note = "Toledo operator context only; no exact service territory or resident assignment."
            row_basis = "inferred" if system in {"water", "wastewater", "transport", "energy", "governance"} else basis
            row_confidence = "limited" if system in {"water", "wastewater", "transport"} else ("moderate" if strength == "moderate" else "limited")
            rows.append([f"DEP-{idx:04d}-{system}", obj, system, interface, rel_type, row_basis, scale, strength, row_source, row_confidence, "real", "inferred", row_note])
    return pd.DataFrame(rows, columns=DEP_COLUMNS)


def build_matrix(nodes: pd.DataFrame, obs: pd.DataFrame, mobility: pd.DataFrame, node_by_geoid: dict[str, str], deps: pd.DataFrame) -> pd.DataFrame:
    dimensions = ["settlement_concentration", "mobility_dependency", "employment_access", "housing_constraint", "water_dependency", "wastewater_dependency", "energy_dependency", "transport_dependency", "climate_hazard_interface", "environmental_health_interface", "governance_dependency", "service_access", "data_certainty"]
    rows = []
    pop = obs[(obs.metric == "population_count") & (obs.source_id.str.contains("decennial"))].set_index("node_id")["value"].to_dict()
    jobs = mobility[mobility.metric == "job_count"].set_index("origin_node_id")["value"].to_dict()
    dep_dimension = {"water": "water_dependency", "wastewater": "wastewater_dependency", "energy": "energy_dependency", "transport": "transport_dependency", "climate_hazard": "climate_hazard_interface", "environmental_health": "environmental_health_interface", "governance": "governance_dependency"}
    for _, row in nodes[nodes.node_type.isin(["population_zone", "municipality"])].iterrows():
        p = pop.get(row.node_id, 0)
        values = {d: "unknown" for d in dimensions}
        values["settlement_concentration"] = "strong" if p >= 250000 else ("moderate" if p >= 50000 else "limited")
        object_deps = deps[deps.population_or_settlement_object == row.node_id]
        source_ids = []
        evidence = []
        for _, dep in object_deps.iterrows():
            source_ids.append(str(dep.source_id))
            evidence.append(str(dep.evidence_strength))
            if dep.system in dep_dimension:
                values[dep_dimension[dep.system]] = str(dep.evidence_strength)
        values["mobility_dependency"] = values["transport_dependency"]
        values["data_certainty"] = "limited" if "limited" in evidence else ("moderate" if evidence else "unknown")
        notes = "Qualitative interface matrix derived from the dependency register; sources=" + ";".join(dict.fromkeys(source_ids)) + "; evidence_strengths=" + ";".join(dict.fromkeys(evidence)) + "; UNKNOWN is not LOW and dependence is not vulnerability."
        rows.append([row["node_id"], row["node_type"], row["name"], *[values[d] for d in dimensions], notes])
    return pd.DataFrame(rows, columns=["object_id", "object_type", "object_name", *dimensions, "notes"])


def render_map36(nodes: pd.DataFrame, rel: pd.DataFrame, counties: gpd.GeoDataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    fig = plt.figure(figsize=(16, 10), facecolor="#f2eadb")
    ax = fig.add_axes([0.04, 0.10, 0.62, 0.82], facecolor="#e8e0cf")
    counties.boundary.plot(ax=ax, color="#897d68", linewidth=0.55)
    counties.plot(ax=ax, color="#e8d7b1", alpha=0.35, edgecolor="none")
    zones = nodes[nodes.node_type == "population_zone"]
    ax.scatter(zones.longitude, zones.latitude, s=45, c="#7d2f3d", alpha=0.9, label="population zone")
    emp = nodes[nodes.node_type == "employment_center"]
    ax.scatter(emp.longitude, emp.latitude, s=100, marker="s", c="#2d6d75", alpha=0.9, label="employment concentration")
    for _, row in rel.sort_values("value", ascending=False).head(12).iterrows():
        source = nodes[nodes.node_id == row.source_node_id].iloc[0]; target = nodes[nodes.node_id == row.target_node_id].iloc[0]
        if source.node_id == target.node_id: continue
        width = max(0.4, min(3.0, math.log1p(float(row.value)) / 2.5))
        ax.add_patch(FancyArrowPatch((source.longitude, source.latitude), (target.longitude, target.latitude), arrowstyle="-|>", mutation_scale=9, linewidth=width, color="#b26d32", alpha=0.55, connectionstyle="arc3,rad=0.10"))
    ax.set_xlim(-86.0, -82.2); ax.set_ylim(40.1, 42.6); ax.set_axis_off()
    side = fig.add_axes([0.70, 0.08, 0.27, 0.84]); side.axis("off")
    side.text(0.02, 0.98, "MAP 36 — POPULATION, MOBILITY\n& SYSTEM DEPENDENCIES, 2026", va="top", fontsize=13, weight="bold", color="#17384b", linespacing=1.18)
    side.text(0.02, 0.82, "Aggregated LODES residence/workplace interfaces and accepted-system dependency context. Arrows are generalized county-to-county commuting relationships, not individual travel paths, passenger movement, or freight routes.", va="top", fontsize=8.3, color="#3f4645", linespacing=1.3)
    side.text(0.02, 0.59, "INTERFACES", fontsize=9.5, weight="bold", color="#17384b")
    side.text(0.04, 0.55, "• water / wastewater service dependence\n• energy and heating dependence\n• transport and employment mobility\n• climate-hazard physical interface\n• environmental-health pathway context\n• ecology/land and nutrient/material interfaces\n• housing and governance context", va="top", fontsize=7.9, color="#3f4645", linespacing=1.35)
    side.text(0.02, 0.28, "BOUNDARIES", fontsize=9.5, weight="bold", color="#17384b")
    side.text(0.04, 0.24, "Worker ≠ job ≠ commuter flow ≠ population. Commuting ≠ migration. Municipal boundary ≠ utility territory. Dependence ≠ vulnerability. Hazard interface ≠ exposure, dose, or illness. No composite score, protected-class ranking, or individual movement model.", va="top", fontsize=7.7, color="#3f4645", linespacing=1.3)
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor="#7d2f3d", markersize=7, label="population zone"), Line2D([0], [0], marker="s", color="w", markerfacecolor="#2d6d75", markersize=7, label="employment concentration"), Line2D([0], [0], color="#b26d32", lw=2, label="generalized commuting interface")], loc="lower left", frameon=True, facecolor="#f2eadb", fontsize=7.5)
    base = MAPS / "36_population_mobility_dependencies_2026"
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    normalize_svg(base.with_suffix(".svg"))


def build_11b_reports(nodes: pd.DataFrame, obs: pd.DataFrame, mobility: pd.DataFrame, relationships: pd.DataFrame, deps: pd.DataFrame, matrix: pd.DataFrame) -> None:
    top_flows = relationships.sort_values("value", ascending=False).head(12)
    source_text = """# Phase 11B Population, Mobility & System Dependency Sources

LODES 8.4 WAC, RAC, OD, and crosswalk products provide workplace, residence, and origin-destination job tabulations. Ohio and Indiana use 2023 WAC/RAC/OD files; Michigan uses 2021 WAC/OD and 2023 RAC because those are the current public files available for the respective products.[10][11][12][13][14][15][16][17][18][19][20][21] The data are aggregated here to county interfaces; they do not expose individual workers, employers, or travel paths.[10]

ACS 2024 5-year B08301/B08303 estimates provide residence-based commuting mode and travel-time context.[9] The records are not residential relocation, migration, passenger surveillance, or freight flow.

Water/wastewater, energy, transport governance, climate, environmental-health, ecology, nutrient, and service-responsibility interfaces reuse accepted Phase 6–10 layers and remain qualified at their original evidence level.

""" + source_block()
    assumptions = f"""# Phase 11B Population, Mobility & System Dependency Assumptions

LODES products are modeled/tabulated administrative products. WAC is workplace jobs, RAC is residence-based workers, and OD is an aggregated origin-destination job interface. Ohio and Indiana WAC/RAC/OD use 2023 products; Michigan WAC/OD use 2021 products and RAC uses 2023. None is treated as a person count, household count, migration flow, passenger count, freight flow, or individual trajectory. Michigan workplace/residence differences are not calculated when the WAC and RAC vintages differ. The 25-job cutoff is applied only to non-self same-state OD rows; cross-state OD rows are not synthesized from state files.

ACS 2024 5-year journey-to-work indicators are survey estimates for the 2020–2024 period. They describe residence-based commuting context and are not migration, relocation, or exact daily travel paths.

The dependency register contains {len(deps)} qualitative object/system interfaces and the matrix contains {len(matrix)} rows. Transport rows use the object's state-matched LODES OD source and remain inferred generalized interfaces. Water and wastewater rows use Toledo/Ohio sources only where their scopes match; other rows use the accepted regional service-responsibility context and do not claim state-specific operators, permits, territories, or loads. The matrix is derived from the dependency-register evidence-strength values and carries its source IDs in the row notes. No composite score is calculated. UNKNOWN is not LOW; dependence is not vulnerability; hazard interface is not exposure, dose, or health outcome.

Population presence does not assign every resident to a named drinking-water, wastewater, electricity, heating, or transit service territory. Municipal boundary, operator, service territory, population served, and estimated service population remain distinct.

Great Black Swamp remains C — HOLD / noncanonical. The Toledo intake-coordinate discrepancy remains unresolved. No Phase 11C or future demographic forecast is implemented.
"""
    findings = f"""# Phase 11B Population, Mobility & System Dependency Findings, 2026

## Residence/workplace relationships

FACT: The package contains {len(mobility)} mobility observations and {len(relationships)} generalized commuting relationships. The largest supported cross-county interfaces are:
""" + "\n".join(f"- {r.origin_geography} residence to {r.destination_geography} workplace: {int(r.value):,} LODES jobs ({r.reference_year} workplace-product year).[10][11][12][13][14][15][16][17][18][19][20][21]" for r in top_flows.itertuples()) + f"""

INFERENCE: Toledo/Lucas County functions as a major residence/workplace interface in the regional settlement system, while other county-seat, industrial, logistics, and service centers create additional cross-county relationships. The package does not infer why people commute or whether any commuter relocated.

## Commuting

FACT: ACS county records distinguish drive-alone, carpool, public transportation, walking, work-from-home, and long-commute shares. These are residence-based survey estimates for the 2020–2024 period.[9]

INFERENCE: The regional settlement pattern is materially dependent on road-based daily mobility, but this is a generalized commuting/system interface finding, not an individual travel model or a measure of community worth.

## Water and wastewater

FACT/INFERENCE: Population concentration creates functional dependence on drinking-water and wastewater systems. The accepted Toledo operator and Ohio regulatory context support a bounded interface; they do not establish that every Census resident is served by one named system, nor do they create exact service territories or wastewater loads.[22][23]

## Energy

FACT/INFERENCE: Settlement and employment concentrations have functional electricity/heating dependence. Accepted PJM and private-utility context supports the system interface, but no local distribution assignment, demand forecast, outage probability, or feeder topology is created.[24][25]

## Transport and employment

FACT: LODES residence/workplace tabulations show jobs and workers at different geographies and generalized cross-county interfaces. Workplace concentration is not residential concentration; the two are retained as separate metrics.[10][11][12][13][14][15][16][17][18][19][20][21]

## Climate and environmental health

INFERENCE: Settlement nodes can be spatially interfaced with accepted physical hazard and environmental-health pathway layers. These interfaces do not establish personal exposure, dose, illness, mortality, or vulnerability.[26][27]

## Ecology, nutrient/material, housing, and governance

INFERENCE: Settlement, stormwater/wastewater, land-cover, nutrient/material, housing, and governance interfaces are represented qualitatively. The accepted ecology and biogeochemical layers are not rebuilt; no new flux, ecological condition, utility service population, or governance-quality score is inferred.[28][29][30]

## Major limitations

UNCERTAINTY: LODES has nonsampling and modelling limitations; ACS has sampling and estimate-period limitations; Census/PEP/ACS vintages are not a single 2026 surface; county OD aggregation obscures within-county and route-level structure; exact utility service territories and population served are not publicly established in this package; seasonal/institutional/ambient population and transit ridership are not modeled.

""" + source_block()
    qa = f"""# Phase 11B Population, Mobility & System Dependency QA

Python validation checks {len(mobility)} mobility observations, {len(relationships)} commuting relationships, {len(deps)} dependency rows, {len(matrix)} matrix rows, LODES/ACS vintages, worker/job/commuter/population distinctions, residence/workplace direction, county-pair scale, no individual inference, no utility-territory assignment, qualitative enum values, no vulnerability/protected-class constructs, Map 36 integrity, the Phase 11A baseline manifest, prior Phase 1–10 freeze integrity, active holds, and Phase 11C absence.

The independent R validator recomputes the same counts and semantic boundaries without importing the Python validator. It also checks Map 35/36 artifacts, working hashes, source IDs, Markdown outputs, and negative-scope text.

NO composite vulnerability score, EJ score, protected-class ranking, disease/dose/health outcome, individual movement model, unsupported forecast, Phase 11C artifact, or Phase 12 artifact is included.
"""
    (REPORTS / "population_mobility_sources.md").write_text(source_text, encoding="utf-8")
    (REPORTS / "population_mobility_assumptions.md").write_text(assumptions, encoding="utf-8")
    (REPORTS / "population_mobility_findings.md").write_text(findings, encoding="utf-8")
    (REPORTS / "population_mobility_qa.md").write_text(qa, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["11a", "11b", "all"], default="all")
    args = parser.parse_args()
    for directory in (CACHE, ANALYSIS, NETWORKS, MAPS, REPORTS):
        directory.mkdir(parents=True, exist_ok=True)
    package = build_11a()
    if args.phase in {"11b", "all"}:
        result = build_11b(package)
        print(json.dumps({"phase": "11A/11B", "nodes": len(package["nodes"]), "population_observations": len(package["observations"]), "relationships": len(pd.read_csv(NETWORKS / "population_settlement_relationships.csv")), "mobility_observations": len(result["mobility"]), "mobility_relationships": len(result["mobility_rel"]), "dependencies": len(result["deps"]), "matrix_rows": len(result["matrix"]), "maps": [35, 36]}, indent=2))
    else:
        print(json.dumps({"phase": "11A", "nodes": len(package["nodes"]), "population_observations": len(package["observations"]), "relationships": len(package["relationships"]), "sources": len(package["sources"]), "map": 35}, indent=2))


if __name__ == "__main__":
    main()
