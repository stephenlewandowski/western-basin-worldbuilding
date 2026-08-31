"""Build Phase 2B shared material-flow tables and Maps 07-08.

The maps distinguish spatial observations from schematic supply-chain links.
No line represents an undocumented transportation route or shipment quantity.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch
import pandas as pd
import pyogrio
from shapely.geometry import Point


ROOT = Path(__file__).resolve().parents[3]
GPKG = ROOT / "data" / "processed" / "glasspunk_base.gpkg"
NETWORKS = ROOT / "data" / "processed" / "networks"
MAPS = ROOT / "outputs" / "maps" / "systems"
REPORTS = ROOT / "reports"
NODES_CSV = NETWORKS / "materials_system_nodes.csv"
EDGES_CSV = NETWORKS / "materials_system_edges.csv"
SOURCES_CSV = NETWORKS / "materials_system_sources.csv"
MANIFEST = REPORTS / "materials_phase2b_manifest.json"
MAP07 = MAPS / "07_carbonate_materials_system"
MAP08 = MAPS / "08_beryllium_strategic_supply_chain"
RETRIEVED = "2026-08-31"
MAP_CRS = "EPSG:5070"
FOCUS = (-83.95, 41.12, -82.72, 41.82)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "svg.fonttype": "none",
    "axes.titleweight": "bold",
    "path.simplify": True,
    "path.simplify_threshold": 0.15,
})


SOURCES = [
    {
        "source_id": "SRC-ODNR-BEDROCK-2006",
        "title": "Bedrock Type",
        "agency_or_publisher": "Ohio Department of Natural Resources",
        "url_or_identifier": "https://gis2.ohiodnr.gov/arcgis/rest/services/DNR_Services/SUBSURFACE/MapServer/5",
        "retrieved_date": "2026-08-29",
        "publication_or_dataset_date": "2006 compilation; source quadrangles largely 1989-1998",
        "spatial_resolution_or_scale": "1:500,000 statewide compilation",
        "license_or_terms": "Public Ohio DNR map service; retain source credit",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Regional occurrence context only; not reserves, quarry boundaries, or parcel-scale geology.",
    },
    {
        "source_id": "SRC-ODNR-MINERALS-2021",
        "title": "2021 Report on Ohio Mineral Industries",
        "agency_or_publisher": "Ohio Department of Natural Resources",
        "url_or_identifier": "https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/geology/industrial-minerals-downloads/IM1_2021_Wright_2022.pdf",
        "retrieved_date": "2026-08-29",
        "publication_or_dataset_date": "2021 data; published 2022",
        "spatial_resolution_or_scale": "Mapped operations; statewide",
        "license_or_terms": "Public state report",
        "confidence": "medium_high",
        "source_type": "government_verified",
        "notes": "Corroborates Woodville quarry operations; not treated as a complete 2026 inventory.",
    },
    {
        "source_id": "SRC-MM-WOODVILLE-2025",
        "title": "2025 Sustainability Report and Woodville Lime Facility",
        "agency_or_publisher": "Martin Marietta",
        "url_or_identifier": "https://mcdn.martinmarietta.com/assets/sustainability/2025sustainabilityreport.pdf",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "2025",
        "spatial_resolution_or_scale": "Facility-level company narrative",
        "license_or_terms": "Public company publication",
        "confidence": "high",
        "source_type": "company_statement",
        "notes": "Woodville processes dolomitic limestone in six lime kilns; company describes water/wastewater and environmental applications broadly, not a Toledo supply contract.",
    },
    {
        "source_id": "SRC-OHEPA-AREA-2022",
        "title": "NPDES Permit 2IJ00028",
        "agency_or_publisher": "Ohio Environmental Protection Agency",
        "url_or_identifier": "https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/35/permits/doc/2IJ00028.pdf",
        "retrieved_date": "2026-08-29",
        "publication_or_dataset_date": "Effective 2022-01-01 through 2026-12-31",
        "spatial_resolution_or_scale": "Official facility address",
        "license_or_terms": "Public state permit",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Verifies the Area Aggregates Woodville facility during the 2026 baseline.",
    },
    {
        "source_id": "SRC-KOKOSING-SPECIALTY-2026",
        "title": "Specialty Aggregate Products",
        "agency_or_publisher": "Kokosing / The Olen Corporation / Area Aggregates",
        "url_or_identifier": "https://www.kokosing.biz/our-work/materials/aggregate/specialty/",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "Current page, 2026",
        "spatial_resolution_or_scale": "Facility/product listing",
        "license_or_terms": "Public company webpage",
        "confidence": "high",
        "source_type": "company_statement",
        "notes": "Lists agricultural lime and filter sand at Woodville; does not establish a customer or transport route.",
    },
    {
        "source_id": "SRC-GRAYMONT-GENOA-2026",
        "title": "Genoa Plant and Graymont Solutions",
        "agency_or_publisher": "Graymont",
        "url_or_identifier": "https://www.graymont.com/solutions/",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "Current page, 2026; plant brochure retained by company",
        "spatial_resolution_or_scale": "Facility/product narrative",
        "license_or_terms": "Public company webpage",
        "confidence": "high",
        "source_type": "company_statement",
        "notes": "Documents Genoa manufacture of dolomitic hydrated/finish and masonry lime; no specific Toledo customer relationship is claimed.",
    },
    {
        "source_id": "SRC-EPA-CAO-2022",
        "title": "Calcium Oxide Supply Chain Profile",
        "agency_or_publisher": "U.S. Environmental Protection Agency",
        "url_or_identifier": "https://www.epa.gov/system/files/documents/2023-03/Calcium%20Oxide%20Supply%20Chain%20Profile.pdf",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "December 2022",
        "spatial_resolution_or_scale": "National functional supply-chain profile",
        "license_or_terms": "Public federal publication",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Documents limestone/dolomite to lime processing and water, metallurgy, construction, and remediation functions; not a local supplier contract.",
    },
    {
        "source_id": "SRC-USGS-BE-2026",
        "title": "Mineral Commodity Summaries 2026 - Beryllium",
        "agency_or_publisher": "U.S. Geological Survey",
        "url_or_identifier": "https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-beryllium.pdf",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "2026",
        "spatial_resolution_or_scale": "National commodity summary",
        "license_or_terms": "Public-domain U.S. Geological Survey publication",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Documents Utah bertrandite/imported beryl, intermediate beryllium hydroxide, Ohio conversion, and broad end-use sectors.",
    },
    {
        "source_id": "SRC-USGS-BE-FLOW-2018",
        "title": "Beryllium: Economic Geology, Material Flow, and Global Importance",
        "agency_or_publisher": "U.S. Geological Survey",
        "url_or_identifier": "https://www.usgs.gov/centers/geology-energy-and-minerals-science-center/science/beryllium-economic-geology-material-flow",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "2018",
        "spatial_resolution_or_scale": "National/global commodity context",
        "license_or_terms": "Public-domain U.S. Geological Survey webpage",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Supports the broad strategic roles of beryllium in computer, telecommunications, aerospace, medical, defense, and nuclear systems.",
    },
    {
        "source_id": "SRC-EPA-MATERION-ELMORE",
        "title": "Materion Elmore permit documentation",
        "agency_or_publisher": "U.S. Environmental Protection Agency",
        "url_or_identifier": "https://semspub.epa.gov/work/05/967810.pdf",
        "retrieved_date": "2026-08-29",
        "publication_or_dataset_date": "Public permit record",
        "spatial_resolution_or_scale": "Facility address and process narrative",
        "license_or_terms": "Public federal record",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Verifies Elmore as beryllium/alloy processing, not extraction.",
    },
    {
        "source_id": "SRC-MATERION-CFS-2025",
        "title": "Materion Supply Agreement with Commonwealth Fusion Systems",
        "agency_or_publisher": "Materion",
        "url_or_identifier": "https://www.materion.com/en/about-materion/news/performance-alloys/materion-supply-agreement-with-commonwealth-fusion",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "2025-10-31",
        "spatial_resolution_or_scale": "Named facility/company supply relationship",
        "license_or_terms": "Public company announcement",
        "confidence": "high",
        "source_type": "company_statement",
        "notes": "Announces Elmore beryllium-fluoride shipments for FLiBe used in CFS ARC plants; no shipment quantities or route modeled.",
    },
    {
        "source_id": "SRC-MATERION-KAIROS-2022",
        "title": "Materion and Kairos Power to Advance Clean Energy",
        "agency_or_publisher": "Materion",
        "url_or_identifier": "https://investor.materion.com/news/news-details/2022/Materion-and-Kairos-Power-to-Advance-Clean-Energy/default.aspx",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "2022-07-27",
        "spatial_resolution_or_scale": "Named Elmore facility/company collaboration",
        "license_or_terms": "Public company announcement",
        "confidence": "medium_high",
        "source_type": "company_statement",
        "notes": "Documents Elmore molten-salt purification and beryllium-fluoride input for Kairos FLiBe; current operating status was not independently reverified.",
    },
    {
        "source_id": "SRC-MATERION-ENDUSES-2024",
        "title": "Beryllium End-Use Performance Requirements",
        "agency_or_publisher": "Materion",
        "url_or_identifier": "https://www.materion.com/en/about-materion/news/beryllium-and-composites/beryllium-steps-up-to-meet-rigorous-end-use-performance-requirements",
        "retrieved_date": RETRIEVED,
        "publication_or_dataset_date": "Company archive dated 2024",
        "spatial_resolution_or_scale": "Product/end-use narrative",
        "license_or_terms": "Public company webpage",
        "confidence": "medium_high",
        "source_type": "company_statement",
        "notes": "Supports optics, aerospace, and defense end uses; broad sector links are not modeled as named Elmore customer contracts.",
    },
    {
        "source_id": "SRC-USACE-LUCKEY-2026",
        "title": "Luckey Site",
        "agency_or_publisher": "U.S. Army Corps of Engineers",
        "url_or_identifier": "https://www.lrd.usace.army.mil/Missions/Projects/Article/3613204/luckey-site/",
        "retrieved_date": "2026-08-29",
        "publication_or_dataset_date": "Updated 2026-07-16",
        "spatial_resolution_or_scale": "Named remediation site",
        "license_or_terms": "Public federal webpage",
        "confidence": "high",
        "source_type": "government_verified",
        "notes": "Establishes current FUSRAP cleanup and historical activity; Luckey is not current beryllium production.",
    },
]


def node(node_id: str, name: str, system: str, node_type: str, role: str,
         local_resource: str, region: str, source_id: str, confidence: str,
         notes: str, *, latitude: float | None = None,
         longitude: float | None = None, canon_status: str = "verified") -> dict:
    return {
        "node_id": node_id,
        "name": name,
        "material_system": system,
        "node_type": node_type,
        "supply_chain_role": role,
        "reality_status": "real",
        "canon_status": canon_status,
        "local_resource": local_resource,
        "scenario_year": 2026,
        "region": region,
        "latitude": latitude,
        "longitude": longitude,
        "source_id": source_id,
        "confidence": confidence,
        "notes": notes,
    }


NODES = [
    node("CARB-GEO-REGIONAL", "Regional carbonate bedrock", "carbonate", "geologic_unit", "geologic_occurrence", "true", "Western Basin", "SRC-ODNR-BEDROCK-2006", "high", "Generalized 1:500,000 occurrence context; not reserves or parcel geology."),
    node("CARB-EXT-AREA-WOODVILLE", "Area Aggregates Woodville extraction", "carbonate", "facility", "extraction", "true", "Black Swamp Country", "SRC-OHEPA-AREA-2022", "medium", "Current permit and company product evidence; street-address point, not quarry boundary.", latitude=41.440421365979, longitude=-83.357258672099),
    node("CARB-EXT-MM-WOODVILLE", "Martin Marietta Woodville quarry", "carbonate", "facility", "extraction", "true", "Black Swamp Country", "SRC-ODNR-MINERALS-2021", "medium_high", "Quarry context documented by ODNR; represented at the co-located facility address, not an operational boundary.", latitude=41.465048865166, longitude=-83.366181833374),
    node("CARB-PROC-MM-WOODVILLE", "Martin Marietta Woodville lime processing", "carbonate", "facility", "primary_processing", "true", "Black Swamp Country", "SRC-MM-WOODVILLE-2025", "high", "Processes dolomitic limestone in lime kilns; no customer-level route modeled.", latitude=41.465048865166, longitude=-83.366181833374),
    node("CARB-PROC-GRAYMONT-GENOA", "Graymont Genoa lime processing", "carbonate", "facility", "primary_processing", "true", "Black Swamp Country", "SRC-GRAYMONT-GENOA-2026", "high", "Produces dolomitic hydrated/finish and masonry lime; exact source quarry unresolved.", latitude=41.515270001961, longitude=-83.355189973188),
    node("CARB-MAT-LIME", "Lime and dolime products", "carbonate", "material_product", "primary_processing", "not_applicable", "System interface", "SRC-EPA-CAO-2022", "high", "Functional product node; not a facility or stock estimate."),
    node("CARB-MAT-AGGREGATE", "Limestone and aggregate products", "carbonate", "material_product", "primary_processing", "not_applicable", "System interface", "SRC-KOKOSING-SPECIALTY-2026", "high", "Product-class node without shipment volume or route."),
    node("CARB-END-WATER", "Drinking-water and wastewater treatment", "carbonate", "end_use_function", "end_use_sector", "not_applicable", "Water System interface", "SRC-EPA-CAO-2022", "high", "General engineering dependency; no claim that a named local facility supplies Toledo."),
    node("CARB-END-AGRICULTURE", "Agriculture and soil amendment", "carbonate", "end_use_function", "end_use_sector", "not_applicable", "Black Swamp Country interface", "SRC-KOKOSING-SPECIALTY-2026", "high", "Woodville agricultural-lime product function."),
    node("CARB-END-CONSTRUCTION", "Construction and infrastructure", "carbonate", "end_use_function", "end_use_sector", "not_applicable", "Industrial interface", "SRC-EPA-CAO-2022", "high", "Broad lime/aggregate function; not a named customer relationship."),
    node("CARB-END-METALLURGY", "Steel and metallurgical processing", "carbonate", "end_use_function", "end_use_sector", "not_applicable", "Industrial interface", "SRC-EPA-CAO-2022", "high", "Broad lime function; not a named local customer relationship."),
    node("CARB-END-ENVIRONMENT", "Environmental treatment", "carbonate", "end_use_function", "end_use_sector", "not_applicable", "Environmental interface", "SRC-EPA-CAO-2022", "high", "Broad remediation/pollution-treatment function."),
    node("SYS-IF-ENERGY", "Industrial energy demand", "shared", "system_interface", "end_use_sector", "not_applicable", "Future Energy System interface", "SRC-MM-WOODVILLE-2025", "high", "Coarse dependency only; no detailed energy model in Phase 2B."),
    node("SYS-IF-FREIGHT", "Freight and logistics dependency", "shared", "system_interface", "logistics_interface", "not_applicable", "Future Freight System interface", "SRC-EPA-CAO-2022", "medium_high", "Coarse dependency only; no route, mode, schedule, or quantity asserted."),
    node("BER-UP-DOMESTIC", "External domestic beryllium resource", "beryllium", "external_resource", "extraction", "false", "External - Utah", "SRC-USGS-BE-2026", "high", "Broad Spor Mountain/Utah domestic source representation; intentionally no mapped mine-to-Elmore route."),
    node("BER-UP-IMPORT", "Imported beryl supply", "beryllium", "external_resource", "extraction", "false", "External - global", "SRC-USGS-BE-2026", "high", "Broad imported source representation; no country, depot, mode, route, or quantity inferred."),
    node("BER-UP-HYDROXIDE", "External beryllium hydroxide intermediate", "beryllium", "intermediate_material", "primary_processing", "false", "External supply system", "SRC-USGS-BE-2026", "high", "USGS-described intermediate shipped in part to an Ohio plant."),
    node("BER-PROC-ELMORE", "Materion Elmore advanced processing", "beryllium", "facility", "advanced_processing", "false", "Black Swamp Country", "SRC-EPA-MATERION-ELMORE", "high", "Strategic processing is true; local extraction is false. Elmore is not a beryllium mine.", latitude=41.491149985926, longitude=-83.215860027455),
    node("BER-MAT-ADVANCED", "Advanced beryllium materials", "beryllium", "material_product", "advanced_processing", "not_applicable", "National/global supply system", "SRC-USGS-BE-2026", "high", "Metal, oxide, beryllium-copper master alloy, and specialized downstream materials; no quantity modeled."),
    node("BER-END-AERO-DEF", "Aerospace and defense systems", "beryllium", "end_use_sector", "end_use_sector", "not_applicable", "External strategic sector", "SRC-USGS-BE-2026", "high", "Broad sourced sector, not a classified or customer-specific Elmore relationship.", canon_status="inferred"),
    node("BER-END-ELEC-TELECOM", "Electronics and telecommunications", "beryllium", "end_use_sector", "end_use_sector", "not_applicable", "External strategic sector", "SRC-USGS-BE-FLOW-2018", "high", "Broad sourced sector, not a named Elmore customer relationship.", canon_status="inferred"),
    node("BER-END-OPTICS", "Precision instruments and optics", "beryllium", "end_use_sector", "end_use_sector", "not_applicable", "External strategic sector", "SRC-MATERION-ENDUSES-2024", "medium_high", "Broad company-supported product market; not a named Elmore customer relationship.", canon_status="inferred"),
    node("BER-END-CFS", "Commonwealth Fusion Systems ARC", "beryllium", "named_end_use", "end_use_sector", "not_applicable", "External fusion system", "SRC-MATERION-CFS-2025", "high", "Named 2025 beryllium-fluoride/FLiBe supply agreement; no fictional Northwest Ohio reactor."),
    node("BER-END-KAIROS", "Kairos Power FLiBe system", "beryllium", "named_end_use", "end_use_sector", "not_applicable", "External advanced nuclear system", "SRC-MATERION-KAIROS-2022", "medium_high", "Named Elmore collaboration announced/commissioned in 2022; current operating status not independently reverified."),
    node("BER-LEG-LUCKEY", "Luckey FUSRAP remediation", "beryllium", "legacy_site", "legacy_cleanup", "false", "Black Swamp Country", "SRC-USACE-LUCKEY-2026", "high", "Historical/legacy context only; not current beryllium production.", latitude=41.458801748910, longitude=-83.490434663133),
]


def edge(edge_id: str, from_id: str, to_id: str, material: str, flow_type: str,
         basis: str, confidence: str, source_id: str, notes: str,
         *, relationship_date: str = "not_applicable",
         current_status: str = "current_2026_baseline") -> dict:
    return {
        "edge_id": edge_id,
        "from_id": from_id,
        "to_id": to_id,
        "material": material,
        "flow_type": flow_type,
        "relationship_basis": basis,
        "reality_status": "real",
        "canon_status": "inferred" if basis in {"scientific_inference", "supply_chain_inference"} else "verified",
        "confidence": confidence,
        "source_id": source_id,
        "relationship_date": relationship_date,
        "current_status": current_status,
        "notes": notes,
    }


EDGES = [
    edge("CARB-E01", "CARB-GEO-REGIONAL", "CARB-EXT-AREA-WOODVILLE", "limestone", "resource_to_extraction", "scientific_inference", "medium", "SRC-ODNR-BEDROCK-2006", "Facility lies in the regional carbonate landscape; this does not delineate its worked geologic unit."),
    edge("CARB-E02", "CARB-GEO-REGIONAL", "CARB-EXT-MM-WOODVILLE", "dolomitic limestone", "resource_to_extraction", "scientific_inference", "medium_high", "SRC-ODNR-MINERALS-2021", "ODNR corroborates the quarry; generalized geology is not a quarry boundary."),
    edge("CARB-E03", "CARB-EXT-MM-WOODVILLE", "CARB-PROC-MM-WOODVILLE", "dolomitic limestone", "extraction_to_processing", "supply_chain_inference", "medium", "SRC-MM-WOODVILLE-2025", "Co-location and dolomitic feed are documented, but an explicit internal feed statement was not located."),
    edge("CARB-E04", "CARB-EXT-AREA-WOODVILLE", "CARB-MAT-AGGREGATE", "limestone / aggregate", "facility_to_product", "documented_supply_relationship", "high", "SRC-KOKOSING-SPECIALTY-2026", "Official company page lists Woodville specialty aggregate products."),
    edge("CARB-E05", "CARB-EXT-AREA-WOODVILLE", "CARB-END-AGRICULTURE", "agricultural lime", "facility_to_end_use", "documented_supply_relationship", "high", "SRC-KOKOSING-SPECIALTY-2026", "Official company page lists agricultural lime at Woodville; no customer or route asserted."),
    edge("CARB-E06", "CARB-PROC-MM-WOODVILLE", "CARB-MAT-LIME", "lime / magnesia products", "facility_to_product", "observed", "high", "SRC-MM-WOODVILLE-2025", "Company documentation identifies dolomitic limestone processing and lime kilns at Woodville."),
    edge("CARB-E07", "CARB-GEO-REGIONAL", "CARB-PROC-GRAYMONT-GENOA", "dolomitic limestone", "resource_to_processing", "supply_chain_inference", "medium", "SRC-GRAYMONT-GENOA-2026", "Genoa uses dolomitic limestone, but the specific quarry/feed relationship is unresolved."),
    edge("CARB-E08", "CARB-PROC-GRAYMONT-GENOA", "CARB-MAT-LIME", "dolomitic hydrated lime", "facility_to_product", "observed", "high", "SRC-GRAYMONT-GENOA-2026", "Official Graymont product/facility materials support Genoa lime production."),
    edge("CARB-E09", "CARB-MAT-LIME", "CARB-END-WATER", "quicklime / hydrated lime", "functional_dependency", "engineering_dependency", "high", "SRC-EPA-CAO-2022", "General water-sector dependency; no named local facility-to-Toledo contract is claimed."),
    edge("CARB-E10", "CARB-MAT-LIME", "CARB-END-METALLURGY", "lime", "functional_dependency", "engineering_dependency", "high", "SRC-EPA-CAO-2022", "Nationally documented metallurgical function; no named local customer relationship."),
    edge("CARB-E11", "CARB-MAT-LIME", "CARB-END-CONSTRUCTION", "lime", "functional_dependency", "engineering_dependency", "high", "SRC-EPA-CAO-2022", "Documented construction function; no shipment route or customer asserted."),
    edge("CARB-E12", "CARB-MAT-AGGREGATE", "CARB-END-CONSTRUCTION", "aggregate", "functional_dependency", "engineering_dependency", "high", "SRC-KOKOSING-SPECIALTY-2026", "Product-class to sector function, not a project-specific delivery."),
    edge("CARB-E13", "CARB-MAT-LIME", "CARB-END-ENVIRONMENT", "lime", "functional_dependency", "engineering_dependency", "high", "SRC-EPA-CAO-2022", "EPA documents environmental-treatment applications."),
    edge("CARB-E14", "CARB-PROC-MM-WOODVILLE", "SYS-IF-ENERGY", "process energy", "system_interface", "engineering_dependency", "high", "SRC-MM-WOODVILLE-2025", "Calcination is energy-intensive; detailed energy sourcing is outside Phase 2B."),
    edge("CARB-E15", "CARB-MAT-LIME", "SYS-IF-FREIGHT", "lime products", "system_interface", "engineering_dependency", "medium_high", "SRC-EPA-CAO-2022", "Distribution dependency only; no mode, route, schedule, or quantity assigned."),
    edge("BER-E01", "BER-UP-DOMESTIC", "BER-UP-HYDROXIDE", "beryllium hydroxide intermediate", "resource_to_intermediate", "observed", "high", "SRC-USGS-BE-2026", "USGS documents Utah bertrandite conversion; map remains schematic."),
    edge("BER-E02", "BER-UP-IMPORT", "BER-UP-HYDROXIDE", "beryllium hydroxide intermediate", "resource_to_intermediate", "observed", "high", "SRC-USGS-BE-2026", "USGS documents imported beryl conversion; no country or route inferred."),
    edge("BER-E03", "BER-UP-HYDROXIDE", "BER-PROC-ELMORE", "beryllium hydroxide", "intermediate_to_processing", "observed", "high", "SRC-USGS-BE-2026", "USGS documents that some intermediate material is shipped to an Ohio plant; no route, mode, or quantity modeled."),
    edge("BER-E04", "BER-PROC-ELMORE", "BER-MAT-ADVANCED", "beryllium metal / oxide / copper-beryllium", "processing_to_product", "observed", "high", "SRC-USGS-BE-2026", "USGS supports Ohio conversion to these broad material forms."),
    edge("BER-E05", "BER-MAT-ADVANCED", "BER-END-AERO-DEF", "advanced beryllium materials", "product_to_sector", "supply_chain_inference", "high", "SRC-USGS-BE-2026", "Broad sector use is sourced; a specific Elmore customer is not asserted."),
    edge("BER-E06", "BER-MAT-ADVANCED", "BER-END-ELEC-TELECOM", "beryllium alloys / components", "product_to_sector", "supply_chain_inference", "medium_high", "SRC-USGS-BE-FLOW-2018", "Broad sector use is sourced; a specific Elmore customer is not asserted."),
    edge("BER-E07", "BER-MAT-ADVANCED", "BER-END-OPTICS", "beryllium / aluminum-beryllium", "product_to_sector", "supply_chain_inference", "medium_high", "SRC-MATERION-ENDUSES-2024", "Company-supported market use; not a named Elmore customer contract."),
    edge("BER-E08", "BER-PROC-ELMORE", "BER-END-CFS", "beryllium fluoride for FLiBe", "named_supply", "documented_supply_relationship", "high", "SRC-MATERION-CFS-2025", "Materion announced Elmore shipments for CFS ARC FLiBe; no quantity or transport route modeled.", relationship_date="2025-10-31", current_status="announced_current_relationship; shipments stated to begin in 2025"),
    edge("BER-E09", "BER-PROC-ELMORE", "BER-END-KAIROS", "beryllium fluoride / FLiBe", "named_supply", "documented_supply_relationship", "medium_high", "SRC-MATERION-KAIROS-2022", "Materion announced an Elmore FLiBe collaboration and commissioned purification plant; current status not independently reverified.", relationship_date="2022-07-27", current_status="documented_2022_collaboration; 2026 operating status unresolved"),
    edge("BER-E10", "BER-PROC-ELMORE", "SYS-IF-ENERGY", "process energy", "system_interface", "engineering_dependency", "medium_high", "SRC-EPA-MATERION-ELMORE", "Advanced processing depends on energy; no detailed load or supplier modeled."),
    edge("BER-E11", "BER-MAT-ADVANCED", "SYS-IF-FREIGHT", "advanced materials", "system_interface", "engineering_dependency", "medium", "SRC-USGS-BE-2026", "External supply/end use implies logistics, but no mode, route, schedule, or quantity is assigned."),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_context():
    carbonate = pyogrio.read_dataframe(GPKG, layer="geology_carbonate_units")
    hydro = pyogrio.read_dataframe(
        GPKG,
        layer="hydrography_physical",
        bbox=FOCUS,
        columns=["featuretypelabel", "streamorder", "gnisidlabel"],
    )
    streamorder = pd.to_numeric(hydro["streamorder"], errors="coerce")
    hydro = hydro[(streamorder >= 3) | hydro["gnisidlabel"].notna()].copy()
    hydro["geometry"] = hydro.geometry.simplify(0.00015, preserve_topology=True)
    lake = pyogrio.read_dataframe(GPKG, layer="water_lake_erie")
    roads = gpd.read_file(ROOT / "data" / "raw" / "census" / "tigerweb_primary_roads.geojson")
    places = gpd.read_file(ROOT / "data" / "raw" / "census" / "tigerweb_incorporated_places.geojson")
    return tuple(frame.to_crs(MAP_CRS) for frame in [carbonate, hydro, lake, roads, places])


def add_north_scale(ax, x0: float, y0: float, width: float = 50_000) -> None:
    ax.annotate("N", xy=(0.95, 0.94), xytext=(0.95, 0.84), xycoords="axes fraction",
                ha="center", va="center", fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", lw=1.3, color="#1f2933"))
    ax.plot([x0, x0 + width], [y0, y0], color="#1f2933", lw=3, solid_capstyle="butt")
    ax.plot([x0, x0], [y0 - 1200, y0 + 1200], color="#1f2933", lw=1)
    ax.plot([x0 + width, x0 + width], [y0 - 1200, y0 + 1200], color="#1f2933", lw=1)
    ax.text(x0 + width / 2, y0 + 3000, f"{int(width/1000)} km", ha="center", fontsize=8)


def project_points(ids: list[str], nodes: pd.DataFrame) -> gpd.GeoDataFrame:
    frame = nodes[nodes.node_id.isin(ids)].copy()
    return gpd.GeoDataFrame(
        frame,
        geometry=[Point(x, y) for x, y in zip(frame.longitude, frame.latitude)],
        crs="EPSG:4326",
    ).to_crs(MAP_CRS)


def box_label(ax, xy, text, *, fc="#ffffff", ec="#334e68", size=9, width=0.23, height=0.085):
    x, y = xy
    patch = FancyBboxPatch((x - width/2, y - height/2), width, height,
                           boxstyle="round,pad=0.012", fc=fc, ec=ec, lw=1.2,
                           transform=ax.transAxes, clip_on=False)
    ax.add_patch(patch)
    ax.text(x, y, text, transform=ax.transAxes, ha="center", va="center",
            fontsize=size, color="#102a43", wrap=True)


def arrow_axes(ax, start, end, *, solid=True, color="#526d82", lw=1.8):
    ax.annotate("", xy=end, xytext=start, xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color,
                                linestyle="-" if solid else "--", mutation_scale=12))


def map07(nodes: pd.DataFrame) -> None:
    carbonate, hydro, lake, roads, places = load_context()
    fig = plt.figure(figsize=(16, 10), facecolor="#f7f4ec")
    grid = fig.add_gridspec(1, 2, width_ratios=[2.05, 0.95], wspace=0.025)
    ax = fig.add_subplot(grid[0, 0])
    panel = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#edf3ef")
    carbonate.plot(ax=ax, color="#d9c57b", edgecolor="#9c7d2e", linewidth=0.35, alpha=0.50, hatch="..")
    lake.plot(ax=ax, color="#d7edf5", edgecolor="#6d9fb5", linewidth=0.7, alpha=0.9)
    hydro.plot(ax=ax, color="#3b82a0", linewidth=0.45, alpha=0.65)
    roads.plot(ax=ax, color="#8795a1", linewidth=0.55, alpha=0.55)

    site_ids = ["CARB-EXT-AREA-WOODVILLE", "CARB-EXT-MM-WOODVILLE", "CARB-PROC-MM-WOODVILLE", "CARB-PROC-GRAYMONT-GENOA"]
    sites = project_points(site_ids, nodes)
    extraction = sites[sites.supply_chain_role == "extraction"]
    processing = sites[sites.supply_chain_role == "primary_processing"]
    extraction.plot(ax=ax, marker="^", color="#d97706", edgecolor="#7c2d12", markersize=120, zorder=7)
    processing.plot(ax=ax, marker="s", color="#1d4ed8", edgecolor="white", linewidth=1.2, markersize=75, zorder=8)
    for row in sites.drop_duplicates("longitude").itertuples():
        label = "Woodville\nquarry + lime processing" if "Woodville" in row.name else "Graymont Genoa\nlime processing"
        if "Area" in row.name:
            label = "Area Aggregates\nWoodville extraction"
        ax.annotate(label, (row.geometry.x, row.geometry.y), xytext=(7, 8), textcoords="offset points",
                    fontsize=8.4, color="#243b53", weight="bold",
                    bbox=dict(boxstyle="round,pad=0.25", fc="#fffdf7", ec="#9fb3c8", alpha=0.92))

    wanted = {"Toledo", "Woodville", "Genoa", "Elmore", "Luckey", "Perrysburg", "Fremont"}
    place_points = places.copy()
    place_points["geometry"] = place_points.geometry.representative_point()
    for row in place_points[place_points.BASENAME.isin(wanted)].itertuples():
        ax.plot(row.geometry.x, row.geometry.y, "o", ms=2.5, color="#52606d", zorder=5)
        ax.annotate(row.BASENAME, (row.geometry.x, row.geometry.y), xytext=(3, -6), textcoords="offset points", fontsize=7.5, color="#52606d")

    bounds = gpd.GeoSeries([Point(FOCUS[0], FOCUS[1]), Point(FOCUS[2], FOCUS[3])], crs=4326).to_crs(MAP_CRS)
    minx, miny = bounds.iloc[0].x, bounds.iloc[0].y
    maxx, maxy = bounds.iloc[1].x, bounds.iloc[1].y
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("MAP 07 — CARBONATE MATERIALS SYSTEM", loc="left", fontsize=18, color="#17324d", pad=12)
    ax.text(0.01, 0.98, "2026 regional baseline · Northwest Ohio", transform=ax.transAxes, va="top", fontsize=10, color="#486581")
    ax.text(0.01, 0.91, "ODNR geology: generalized 1:500,000 occurrence context — not quarry or parcel precision\nAccepted 3DHP physical hydrography shown; network connectors and inferred routing omitted",
            transform=ax.transAxes, fontsize=8.1, color="#334e68",
            bbox=dict(boxstyle="round,pad=0.35", fc="#fffdf7", ec="#bcccdc", alpha=0.94))
    add_north_scale(ax, minx + 7000, miny + 7500, 50_000)
    ax.legend(handles=[
        Patch(facecolor="#d9c57b", edgecolor="#9c7d2e", hatch="..", label="Generalized carbonate-bearing geology"),
        Line2D([], [], marker="^", color="none", markerfacecolor="#d97706", markeredgecolor="#7c2d12", markersize=9, label="Extraction"),
        Line2D([], [], marker="s", color="none", markerfacecolor="#1d4ed8", markeredgecolor="white", markersize=8, label="Primary processing"),
        Line2D([], [], color="#3b82a0", lw=1.2, label="Physical hydrography"),
    ], loc="lower right", frameon=True, framealpha=0.95, fontsize=8)

    panel.set_axis_off(); panel.set_facecolor("#f7f4ec")
    panel.text(0.5, 0.965, "HOW GEOLOGY BECOMES FUNCTION", ha="center", va="top", transform=panel.transAxes, fontsize=13, weight="bold", color="#17324d")
    box_label(panel, (0.50, 0.86), "CARBONATE BEDROCK\nregional occurrence", fc="#efe2ad", width=0.62)
    box_label(panel, (0.28, 0.69), "EXTRACTION\nWoodville sites", fc="#fde7c2", width=0.40)
    box_label(panel, (0.72, 0.69), "PROCESSING\nWoodville + Genoa", fc="#dbeafe", width=0.42)
    box_label(panel, (0.50, 0.52), "LIMESTONE / AGGREGATE\nLIME / DOLIME", fc="#e6f0f7", width=0.62)
    arrow_axes(panel, (0.50, 0.815), (0.28, 0.735), solid=False)
    arrow_axes(panel, (0.50, 0.815), (0.72, 0.735), solid=False)
    arrow_axes(panel, (0.28, 0.645), (0.44, 0.565), solid=True)
    arrow_axes(panel, (0.72, 0.645), (0.56, 0.565), solid=True)
    enduses = [
        ((0.25, 0.35), "WATER +\nWASTEWATER", "#d6eff7"),
        ((0.75, 0.35), "STEEL +\nINDUSTRY", "#e5e7eb"),
        ((0.25, 0.23), "AGRICULTURE +\nSOIL", "#dcfce7"),
        ((0.75, 0.23), "CONSTRUCTION +\nINFRASTRUCTURE", "#fef3c7"),
        ((0.50, 0.13), "ENVIRONMENTAL TREATMENT", "#d1fae5"),
    ]
    for xy, label, color in enduses:
        box_label(panel, xy, label, fc=color, width=0.40 if xy[0] != 0.5 else 0.58, height=0.08, size=8.2)
        arrow_axes(panel, (0.50, 0.475), (xy[0], xy[1]+0.05), solid=False, lw=1.4)
    panel.text(0.5, 0.002, "Solid = documented product relationship · Dashed = generalized dependency\nArrows are not freight routes; no supplier-to-Toledo contract is asserted.\nNo groundwater-flow, quarry-capture, or wetland-drawdown inference.",
               ha="center", va="bottom", transform=panel.transAxes, fontsize=7.4, color="#486581")
    for suffix in ["png", "svg"]:
        fig.savefig(MAP07.with_suffix(f".{suffix}"), dpi=220 if suffix == "png" else None, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def map08(nodes: pd.DataFrame) -> None:
    _, hydro, lake, roads, places = load_context()
    fig = plt.figure(figsize=(16, 10), facecolor="#f7f4ec")
    grid = fig.add_gridspec(1, 2, width_ratios=[0.88, 1.42], wspace=0.03)
    ax = fig.add_subplot(grid[0, 0]); net = fig.add_subplot(grid[0, 1])
    ax.set_facecolor("#eef3f5")
    lake.plot(ax=ax, color="#d7edf5", edgecolor="#6d9fb5", linewidth=0.7)
    hydro.plot(ax=ax, color="#4b91aa", linewidth=0.45, alpha=0.62)
    roads.plot(ax=ax, color="#9aa5b1", linewidth=0.5, alpha=0.45)
    locals_ = project_points(["BER-PROC-ELMORE", "BER-LEG-LUCKEY"], nodes)
    elmore = locals_[locals_.node_id == "BER-PROC-ELMORE"]
    luckey = locals_[locals_.node_id == "BER-LEG-LUCKEY"]
    elmore.plot(ax=ax, marker="*", color="#6d28d9", edgecolor="white", linewidth=1.3, markersize=260, zorder=8)
    luckey.plot(ax=ax, marker="X", color="#9ca3af", edgecolor="#4b5563", linewidth=0.7, markersize=75, zorder=7)
    erow = next(elmore.itertuples()); lrow = next(luckey.itertuples())
    ax.annotate("MATERION ELMORE\nADVANCED PROCESSING\nLOCAL EXTRACTION = FALSE", (erow.geometry.x, erow.geometry.y), xytext=(-10, 12), textcoords="offset points", ha="right", fontsize=8.6, weight="bold", color="#4c1d95", bbox=dict(boxstyle="round,pad=0.35", fc="#f5f3ff", ec="#8b5cf6"))
    ax.annotate("Luckey FUSRAP\nlegacy/remediation", (lrow.geometry.x, lrow.geometry.y), xytext=(-16, -25), textcoords="offset points", ha="right", fontsize=7.5, color="#6b7280", bbox=dict(boxstyle="round,pad=0.25", fc="#f3f4f6", ec="#9ca3af"))
    wanted = {"Toledo", "Elmore", "Luckey", "Genoa", "Woodville", "Oak Harbor", "Fremont"}
    place_points = places.copy(); place_points["geometry"] = place_points.geometry.representative_point()
    for row in place_points[place_points.BASENAME.isin(wanted)].itertuples():
        ax.plot(row.geometry.x, row.geometry.y, "o", ms=2.2, color="#52606d")
        ax.annotate(row.BASENAME, (row.geometry.x, row.geometry.y), xytext=(3, -6), textcoords="offset points", fontsize=7.2, color="#52606d")
    map_focus = (-83.75, 41.25, -82.92, 41.72)
    bounds = gpd.GeoSeries([Point(map_focus[0], map_focus[1]), Point(map_focus[2], map_focus[3])], crs=4326).to_crs(MAP_CRS)
    minx, miny = bounds.iloc[0].x, bounds.iloc[0].y; maxx, maxy = bounds.iloc[1].x, bounds.iloc[1].y
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title("REGIONAL ANCHOR", loc="left", fontsize=13, color="#17324d")
    ax.text(0.02, 0.025, "Physical waterways shown for context.\nNo transport route is mapped.", transform=ax.transAxes, fontsize=8, color="#486581", bbox=dict(boxstyle="round,pad=0.3", fc="#fff", ec="#bcccdc", alpha=0.9))
    add_north_scale(ax, minx + 5000, miny + 5500, 25_000)

    net.set_axis_off(); net.set_xlim(0, 1); net.set_ylim(0, 1)
    net.text(0.5, 0.975, "MAP 08 — BERYLLIUM STRATEGIC SUPPLY CHAIN", ha="center", va="top", fontsize=17, weight="bold", color="#17324d")
    net.text(0.5, 0.935, "2026 baseline · schematic relationships, not a transportation map", ha="center", fontsize=9.5, color="#486581")
    box_label(net, (0.10, 0.77), "EXTERNAL DOMESTIC\nRESOURCE (UTAH)", fc="#fef3c7", width=0.18)
    box_label(net, (0.10, 0.60), "IMPORTED BERYL\nGLOBAL SUPPLY", fc="#fef3c7", width=0.18)
    box_label(net, (0.34, 0.685), "BERYLLIUM HYDROXIDE\nINTERMEDIATE", fc="#ffedd5", width=0.22)
    box_label(net, (0.62, 0.685), "MATERION ELMORE\nADVANCED PROCESSING\nNOT A MINE", fc="#ede9fe", ec="#6d28d9", width=0.25, height=0.11, size=9.2)
    box_label(net, (0.87, 0.685), "ADVANCED BERYLLIUM\nMATERIALS", fc="#dbeafe", width=0.22)
    arrow_axes(net, (0.19, 0.77), (0.23, 0.70), solid=True, color="#9a6b16")
    arrow_axes(net, (0.19, 0.60), (0.23, 0.67), solid=True, color="#9a6b16")
    arrow_axes(net, (0.45, 0.685), (0.49, 0.685), solid=True, color="#9a6b16")
    arrow_axes(net, (0.745, 0.685), (0.76, 0.685), solid=True, color="#6d28d9")

    sectors = [
        ((0.20, 0.39), "AEROSPACE +\nDEFENSE", False, "#e0e7ff"),
        ((0.43, 0.39), "ELECTRONICS +\nTELECOM", False, "#e0e7ff"),
        ((0.66, 0.39), "PRECISION OPTICS +\nINSTRUMENTS", False, "#e0e7ff"),
        ((0.31, 0.19), "KAIROS POWER\nFLiBe / NUCLEAR", True, "#d1fae5"),
        ((0.69, 0.19), "CFS ARC\nBeF₂ → FLiBe / FUSION", True, "#d1fae5"),
    ]
    for xy, label, verified, color in sectors:
        box_label(net, xy, label, fc=color, ec="#047857" if verified else "#64748b", width=0.24 if xy[1] > 0.2 else 0.29, height=0.085, size=8.2)
        start = (0.87, 0.64) if not verified else (0.62, 0.63)
        arrow_axes(net, start, (xy[0], xy[1]+0.05), solid=verified, color="#047857" if verified else "#64748b", lw=1.7)
    net.text(0.69, 0.105, "Verified announcement: 31 Oct 2025\nElmore beryllium fluoride for CFS ARC FLiBe", transform=net.transAxes, ha="center", fontsize=8, color="#065f46")
    net.text(0.31, 0.105, "Documented 2022 collaboration;\n2026 operating status not independently reverified", transform=net.transAxes, ha="center", fontsize=8, color="#065f46")
    net.plot([0.05, 0.95], [0.075, 0.075], transform=net.transAxes, color="#d9e2ec", lw=1)
    net.text(0.5, 0.045, "Solid = observed or documented named relationship   ·   Dashed = broad sector inference\nNo mine-to-Elmore route, mode, schedule, tonnage, classified customer, or Northwest Ohio fusion reactor is inferred.", transform=net.transAxes, ha="center", va="center", fontsize=8.2, color="#486581")
    fig.savefig(MAP08.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(MAP08.with_suffix(".svg"), bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    NETWORKS.mkdir(parents=True, exist_ok=True); MAPS.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    nodes = pd.DataFrame(NODES); edges = pd.DataFrame(EDGES); sources = pd.DataFrame(SOURCES)
    nodes.to_csv(NODES_CSV, index=False); edges.to_csv(EDGES_CSV, index=False); sources.to_csv(SOURCES_CSV, index=False)
    spatial = nodes[nodes.latitude.notna() & nodes.longitude.notna()].copy()
    spatial_gdf = gpd.GeoDataFrame(spatial, geometry=gpd.points_from_xy(spatial.longitude, spatial.latitude), crs="EPSG:4326")
    pyogrio.write_dataframe(spatial_gdf, GPKG, layer="materials_flow_nodes", driver="GPKG", append=False)
    map07(nodes); map08(nodes)
    summary = {
        "phase": "Phase 2B - 2026 materials-flow baseline",
        "node_count": len(nodes),
        "edge_count": len(edges),
        "source_count": len(sources),
        "spatial_node_count": len(spatial),
        "relationship_basis_counts": edges.relationship_basis.value_counts().sort_index().to_dict(),
        "material_system_counts": nodes.material_system.value_counts().sort_index().to_dict(),
        "files": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in [NODES_CSV, EDGES_CSV, SOURCES_CSV, MAP07.with_suffix('.png'), MAP07.with_suffix('.svg'), MAP08.with_suffix('.png'), MAP08.with_suffix('.svg')]},
        "scientific_constraints": {
            "elmore_local_extraction": False,
            "unresolved_edges_are_transport_routes": False,
            "groundwater_flow_modeled": False,
            "shipment_quantities_modeled": False,
            "materials_corridor_geometry_created": False,
            "maps_09_or_10_created": False,
        },
    }
    MANIFEST.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
