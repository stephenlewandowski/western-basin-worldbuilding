# Information Governance Findings

Phase 4B is a factual 2026 information-dependency layer over the accepted and
validated Phase 4A observation baseline. It contains 20 qualitative information
dependencies, 10 evidence-qualified blind spots, four authority rows, and a 4 ×
7 ordinal matrix. These are analytical descriptors, not quantitative risk scores.

# HAB / Drinking Water

The Lake Erie chain combines a public GLOS Toledo crib time series, NOAA GLERL
observation and research context, NOAA NCCOS HAB forecasting, and City of Toledo
water-quality and treatment roles. The strongest documented dependency is the
use of integrated observation data in forecast products and the City's documented
continuous water-quality monitoring/treatment function.

The exact external forecast-to-Toledo operational handoff is not established by
the public sources used here. The GLOS station coordinate is a public observation
coordinate, not a resolution of the physical Toledo intake discrepancy. The
chain therefore depends on multiple information types while retaining point
coverage, update-cadence, and decision-threshold uncertainty.

# Hydrology / Flood

The representative Lower Maumee chain is USGS 04193500 at Waterville → NWIS
real-time data → NOAA NWPS → NWS flood information/warnings → public-safety
response. The river observation and public warning interfaces are distinct from
local response authority. The model does not assign a county emergency manager,
evacuation action, or station-specific forecast ingestion path.

The principal blind spots are point coverage, undocumented common update timing,
and product-level rather than station-level forecast provenance. These are
information gaps, not evidence that the warning system failed.

# Environmental / Regulatory

The environmental chain is program-level: regulated monitoring/reporting → EPA
ECHO public data → EPA/state-authorized NPDES oversight → compliance, permitting,
or reporting response. ECHO is treated as a public data product rather than a
raw continuous sensor stream. The authority matrix preserves the distinction
between regulated-entity observation/reporting, public-data publication, and
regulatory decision authority.

Periodic or self-reported information is not interpreted as regulatory failure.
The unresolved questions concern the public view of underlying records and the
specific state/federal jurisdiction for a named case, which this phase does not
model.

# Energy Information

The energy chain uses EIA public electricity statistics as factual context and
PJM public operating information as the operator-facing public interface. PJM's
public role supports a high-level operations/planning coordination endpoint, but
internal workflows and private operational detail are not represented.

The information layer does not reconstruct SCADA, control networks, dispatch,
private telemetry, credentials, cyber architecture, outage probability, or
specific control-center decisions. Public visibility is therefore intentionally
high-level and incomplete.

# Cross-System Information Dependencies

Across all four domains, information availability is not equivalent to decision
authority. A public product can be timely but point-limited, broad but model-
dependent, or visible without revealing the internal handoff that turns it into
a decision. Phase 4B makes those distinctions explicit instead of collapsing
observation, analysis, authority, and response into one node.

The main cross-system concentrations are:

- dependence on public products whose internal update and handoff details are not
  fully documented;
- dependence on forecasts or regulatory products that summarize multiple inputs;
- separation between data stewardship/publication and operational authority; and
- incomplete public visibility into operator or facility-level information.

# Governance Boundaries

- GLOS/NOAA and USGS provide observation or data services; they do not thereby
  acquire Toledo municipal treatment authority or local flood-response authority.
- NOAA forecast and NWS warning roles are distinct from local public-safety
  decisions.
- EPA/state-authorized NPDES authorities have program roles that are not
  interchangeable with a specific facility or local regulator.
- EIA is a public statistical source, while PJM is the represented regional
  operator; neither is treated as a complete view of all utility operations.
- Public access does not imply operational completeness, and partially public
  reporting does not imply wrongdoing.

# Blind Spots and Uncertainty

The short register records spatial coverage, status, model, temporal-latency,
organizational-handoff, public-data, and jurisdiction blind spots. The most
important are the unresolved Toledo intake coordinate, the single-station
representative limits of the hydrology chain, the absence of station-specific
forecast provenance, the lack of a Toledo-specific external HAB forecast handoff,
and the program-level nature of environmental and energy public data.

No blind spot is converted into a vulnerability claim. No consequence is
quantified as probability, delay, casualty, economic loss, or outage.

# Public versus Operational Information

Phase 4A and 4B can document public station records, forecast products, warning
pages, regulatory data interfaces, and public operator data. They cannot infer
private telemetry, internal control logic, exact dispatch decisions, local
emergency protocols, or unreported facility records from those public products.
That boundary is part of the model rather than a missing technical layer to be
filled by assumption.

# Data Gaps

Useful next evidence would include current GLOS station status and cadence,
independent intake-coordinate reconciliation, documented station-to-forecast
provenance, basin-level gauge/rainfall aggregation methods, a defined facility
and permit for regulatory analysis, and publicly releasable explanations of
operator-data timing and scope. None is required to assert that an actual system
failure occurred.

# Implications for Phase 4C

No Phase 4C work is begun here. Any later scenario phase would require separate
approval and would need to preserve the factual 2026 observation, dependency,
and authority layers. It must not convert these blind spots into invented cyber,
AI, privacy, surveillance, or future-infrastructure claims.

## Worldbuilding Implications

The factual layer supports later interpretive themes such as information
asymmetry, environmental sensing as public infrastructure, contested forecasts,
model dependence, public transparency versus operational confidentiality,
jurisdictional fragmentation, sensor redundancy, institutional memory, and
decision-making under uncertainty. These are worldbuilding prompts, not claims
about current institutional failure or hidden control.
