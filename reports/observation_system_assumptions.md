# Phase 4A Observation System Assumptions

Baseline: **2026**

Status vocabulary: **factual_2026**, **public station/network/product/service**,
**public organizational role**, and **documented operational role**. No scenario
records are present.

## Modeling boundary

The observation system answers: how does a limited set of public observations
become an operational or regulatory decision? It is a representative
information-flow model, not an exhaustive sensor inventory, real-time control
model, or data-engineering architecture.

The conceptual chain is:

`physical system → observation / sensor → data product → analysis / forecast → decision organization → operation / response`

Nodes that are networks, data products, forecasts, organizations, or responses
remain schematic and may have blank coordinates. Only public station coordinates
with a source record are spatialized.

## Relationship semantics

- `observes` identifies a documented observation relationship or a physical
  context represented by a public observation network.
- `publishes` identifies a public station, network, or organization exposing a
  data product.
- `feeds` is used only where the source supports an observation/data input to an
  analysis or forecast; the internal data path is not reconstructed.
- `reports_to` identifies a public regulatory reporting relationship at program
  level.
- `used_by` identifies a public product/service and its documented user or
  operator context.
- `supports_decision` identifies an information product or organization that
  supports a decision interface. It does not assert a threshold, automated
  trigger, or causal guarantee.
- `operates` identifies the organization’s documented operational role.

No `triggers` relationship is used. Automated control is not modeled.

## Domain assumptions

### Lake Erie / HAB / drinking water

NOAA GLERL and NOAA NCCOS support the observation-to-forecast portion. GLOS
provides the public Toledo crib station/data product. City of Toledo sources
support continuous water-quality monitoring and treatment operations. The model
uses a qualified forecast-to-Toledo decision edge because public sources support
general drinking-water-manager use, but do not establish a Toledo-specific
external data feed.

The GLOS coordinate is retained as a public observation-station coordinate only.
It must not be treated as the resolved physical Toledo intake coordinate. The
existing intake-coordinate discrepancy remains open.

### Maumee / weather / flood

USGS station 04193500 at Waterville is one representative streamgage. NWIS
provides the public observation product, NOAA NWPS provides the public
water-prediction interface, and NWS provides the public warning/safety
interface. The station-specific internal ingestion path, warning threshold, and
local emergency-management action are outside scope.

### Environmental / regulatory

NPDES and EPA ECHO are modeled at program level. The physical-system node is a
general regulated-facility context, not a named facility or measurement site.
No permit limit, sample value, violation, plume, or enforcement outcome is
created.

### Energy information

EIA and PJM are represented through public statistical and operating-information
interfaces. The energy chain remains high-level and does not include SCADA,
control-center details, private telemetry, cyber architecture, dispatch,
congestion, outage probability, or power flow.

## Status and provenance

Every node and edge has a `source_id`, confidence, and notes field. Source IDs
must resolve to keys in `metadata/sources.yml`. A blank coordinate means the
object is intentionally schematic, not that a location was omitted by mistake.

No 2050/2075 objects, fictional sensor networks, AI decision authority, or
surveillance architecture are included. Compute is not added as a separate
Phase 4A object because the approved baseline can be represented without
expanding the Phase 3 compute layer.
