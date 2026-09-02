"""Build Phase 4C qualitative information/governance futures for 2050/2075.

All records are fictional scenario deltas over the accepted/frozen Phase 4A and
Phase 4B 2026 baselines. This script does not modify baseline tables or maps and
does not model offensive security, sensitive topology, or probabilities.
"""
from __future__ import annotations

import hashlib
import json
import textwrap
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
NETWORKS = ROOT / "data/processed/networks"
ANALYSIS = ROOT / "data/processed/analysis"
SCENARIOS = ROOT / "data/processed/scenarios"
MAPS = ROOT / "outputs/maps/systems"
FIGURES = ROOT / "outputs/figures"
REPORTS = ROOT / "reports"
GPKG = ROOT / "data/processed/glasspunk_base.gpkg"

ASSUMPTIONS = SCENARIOS / "information_scenario_assumptions.csv"
NODES = SCENARIOS / "information_nodes_scenario.csv"
EDGES = SCENARIOS / "information_edges_scenario.csv"
BLINDSPOTS = SCENARIOS / "information_blind_spots_scenario.csv"
AUTHORITY = SCENARIOS / "information_authority_scenario.csv"
COMPARISON = FIGURES / "information_scenarios_comparison.csv"
MAP2050 = MAPS / "16_information_governance_futures_2050"
MAP2075 = MAPS / "16b_information_governance_futures_2075"
COMPARISON_BASE = FIGURES / "information_scenarios_comparison"
MANIFEST = REPORTS / "information_scenario_manifest.json"
RETRIEVED_DATE = "2026-09-02"

ASSUMPTION_COLUMNS = ["assumption_id", "scenario_id", "scenario_year", "domain", "assumption", "basis", "source_id", "plausibility", "uncertainty", "dependency", "status", "notes"]
NODE_COLUMNS = ["object_id", "scenario_id", "scenario_year", "baseline_object_id", "object_name", "domain", "future_role", "change_type", "reality_status", "relationship_basis", "assumption_id", "plausibility", "source_or_basis", "notes"]
EDGE_COLUMNS = ["edge_id", "scenario_id", "scenario_year", "from_object_id", "to_object_id", "relationship_type", "change_type", "reality_status", "relationship_basis", "assumption_id", "plausibility", "source_or_basis", "notes"]
BLIND_COLUMNS = ["blindspot_state_id", "scenario_id", "scenario_year", "baseline_blindspot_id", "domain", "affected_chain", "change_type", "future_blindspot", "description", "assumption_id", "plausibility", "relationship_basis", "source_or_basis", "notes"]
AUTHORITY_COLUMNS = ["scenario_id", "scenario_year", "observes", "analyzes", "advises", "decides", "operates_or_responds", "authority_pattern", "assumption_id", "plausibility", "reality_status", "relationship_basis", "source_or_basis", "notes"]
COMPARISON_COLUMNS = ["scenario_id", "scenario_year", "scenario_family", "openness", "interoperability", "sensing_density", "automation", "human_decision_authority", "redundancy", "data_concentration", "privacy_constraint", "security_constraint", "model_dependence", "public_transparency", "resilience_to_information_loss"]

SCENARIO_SPECS = {
    "A2050": {
        "year": 2050, "family": "Trusted Public Infrastructure", "plausibility": "moderate",
        "assumptions": [
            ("cross_system", "Interoperable public observation standards expand across selected water, weather, and environmental products.", "scenario extrapolation from coordinated observing-system guidance", "phase4c_noaa_ioos", "moderate", "moderate", "IOOS-style coordination and compatible public products", "No universal data standard or complete coverage is assumed."),
            ("cross_system", "Provenance and public explanation become routine properties of high-consequence decision-support products.", "scenario extrapolation from trustworthy AI and resilience guidance", "phase4c_nist_ai_rmf", "moderate", "moderate", "shared catalogs and traceable source lineage", "The scenario strengthens provenance without making every process transparent."),
            ("lake_erie_hab", "HAB and drinking-water products share selected cross-agency inputs while City authority remains human.", "Phase 4A/4B factual chain plus scenario assumption", "phase4a_glerl_hab", "moderate", "moderate", "shared forecast and explanation products", "A direct machine-to-machine feed is not required by the scenario."),
            ("maumee_hydrology", "Flood and weather products expose clearer public context and interoperable warning explanations.", "Phase 4A/4B factual chain plus scenario assumption", "phase4a_nws_flood", "moderate", "moderate", "public warning interoperability", "No precise warning latency or coverage is forecast."),
            ("environmental_regulatory", "Selected regulatory records gain stronger provenance and cross-agency linkage while case authority remains institutional.", "scenario extrapolation from public environmental data and AI governance", "phase4c_nist_ai_rmf", "moderate", "moderate", "traceable public regulatory data", "No universal open access to operational or enforcement records is assumed."),
            ("energy_information", "PJM/EIA information remains partly public while operator and infrastructure boundaries remain protected.", "Phase 4A/4B factual boundary plus resilience guidance", "phase4c_cisa_cpg", "high", "moderate", "public context plus restricted operational detail", "No SCADA or private telemetry is introduced."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "NOAA GLERL interoperable HAB observation coordinator", "lake_erie_hab", "expanded coordinated observation role", "expand_role", "phase4c_noaa_ioos"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "Publicly cataloged GLOS crib data product", "lake_erie_hab", "provenance-linked public data product", "data_opened", "phase4c_nist_ai_rmf"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "Shared Lake Erie HAB decision-support forecast", "lake_erie_hab", "interoperable forecast role", "provenance_strengthened", "phase4a_glerl_hab"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "City of Toledo human water decision authority", "lake_erie_hab", "human decision authority retained", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "Interoperable public water-prediction service", "maumee_hydrology", "shared forecast context", "expand_role", "phase4c_noaa_ioos"),
            ("OBS-ORG-NWS", "NWS transparent warning and explanation role", "maumee_hydrology", "public warning advisor", "expand_role", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Provenance-linked environmental compliance data", "environmental_regulatory", "traceable regulatory data product", "provenance_strengthened", "phase4c_nist_ai_rmf"),
            ("OBS-DAT-PJM-DATAMINER", "Publicly documented PJM operating context", "energy_information", "high-level public operator information", "persist", "phase4a_pjm_dataminer"),
            ("OBS-ORG-PJM", "PJM human regional operator authority", "energy_information", "operator authority retained", "human_authority_retained", "phase4a_pjm_operations"),
            ("", "Regional provenance and catalog function", "cross_system", "shared source lineage and explanation", "new_function", "phase4c_nist_ai_rmf"),
            ("", "Cross-agency model interoperability function", "cross_system", "compatible model exchange", "new_function", "phase4c_noaa_ioos"),
            ("", "Public decision explanation function", "cross_system", "human-readable decision context", "new_function", "phase4c_nist_ai_rmf"),
        ],
        "authority": ("GLOS/IOOS; NOAA GLERL; USGS; regulated reporters; EIA/PJM public interfaces", "NOAA forecast services; EPA/state programs; public operator analysis", "NOAA/NWS forecasts, EPA/ECHO context, public explanation products", "City of Toledo, NWS/public authorities, EPA/state authorities, PJM retain human authority", "City water operations, NWS warnings, regulatory response, and PJM coordination remain institutionally operated", "interoperable coordination with human authority retained"),
        "blind": [("IBS-A-001", "lake_erie_hab", "A", "reduced", "Unequal spatial coverage remains despite interoperable catalogs.", "More comparable products, but point observations still do not represent the full lake or intake geometry."), ("IBS-A-003", "lake_erie_hab", "A", "transformed", "Model uncertainty becomes more visible through provenance and explanation.", "Transparency improves interpretation without resolving forecast error or local thresholds."), ("IBS-B-003", "maumee_hydrology", "B", "reduced", "Warning timing is more legible across public products, but event-specific latency remains variable.", "Public understanding improves without a guaranteed response interval."), ("IBS-C-001", "environmental_regulatory", "C", "transformed", "Public records are more traceable but still do not equal continuous raw measurement.", "Provenance improves; periodic or self-reported coverage remains."), ("IBS-D-001", "energy_information", "D", "persists", "Public energy data remain intentionally incomplete at the operational layer.", "Interoperability does not open private telemetry or internal workflows."), ("", "cross_system", "X", "new_blindspot", "Institutional complexity from shared standards and explanation duties.", "More interfaces create new maintenance and accountability burdens.")],
        "comparison": ("moderate", "high", "moderate", "moderate", "high", "moderate", "moderate", "moderate", "moderate", "high", "moderate", "moderate"),
    },
    "A2075": {
        "year": 2075, "family": "Trusted Public Infrastructure", "plausibility": "moderate",
        "assumptions": [
            ("cross_system", "Interoperability is mature across major public environmental and infrastructure information products.", "scenario continuation from IOOS coordination driver", "phase4c_noaa_ioos", "moderate", "moderate", "shared public standards", "Mature coordination does not imply universal integration."),
            ("cross_system", "Source provenance, model lineage, and public explanations are treated as routine infrastructure.", "scenario continuation from NIST AI RMF", "phase4c_nist_ai_rmf", "moderate", "moderate", "traceable analysis", "Institutional trust remains uneven."),
            ("lake_erie_hab", "Lake Erie forecasts and drinking-water evidence are jointly legible across agencies, with City authority retained.", "Phase 4A/4B chain plus scenario continuation", "phase4a_glerl_hab", "moderate", "moderate", "shared water decision context", "No single integrated lake truth system is assumed."),
            ("maumee_hydrology", "Hydrologic and weather information is interoperable enough to support regional warning explanation.", "Phase 4A/4B chain plus scenario continuation", "phase4a_nws_flood", "moderate", "moderate", "regional warning context", "No complete basin coverage is assumed."),
            ("environmental_regulatory", "Regulatory data lineage is broadly shared while legal authority remains distributed.", "scenario continuation from EPA data boundary", "phase4a_epa_echo", "moderate", "moderate", "provenance-linked oversight", "Shared data do not erase jurisdiction."),
            ("energy_information", "PJM and public statistical information are trusted public interfaces around protected operational detail.", "scenario continuation from PJM/CISA boundary", "phase4c_cisa_cpg", "high", "moderate", "public context with operational limits", "No sensitive infrastructure disclosure is assumed."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "Mature interoperable Great Lakes observation coordination", "lake_erie_hab", "mature shared observation role", "expand_role", "phase4c_noaa_ioos"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "Mature provenance-linked lake observation product", "lake_erie_hab", "open, traceable public product", "data_opened", "phase4c_nist_ai_rmf"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "Mature explainable HAB forecast service", "lake_erie_hab", "shared forecast and explanation", "provenance_strengthened", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "City of Toledo human water authority", "lake_erie_hab", "human decision authority retained", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "Mature regional water-prediction service", "maumee_hydrology", "interoperable forecast service", "expand_role", "phase4c_noaa_ioos"),
            ("OBS-ORG-NWS", "NWS regional warning explanation authority", "maumee_hydrology", "public warning advisor", "expand_role", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Traceable public environmental record", "environmental_regulatory", "mature provenance-linked data", "provenance_strengthened", "phase4c_nist_ai_rmf"),
            ("OBS-DAT-PJM-DATAMINER", "Mature public PJM operating context", "energy_information", "stable public operator interface", "persist", "phase4a_pjm_dataminer"),
            ("OBS-ORG-PJM", "PJM human regional operator authority", "energy_information", "operator authority retained", "human_authority_retained", "phase4a_pjm_operations"),
            ("", "Regional data provenance utility", "cross_system", "shared lineage and explanation infrastructure", "new_node", "phase4c_nist_ai_rmf"),
            ("", "Public model-comparison service", "cross_system", "cross-agency model comparison", "new_function", "phase4c_noaa_ioos"),
            ("", "Public decision-audit explanation function", "cross_system", "institutional explanation and audit", "new_function", "phase4c_nist_ai_rmf"),
        ],
        "authority": ("GLOS/NOAA/USGS and regulated reporters through shared public standards", "NOAA/NWS/EPA/state/PJM analytical services", "Public forecast, regulatory lineage, and explanation services", "City, NWS/public authorities, EPA/state authorities, and PJM retain human authority", "Institutional operators retain response authority", "mature interoperability with distributed human authority"),
        "blind": [("IBS-A-001", "lake_erie_hab", "A", "reduced", "Coverage metadata and coordinated observation reduce but do not eliminate spatial blind spots.", "The physical intake discrepancy remains unresolved unless separately reviewed."), ("IBS-A-002", "lake_erie_hab", "A", "resolved", "Current station status and cadence are assumed documented within this scenario.", "This is a scenario condition, not a factual claim about 2026."), ("IBS-B-001", "maumee_hydrology", "B", "reduced", "Regional observation coordination reduces point-coverage dependence.", "No complete basin representation is guaranteed."), ("IBS-C-002", "environmental_regulatory", "C", "persists", "Jurisdiction boundaries remain even with shared provenance.", "Data sharing does not create a single regulator."), ("IBS-D-001", "energy_information", "D", "persists", "Protected operational information remains a public-data boundary.", "Trust does not require exposing sensitive detail."), ("", "cross_system", "X", "new_blindspot", "Standard fatigue and institutional accountability across mature shared infrastructure.", "Long-lived interoperability creates maintenance and legitimacy obligations.")],
        "comparison": ("high", "high", "high", "moderate", "high", "high", "moderate", "moderate", "moderate", "high", "high", "high"),
    },
    "B2050": {
        "year": 2050, "family": "Federated Resilience", "plausibility": "moderate",
        "assumptions": [
            ("cross_system", "Observation ownership remains distributed among agencies, municipalities, and operators.", "scenario extrapolation from IOOS coordination and local resilience", "phase4c_noaa_ioos", "moderate", "moderate", "federated exchange", "No single regional data owner is assumed."),
            ("cross_system", "Selective exchange and minimum-necessary data practices become normal for public/operational boundaries.", "scenario extrapolation from NIST Privacy Framework", "phase4c_nist_privacy_framework", "moderate", "moderate", "federated sharing", "No specific privacy technology is assumed."),
            ("lake_erie_hab", "Local water managers retain decision capability while lake observations and forecasts are cross-checked across organizations.", "Phase 4A/4B chain plus scenario assumption", "phase4a_toledo_water_quality", "moderate", "moderate", "local decision resilience", "No local autonomy guarantee is made."),
            ("maumee_hydrology", "Municipal and regional flood information can degrade gracefully when a central product is unavailable.", "scenario extrapolation from CISA continuity guidance", "phase4c_cisa_cpg", "moderate", "moderate", "redundant local exchange", "No specific outage or response delay is forecast."),
            ("environmental_regulatory", "Regulated reporters, state authorities, and federal programs exchange selected records without collapsing jurisdiction.", "Phase 4B authority boundary plus scenario assumption", "phase4a_epa_npdes", "moderate", "moderate", "selective regulatory federation", "Periodic reporting remains periodic."),
            ("energy_information", "PJM and utilities preserve operational boundaries while exchanging high-level continuity information.", "Phase 4A/4B public boundary plus CISA guidance", "phase4c_cisa_cpg", "moderate", "moderate", "federated operator continuity", "No utility topology is modeled."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "Federated Great Lakes HAB observation participant", "lake_erie_hab", "distributed observation ownership", "federated_exchange", "phase4c_noaa_ioos"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "Locally governed GLOS crib data product", "lake_erie_hab", "selectively shared lake data", "federated_exchange", "phase4c_nist_privacy_framework"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "Cross-checked regional HAB model", "lake_erie_hab", "multiple-model advisory role", "model_dependence_increased", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "Municipal water decision authority", "lake_erie_hab", "local human authority", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "Federated water-prediction participant", "maumee_hydrology", "regional/local forecast exchange", "federated_exchange", "phase4c_cisa_cpg"),
            ("OBS-ORG-NWS", "NWS warning coordination participant", "maumee_hydrology", "shared warning advisor", "federated_exchange", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Selective environmental reporting exchange", "environmental_regulatory", "federated regulatory data", "data_restricted", "phase4c_nist_privacy_framework"),
            ("OBS-DAT-PJM-DATAMINER", "Federated PJM continuity information", "energy_information", "selective public/operator context", "federated_exchange", "phase4c_cisa_cpg"),
            ("OBS-ORG-PJM", "PJM/operator authority with local coordination", "energy_information", "distributed coordination authority", "human_authority_retained", "phase4a_pjm_operations"),
            ("", "Local edge analysis function", "cross_system", "municipal/local processing", "new_function", "phase4c_noaa_ioos"),
            ("", "Federated exchange agreement function", "cross_system", "selective data federation", "federated_exchange", "phase4c_nist_privacy_framework"),
            ("", "Continuity and redundancy function", "cross_system", "graceful degradation support", "redundancy_added", "phase4c_cisa_cpg"),
        ],
        "authority": ("Local municipalities, GLOS/NOAA/USGS participants, reporters, utilities/operators", "Local edge analysis plus NOAA/NWS/EPA/PJM participants", "Multiple organizations cross-check and advise", "City, NWS/public authorities, EPA/state authorities, and PJM retain local/institutional decisions", "Distributed local and regional operators respond", "federated authority with local autonomy and redundancy"),
        "blind": [("IBS-A-004", "lake_erie_hab", "A", "persists", "The direct forecast-to-Toledo handoff remains locally negotiated rather than universal.", "Federation supports exchange but does not prove one common feed."), ("IBS-B-002", "maumee_hydrology", "B", "transformed", "Station-to-forecast provenance differs across federated participants.", "Multiple paths exist, but standards and lineage can vary."), ("IBS-B-003", "maumee_hydrology", "B", "reduced", "Local fallback products reduce dependence on one warning service.", "Timeliness remains uneven across jurisdictions."), ("IBS-C-002", "environmental_regulatory", "C", "persists", "Jurisdiction boundaries remain explicit and may complicate handoffs.", "Fragmentation is not treated as regulatory failure."), ("IBS-D-001", "energy_information", "D", "reduced", "Federated continuity information reduces central-service dependence.", "Operational detail remains nonpublic."), ("", "cross_system", "X", "new_blindspot", "Data fragmentation and inconsistent standards across local owners.", "Resilience gains can trade against interoperability.")],
        "comparison": ("moderate", "moderate", "moderate", "moderate", "high", "high", "low", "high", "moderate", "moderate", "high", "high"),
    },
    "B2075": {
        "year": 2075, "family": "Federated Resilience", "plausibility": "moderate",
        "assumptions": [
            ("cross_system", "Distributed observation owners use durable federation agreements rather than one central platform.", "scenario continuation from IOOS and resilience guidance", "phase4c_noaa_ioos", "moderate", "moderate", "federated exchange", "No universal standard is assumed."),
            ("cross_system", "Minimum-necessary exchange and privacy-aware stewardship remain institutional norms.", "scenario continuation from NIST Privacy Framework", "phase4c_nist_privacy_framework", "moderate", "moderate", "selective access", "No specific privacy technology is assumed."),
            ("lake_erie_hab", "Toledo and neighboring authorities maintain local water decisions while multiple observation paths cross-check one another.", "Phase 4A/4B chain plus scenario continuation", "phase4a_toledo_water_quality", "moderate", "moderate", "local resilience", "No single authority controls all lake information."),
            ("maumee_hydrology", "Flood information remains resilient through local fallback and regional coordination.", "scenario continuation from CISA guidance", "phase4c_cisa_cpg", "moderate", "moderate", "redundant local services", "No exact fallback performance is forecast."),
            ("environmental_regulatory", "Regulatory data exchange is federated, with durable state/federal jurisdiction boundaries.", "Phase 4B authority boundary plus scenario continuation", "phase4a_epa_npdes", "moderate", "moderate", "federated oversight", "Shared data do not create one regulator."),
            ("energy_information", "Operator continuity depends on multiple trusted regional information exchanges with protected details.", "scenario continuation from PJM/CISA boundary", "phase4c_cisa_cpg", "moderate", "moderate", "distributed continuity", "No sensitive topology is exposed."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "Mature federated Great Lakes observation network", "lake_erie_hab", "distributed observation role", "federated_exchange", "phase4c_noaa_ioos"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "Federated/local lake observation product", "lake_erie_hab", "selectively shared data", "federated_exchange", "phase4c_nist_privacy_framework"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "Multi-model regional HAB advisory", "lake_erie_hab", "cross-checked forecast", "model_dependence_increased", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "Municipal water decision authority", "lake_erie_hab", "local human authority", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "Federated regional water prediction", "maumee_hydrology", "fallback-compatible forecast role", "federated_exchange", "phase4c_cisa_cpg"),
            ("OBS-ORG-NWS", "Federated NWS warning role", "maumee_hydrology", "regional warning coordinator", "federated_exchange", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Federated environmental record", "environmental_regulatory", "selective regulatory exchange", "data_restricted", "phase4c_nist_privacy_framework"),
            ("OBS-DAT-PJM-DATAMINER", "Distributed operator-information exchange", "energy_information", "selective public/operator context", "federated_exchange", "phase4c_cisa_cpg"),
            ("OBS-ORG-PJM", "Distributed PJM/operator authority", "energy_information", "federated operator coordination", "human_authority_retained", "phase4a_pjm_operations"),
            ("", "Local model comparison function", "cross_system", "independent model checking", "new_function", "phase4c_nist_ai_rmf"),
            ("", "Federated data stewardship function", "cross_system", "minimum-necessary exchange", "federated_exchange", "phase4c_nist_privacy_framework"),
            ("", "Regional continuity mesh function", "cross_system", "distributed fallback support", "redundancy_added", "phase4c_cisa_cpg"),
        ],
        "authority": ("Distributed municipalities, agencies, reporters, and operators", "Local and regional model participants", "Multiple independent advisory products", "Local municipal, state/federal, NWS/public, and PJM authorities retain decisions", "Distributed operators and public-safety organizations respond", "mature federation with local autonomy and cross-checking"),
        "blind": [("IBS-A-004", "lake_erie_hab", "A", "persists", "Local forecast handoffs remain negotiated across federated owners.", "Federation does not create one Toledo-specific external feed."), ("IBS-B-002", "maumee_hydrology", "B", "transformed", "Multiple forecast paths create lineage comparison work.", "More alternatives can make disagreement harder to resolve."), ("IBS-B-003", "maumee_hydrology", "B", "reduced", "Fallback services reduce dependence on one timing path.", "Local timing remains variable."), ("IBS-C-002", "environmental_regulatory", "C", "persists", "Jurisdiction is durable and visible.", "Federated data do not merge legal authority."), ("IBS-D-001", "energy_information", "D", "reduced", "Central public-data dependence is reduced.", "Protected operator details remain unavailable."), ("", "cross_system", "X", "new_blindspot", "Federated model disagreement and standard divergence.", "Autonomy can make regional synthesis slower or contested.")],
        "comparison": ("moderate", "moderate", "high", "moderate", "high", "high", "low", "high", "moderate", "moderate", "high", "high"),
    },
    "C2050": {
        "year": 2050, "family": "High-Automation / Contested Information", "plausibility": "exploratory",
        "assumptions": [
            ("cross_system", "Dense sensing and machine-assisted analysis become strategically valuable across environmental and infrastructure domains.", "explicit fictional scenario extrapolation from AI governance and observing systems", "phase4c_nist_ai_rmf", "exploratory", "high", "AI-assisted analysis and model dependence", "No precise sensor count or deployment is assumed."),
            ("cross_system", "Automated anomaly detection and recommendation expand, but final public authority remains human-supervised.", "explicit fictional scenario assumption bounded by NIST AI RMF", "phase4c_nist_ai_rmf", "exploratory", "high", "human-in-the-loop decision support", "AI does not receive sovereign or final governmental authority."),
            ("lake_erie_hab", "HAB forecasts combine dense observations and AI-assisted analysis, increasing speed and model dependence for water managers.", "Phase 4A/4B chain plus explicit scenario assumption", "phase4a_glerl_hab", "exploratory", "high", "forecast/model dependence", "No local treatment automation or threshold is asserted."),
            ("maumee_hydrology", "Flood systems use machine-assisted anomaly detection and predictive products while NWS/public authorities retain warning authority.", "Phase 4A/4B chain plus explicit scenario assumption", "phase4c_nist_ai_rmf", "exploratory", "high", "automated analysis with human warning authority", "No exact prediction or response performance is forecast."),
            ("environmental_regulatory", "Environmental records gain stronger authentication/provenance while contested interpretations and access limits increase.", "EPA boundary plus NIST/CISA scenario extrapolation", "phase4c_cisa_cpg", "exploratory", "high", "trusted lineage versus contested interpretation", "No attack path or vulnerability is modeled."),
            ("energy_information", "PJM/operator information becomes more interconnected and compute-dependent while operational access becomes more restricted.", "Phase 4A/4B public boundary plus explicit scenario assumption", "phase4c_cisa_cpg", "exploratory", "high", "automation, availability, and restricted operational information", "No SCADA or sensitive topology is introduced."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "Dense Great Lakes HAB observation coordinator", "lake_erie_hab", "dense sensing and machine-assisted coordination", "expand_role", "phase4c_nist_ai_rmf"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "High-value lake observation data product", "lake_erie_hab", "increased data concentration and provenance", "dependency_increased", "phase4c_cisa_cpg"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "AI-assisted Lake Erie HAB forecast", "lake_erie_hab", "automated analysis and recommendation", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "City human supervisory water authority", "lake_erie_hab", "human final decision authority retained", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "AI-assisted water-prediction service", "maumee_hydrology", "automated anomaly detection and forecast analysis", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-NWS", "NWS warning authority with machine recommendations", "maumee_hydrology", "human warning authority over automated analysis", "human_authority_retained", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Authenticated environmental compliance record", "environmental_regulatory", "stronger provenance and access controls", "provenance_strengthened", "phase4c_cisa_cpg"),
            ("OBS-DAT-PJM-DATAMINER", "High-volume PJM operating-information interface", "energy_information", "increased machine-to-machine dependence", "dependency_increased", "phase4c_cisa_cpg"),
            ("OBS-ORG-PJM", "PJM operator with human supervisory authority", "energy_information", "operator-led automation with human authority", "automated_operation", "phase4a_pjm_operations"),
            ("", "AI-assisted cross-domain analysis function", "cross_system", "machine-assisted synthesis", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("", "Automated anomaly detection function", "cross_system", "rapid signal triage", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("", "Provenance and authentication assurance function", "cross_system", "trusted lineage and access control", "provenance_strengthened", "phase4c_cisa_cpg"),
        ],
        "authority": ("Dense public and operational sensors; agencies and operators remain data stewards", "AI-assisted NOAA/NWS/EPA/PJM analysis", "Machine recommendations plus human institutional advisors", "City, NWS/public authorities, EPA/state authorities, and PJM retain final authority", "Selected operators use bounded automation under human supervision", "operator-led automation with human supervisory authority and restricted data"),
        "blind": [("IBS-A-003", "lake_erie_hab", "A", "transformed", "Forecast uncertainty becomes model-opacity and contestation risk.", "More analysis can increase speed while making model disagreement harder to explain."), ("IBS-A-004", "lake_erie_hab", "A", "persists", "The direct forecast-to-Toledo handoff remains an institutional trust boundary.", "Automation does not establish municipal use or authority."), ("IBS-B-003", "maumee_hydrology", "B", "transformed", "Latency may shrink, but system dependence and model disagreement become new concerns.", "Faster products do not guarantee trustworthy warnings."), ("IBS-C-001", "environmental_regulatory", "C", "transformed", "Authenticated records can still be incomplete, periodic, or contested in interpretation.", "Integrity improvements do not create continuous observation."), ("IBS-D-001", "energy_information", "D", "transformed", "Public-data gaps become stronger operational-data separation and compute dependence.", "Interconnection increases value without opening sensitive detail."), ("", "cross_system", "X", "new_blindspot", "Model opacity and institutional trust gap.", "The main risk is contested interpretation, not a specified attack." )],
        "comparison": ("low", "high", "high", "high", "moderate", "moderate", "high", "high", "high", "moderate", "moderate", "moderate"),
    },
    "C2075": {
        "year": 2075, "family": "High-Automation / Contested Information", "plausibility": "exploratory",
        "assumptions": [
            ("cross_system", "Information infrastructure is dense, interconnected, and treated as a strategic continuity asset.", "explicit fictional continuation from AI/resilience guidance", "phase4c_cisa_cpg", "exploratory", "high", "availability, provenance, and concentration", "No physical network topology is modeled."),
            ("cross_system", "AI-assisted analysis and bounded automated operations are common, but human authority remains explicit and contestable.", "explicit fictional continuation bounded by NIST AI RMF", "phase4c_nist_ai_rmf", "exploratory", "high", "supervisory human authority", "No sovereign AI or final governmental AI authority is assumed."),
            ("lake_erie_hab", "Lake Erie water decisions depend on dense observation/model ecosystems with strong provenance and persistent model disagreement.", "Phase 4A/4B chain plus explicit scenario continuation", "phase4c_nist_ai_rmf", "exploratory", "high", "model dependence and trust", "No exact sensor locations or treatment controls are forecast."),
            ("maumee_hydrology", "Flood understanding relies on automated analysis, local fallback, and human/public warning legitimacy.", "Phase 4A/4B chain plus explicit scenario continuation", "phase4c_cisa_cpg", "exploratory", "high", "automated continuity and authority", "No response probability or delay is calculated."),
            ("environmental_regulatory", "Regulatory decisions use authenticated machine-assisted records but remain jurisdictionally and politically contested.", "EPA boundary plus explicit scenario continuation", "phase4c_nist_ai_rmf", "exploratory", "high", "provenance versus legitimacy", "No specific failure or enforcement outcome is asserted."),
            ("energy_information", "Energy information is highly interconnected, compute-dependent, and selectively restricted around operator decisions.", "Phase 4A/4B boundary plus explicit scenario continuation", "phase4c_cisa_cpg", "exploratory", "high", "availability, concentration, and restricted access", "No sensitive topology or offensive security content is modeled."),
        ],
        "nodes": [
            ("OBS-NET-NOAA-GLERL-HAB", "Mature dense HAB observation ecosystem", "lake_erie_hab", "dense interconnected sensing", "expand_role", "phase4c_nist_ai_rmf"),
            ("OBS-DAT-GLOS-ERDDAP-CRIB", "Strategic lake information product", "lake_erie_hab", "high-value authenticated data dependency", "dependency_increased", "phase4c_cisa_cpg"),
            ("OBS-MOD-NOAA-HAB-FORECAST", "Mature AI-assisted HAB forecast", "lake_erie_hab", "automated analysis under human review", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-CITY-TOLEDO-WATER", "City human supervisory water authority", "lake_erie_hab", "human final decision authority retained", "human_authority_retained", "phase4a_toledo_water_quality"),
            ("OBS-MOD-NOAA-NWPS", "Mature automated water-prediction service", "maumee_hydrology", "automated forecast and anomaly analysis", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("OBS-ORG-NWS", "NWS human warning legitimacy authority", "maumee_hydrology", "human/public authority over automated products", "human_authority_retained", "phase4a_nws_flood"),
            ("OBS-DAT-EPA-ECHO", "Authenticated machine-assisted environmental record", "environmental_regulatory", "restricted/provenance-strong data product", "data_restricted", "phase4c_cisa_cpg"),
            ("OBS-DAT-PJM-DATAMINER", "Strategic PJM information interface", "energy_information", "high-concentration operating information", "dependency_increased", "phase4c_cisa_cpg"),
            ("OBS-ORG-PJM", "PJM operator-led bounded automation", "energy_information", "automated operations with human authority", "automated_operation", "phase4a_pjm_operations"),
            ("", "Mature AI-assisted cross-domain analysis", "cross_system", "machine synthesis of competing products", "automated_analysis", "phase4c_nist_ai_rmf"),
            ("", "Mature automated continuity function", "cross_system", "bounded automated fallback operation", "automated_operation", "phase4c_cisa_cpg"),
            ("", "Institutional provenance and trust function", "cross_system", "authentication, lineage, and explanation", "provenance_strengthened", "phase4c_nist_ai_rmf"),
        ],
        "authority": ("Dense public/operational observation ecosystem and distributed stewards", "AI-assisted and automated NOAA/NWS/EPA/PJM analysis", "Machine recommendations, competing models, and human institutional advisors", "Human City, NWS/public, EPA/state, and PJM authorities retain final decisions", "Bounded automated continuity and operator actions remain supervised", "high automation with contested information and explicit human authority"),
        "blind": [("IBS-A-003", "lake_erie_hab", "A", "transformed", "Model opacity, disagreement, and concentration replace simpler coverage questions.", "More sensing does not ensure shared interpretation."), ("IBS-A-004", "lake_erie_hab", "A", "persists", "Institutional trust and municipal authority remain a boundary around external products.", "No automatic promotion of forecast to decision is assumed."), ("IBS-B-002", "maumee_hydrology", "B", "transformed", "Multiple automated models create provenance and disagreement burdens.", "More models can produce more contested warnings."), ("IBS-C-001", "environmental_regulatory", "C", "transformed", "Authenticated records may be restricted, incomplete, or difficult to interpret politically.", "Integrity does not guarantee legitimacy or coverage."), ("IBS-D-001", "energy_information", "D", "transformed", "Information concentration and operational restriction become central public blind spots.", "The public interface remains deliberately incomplete."), ("", "cross_system", "X", "new_blindspot", "Algorithmic dependence and institutional trust gap.", "Fast optimization can outpace shared legitimacy.")],
        "comparison": ("low", "high", "high", "high", "moderate", "moderate", "high", "high", "high", "low", "moderate", "moderate"),
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_assumptions() -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        for index, (domain, assumption, basis, source_id, plausibility, uncertainty, dependency, notes) in enumerate(spec["assumptions"], 1):
            rows.append((f"ISA-{scenario_id}-{index:02d}", scenario_id, spec["year"], domain, assumption, basis, source_id, plausibility, uncertainty, dependency, "scenario_assumption", notes))
    return pd.DataFrame(rows, columns=ASSUMPTION_COLUMNS)


def make_nodes(assumptions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        assumption_ids = assumptions.loc[assumptions.scenario_id == scenario_id, "assumption_id"].tolist()
        for index, (baseline_id, name, domain, role, change, source) in enumerate(spec["nodes"], 1):
            aid = assumption_ids[min(index - 1, len(assumption_ids) - 1)]
            object_id = f"IF-{scenario_id}-{index:02d}"
            plausibility = "exploratory" if scenario_id.startswith("C") else ("high" if index in {4, 6, 9} else "moderate")
            rows.append((object_id, scenario_id, spec["year"], baseline_id, name, domain, role, change, "fictional", "scenario_assumption", aid, plausibility, source, "Scenario delta only; no future coordinate or quantitative deployment claim."))
    return pd.DataFrame(rows, columns=NODE_COLUMNS)


def make_edges(nodes: pd.DataFrame, assumptions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        n = nodes[nodes.scenario_id == scenario_id].sort_values("object_id").object_id.tolist()
        a = assumptions.loc[assumptions.scenario_id == scenario_id, "assumption_id"].tolist()
        edge_defs = [
            (n[0], n[1], "supports_decision", "provenance_strengthened"),
            (n[1], n[2], "feeds", "new_edge"),
            (n[2], n[3], "supports_decision", "human_authority_retained"),
            (n[4], n[5], "supports_decision", "new_edge"),
            (n[5], n[3], "supports_decision", "new_edge"),
            (n[6], n[3], "used_by", "new_edge"),
            (n[7], n[8], "used_by", "new_edge"),
            (n[9], n[10], "supports_decision", "new_edge"),
        ]
        for index, (from_id, to_id, relationship, change) in enumerate(edge_defs, 1):
            aid = a[(index - 1) % len(a)]
            source = assumptions.loc[assumptions.assumption_id == aid, "source_id"].iloc[0]
            rows.append((f"IFE-{scenario_id}-{index:02d}", scenario_id, spec["year"], from_id, to_id, relationship, change, "fictional", "scenario_assumption", aid, "exploratory" if scenario_id.startswith("C") else "moderate", source, "Scenario relationship only; not a physical communication route or automated final decision."))
    return pd.DataFrame(rows, columns=EDGE_COLUMNS)


def make_blindspots(assumptions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        aids = assumptions.loc[assumptions.scenario_id == scenario_id, "assumption_id"].tolist()
        for index, (baseline_id, domain, chain, change, future_blindspot, description) in enumerate(spec["blind"], 1):
            aid = aids[(index - 1) % len(aids)]
            source = assumptions.loc[assumptions.assumption_id == aid, "source_id"].iloc[0]
            rows.append((f"IBSS-{scenario_id}-{index:02d}", scenario_id, spec["year"], baseline_id, domain, chain, change, future_blindspot, description, aid, "exploratory" if scenario_id.startswith("C") else "moderate", "scenario_assumption", source, "Qualitative scenario evolution of an information gap; not a vulnerability or failure claim."))
    return pd.DataFrame(rows, columns=BLIND_COLUMNS)


def make_authority(assumptions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        aid = assumptions.loc[assumptions.scenario_id == scenario_id, "assumption_id"].iloc[0]
        source = assumptions.loc[assumptions.assumption_id == aid, "source_id"].iloc[0]
        observes, analyzes, advises, decides, operates, pattern = spec["authority"]
        rows.append((scenario_id, spec["year"], observes, analyzes, advises, decides, operates, pattern, aid, spec["plausibility"], "fictional", "scenario_assumption", source, "Scenario authority pattern; human decision authority remains explicit."))
    return pd.DataFrame(rows, columns=AUTHORITY_COLUMNS)


def make_comparison() -> pd.DataFrame:
    rows = []
    for scenario_id, spec in SCENARIO_SPECS.items():
        values = spec["comparison"]
        rows.append((scenario_id, spec["year"], spec["family"], *values))
    return pd.DataFrame(rows, columns=COMPARISON_COLUMNS)


def write_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    assumptions = make_assumptions()
    nodes = make_nodes(assumptions)
    edges = make_edges(nodes, assumptions)
    blind = make_blindspots(assumptions)
    authority = make_authority(assumptions)
    comparison = make_comparison()
    for directory in [SCENARIOS, ANALYSIS, MAPS, FIGURES, REPORTS]:
        directory.mkdir(parents=True, exist_ok=True)
    assumptions.to_csv(ASSUMPTIONS, index=False)
    nodes.to_csv(NODES, index=False)
    edges.to_csv(EDGES, index=False)
    blind.to_csv(BLINDSPOTS, index=False)
    authority.to_csv(AUTHORITY, index=False)
    comparison.to_csv(COMPARISON, index=False)
    return assumptions, nodes, edges, blind, authority, comparison


def draw_box(ax, x: float, y: float, width: float, height: float, label: str, color: str, fontsize: float = 8.0) -> None:
    ax.add_patch(FancyBboxPatch((x, y), width, height, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.3))
    ax.text(x + width / 2, y + height / 2, label, ha="center", va="center", fontsize=fontsize, color="#29343a", wrap=True)


def render_map(nodes: pd.DataFrame, year: int, output: Path) -> None:
    plt.rcParams["svg.hashsalt"] = f"western-basin-phase4c-information-{year}"
    plt.rcParams["svg.fonttype"] = "none"
    fig = plt.figure(figsize=(16, 10), facecolor="#f1eadc")
    map_ax = fig.add_axes([0.045, 0.18, 0.58, 0.75], facecolor="#e9e1ce")
    lens_ax = fig.add_axes([0.045, 0.045, 0.58, 0.095], facecolor="#eee5d3")
    side_ax = fig.add_axes([0.66, 0.045, 0.30, 0.885], facecolor="#eee5d3")
    lens_ax.axis("off")
    side_ax.axis("off")
    lake = gpd.read_file(GPKG, layer="water_lake_erie").cx[-85.5:-82.5, 40.9:42.2]
    watersheds = gpd.read_file(GPKG, layer="water_watersheds_huc8")
    flowlines = gpd.read_file(GPKG, layer="water_flowlines_order3")
    watersheds.plot(ax=map_ax, facecolor="#eadfbd", edgecolor="#a69876", linewidth=0.65, alpha=0.62, zorder=1)
    lake.plot(ax=map_ax, facecolor="#b8d6e0", edgecolor="#7295a2", linewidth=0.7, zorder=0)
    flowlines.plot(ax=map_ax, color="#5f91a6", linewidth=0.62, alpha=0.58, zorder=2)
    base_nodes = pd.read_csv(NETWORKS / "observation_system_nodes.csv", dtype=str).fillna("")
    stations = base_nodes[(base_nodes.node_type == "sensor_or_station") & (base_nodes.latitude != "") & (base_nodes.longitude != "")]
    for _, row in stations.iterrows():
        color = "#a8a92e" if row.domain == "lake_erie_hab" else "#2d7fa6"
        x, y = float(row.longitude), float(row.latitude)
        map_ax.scatter(x, y, s=115, marker="o", color=color, edgecolor="#fff9ed", linewidth=1.4, zorder=6)
        label = "GLOS Toledo crib\n(2026 factual anchor)" if row.node_id.endswith("GLOS-TOLEDO-CRIB") else "USGS 04193500\n(2026 factual anchor)"
        offset = (7, 8) if row.node_id.endswith("GLOS-TOLEDO-CRIB") else (7, -28)
        map_ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", fontsize=7.6, color="#263238", bbox=dict(boxstyle="round,pad=.22", facecolor="#f8f2e5", edgecolor=color, alpha=0.94), zorder=7)
    map_ax.set_xlim(-85.25, -82.72)
    map_ax.set_ylim(41.08, 42.10)
    map_ax.set_xticks([])
    map_ax.set_yticks([])
    suffix = "2050" if year == 2050 else "2075"
    map_ax.set_title(f"MAP {'16' if year == 2050 else '16b'} — INFORMATION / GOVERNANCE FUTURES, {suffix}", loc="left", fontsize=17, weight="bold", color="#17384b", pad=15)
    map_ax.text(0.01, 0.965, "2026 factual observation anchors; future roles and information dependencies remain schematic", transform=map_ax.transAxes, fontsize=9.5, color="#4d5b5c", va="top")
    map_ax.text(0.01, 0.025, "Future information flows are not physical communication routes.", transform=map_ax.transAxes, fontsize=7.8, color="#4f514b")
    map_ax.text(0.99, 0.025, "Toledo intake-coordinate discrepancy remains unresolved.", transform=map_ax.transAxes, ha="right", fontsize=7.8, color="#9a5543")
    map_ax.legend(handles=[Line2D([0], [0], marker="o", color="none", markerfacecolor="#a8a92e", markeredgecolor="white", markersize=9, label="Lake / HAB factual anchor"), Line2D([0], [0], marker="o", color="none", markerfacecolor="#2d7fa6", markeredgecolor="white", markersize=9, label="Maumee factual anchor"), Line2D([0], [0], color="#5f91a6", linewidth=2, label="Existing water geography")], loc="upper left", bbox_to_anchor=(0.01, 0.90), frameon=True, facecolor="#f8f2e5", edgecolor="#a69876", fontsize=7.8)
    lens_ax.text(0.005, 0.82, "FUTURE ROLE LENS", fontsize=9.2, weight="bold", color="#17384b")
    lens = [(0.01, "2026\nFACT", "#527e8b"), (0.18, "PERSISTS", "#5a9b83"), (0.35, "CHANGED\nROLE", "#c37d32"), (0.52, "NEW\nFUNCTION", "#8b65a5"), (0.69, "AUTOMATED\nANALYSIS", "#c56b5c"), (0.86, "HUMAN\nAUTHORITY", "#2d7fa6")]
    for x, label, color in lens:
        draw_box(lens_ax, x, 0.17, 0.12, 0.49, label, color, 6.8)
    for x in [0.135, 0.305, 0.475, 0.645, 0.815]:
        lens_ax.add_patch(FancyArrowPatch((x, 0.415), (x + 0.04, 0.415), arrowstyle="-|>", mutation_scale=10, color="#626969", linewidth=1.0))
    side_ax.text(0.04, 0.975, f"SCENARIO DIVERGENCE — {year}", fontsize=13.2, weight="bold", color="#17384b", va="top")
    side_ax.text(0.04, 0.94, "All three futures retain explicit human decision authority; their information tradeoffs diverge.", fontsize=8.4, color="#4d5b5c", va="top", wrap=True)
    descriptions = {
        2050: [
            ("A  TRUSTED PUBLIC INFRASTRUCTURE", "Interoperable observation, stronger provenance, shared explanations, and broader public access; institutional complexity remains.", "#5a9b83"),
            ("B  FEDERATED RESILIENCE", "Distributed ownership, local processing, selective exchange, redundancy, and graceful degradation; standards fragment.", "#2d7fa6"),
            ("C  HIGH-AUTOMATION / CONTESTED", "Dense sensing, AI-assisted analysis, stronger authentication, and tighter operational boundaries; trust and model dependence rise.", "#c56b5c"),
        ],
        2075: [
            ("A  TRUSTED PUBLIC INFRASTRUCTURE", "Mature interoperable public information infrastructure with traceable models and durable human institutional authority.", "#5a9b83"),
            ("B  FEDERATED RESILIENCE", "Mature local/regional federation with multiple models and fallback paths; autonomy preserves resilience but complicates synthesis.", "#2d7fa6"),
            ("C  HIGH-AUTOMATION / CONTESTED", "Mature automated analysis and bounded operations with concentrated, restricted information and persistent legitimacy disputes.", "#c56b5c"),
        ],
    }[year]
    y = 0.875
    for title, body, color in descriptions:
        side_ax.add_patch(FancyBboxPatch((0.03, y - 0.15), 0.94, 0.14, boxstyle="round,pad=.012", facecolor="#f8f2e5", edgecolor=color, linewidth=1.25))
        side_ax.text(0.06, y - 0.04, title, fontsize=8.5, weight="bold", color=color, va="top")
        side_ax.text(0.06, y - 0.075, textwrap.fill(body, width=48), fontsize=7.35, color="#343b3d", va="top", linespacing=1.18)
        y -= 0.18
    side_ax.text(0.04, 0.145, "BOUNDARIES", fontsize=10.2, weight="bold", color="#17384b")
    boundary = ("2026 baseline objects remain unchanged.\n"
                "Future objects are scenario deltas with explicit assumptions.\n"
                "AI assists analysis/recommendation; human authority remains explicit.\n"
                "Security is modeled only as trust, provenance, availability,\n"
                "authentication, access, continuity, and concentration.\n\n"
                "No offensive security, sensitive topology, or future Phase 4D work.")
    side_ax.text(0.04, 0.12, boundary, fontsize=7.7, color="#3f4645", va="top", linespacing=1.30)
    fig.savefig(output.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
    svg_path = output.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def render_comparison(comparison: pd.DataFrame) -> None:
    plt.rcParams["svg.fonttype"] = "none"
    order = ["low", "moderate", "high"]
    colors = {"low": "#c7ddd4", "moderate": "#e4c77f", "high": "#c56e55"}
    metric_columns = COMPARISON_COLUMNS[3:]
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="#f1eadc")
    values = comparison[metric_columns].to_numpy()
    codes = [[order.index(value) for value in row] for row in values]
    from matplotlib.colors import ListedColormap
    ax.imshow(codes, cmap=ListedColormap([colors[key] for key in order]), vmin=-0.5, vmax=2.5, aspect="auto")
    ax.set_xticks(range(len(metric_columns)), [c.replace("_", " ") for c in metric_columns], rotation=28, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(comparison)), [f"{r.scenario_id} — {r.scenario_family}" for _, r in comparison.iterrows()], fontsize=8.5)
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            ax.text(j, i, value, ha="center", va="center", fontsize=7.7, color="#29343a")
    ax.set_title("INFORMATION / GOVERNANCE SCENARIO COMPARISON — 2050 / 2075", loc="left", fontsize=16, weight="bold", color="#17384b", pad=16)
    fig.text(0.5, 0.93, "Qualitative scenario descriptors; not probabilities, forecasts, or quantitative risk scores.", ha="center", fontsize=9, color="#4d595a")
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=colors[key], edgecolor="none") for key in order]
    ax.legend(handles, order, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(COMPARISON_BASE.with_suffix(".png"), dpi=220, facecolor=fig.get_facecolor())
    svg_path = COMPARISON_BASE.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches="tight", facecolor=fig.get_facecolor(), metadata={"Date": None})
    plt.close(fig)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")


def write_manifest(frames: tuple[pd.DataFrame, ...]) -> dict[str, object]:
    assumptions, nodes, edges, blind, authority, comparison = frames
    artifacts = [ASSUMPTIONS, NODES, EDGES, BLINDSPOTS, AUTHORITY, COMPARISON, COMPARISON_BASE.with_suffix(".png"), COMPARISON_BASE.with_suffix(".svg"), MAP2050.with_suffix(".png"), MAP2050.with_suffix(".svg"), MAP2075.with_suffix(".png"), MAP2075.with_suffix(".svg")]
    manifest = {"phase": "4C", "generated": RETRIEVED_DATE, "status": "scenario_baseline", "counts": {"assumptions": len(assumptions), "scenario_node_states": len(nodes), "scenario_edge_deltas": len(edges), "blindspot_states": len(blind), "authority_rows": len(authority), "comparison_rows": len(comparison)}, "scenario_ids": sorted(nodes.scenario_id.unique().tolist()), "artifacts": {path.relative_to(ROOT).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in artifacts}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    frames = write_tables()
    assumptions, nodes, edges, blind, authority, comparison = frames
    render_comparison(comparison)
    render_map(nodes, 2050, MAP2050)
    render_map(nodes, 2075, MAP2075)
    manifest = write_manifest(frames)
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()
