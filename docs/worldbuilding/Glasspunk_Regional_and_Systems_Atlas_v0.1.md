# Glasspunk Toledo / Cyberglass
## Regional Atlas and Systems Atlas — Working Canon v0.1

**Status:** Working worldbuilding specification  
**Geographic focus:** Toledo / Northwest Ohio / western Lake Erie  
**Primary time slices:** 2026 baseline; 2035; 2050; 2075; optional 2100  
**Primary spatial tools:** Python and R  
**QGIS role:** Optional inspection/cartographic cleanup, not a core dependency

---

## 1. Purpose

This note captures the current regional-boundary logic, setting lore, mapping rules, and systems-atlas concepts developed after the initial Glasspunk Toledo outline.

The five-region map is a **worldbuilding framework over real geography**, not a replacement for physical geography, political boundaries, watersheds, or infrastructure networks.

The working principle is:

> **Real geography first; fictional interpretation second.**

The project should maintain three distinct but interoperable spatial layers:

1. **Real physical and human geography**
   - shoreline
   - islands
   - rivers and tributaries
   - watersheds
   - wetlands
   - roads and rail
   - municipalities
   - industrial and civic infrastructure

2. **Fictional regional identity**
   - five Glasspunk macroregions
   - interpretive, culturally and economically meaningful
   - allowed to overlap or fade at their edges

3. **Cross-cutting systems**
   - hydrology
   - nutrient flows
   - energy
   - freight
   - ecology
   - exposure/public health
   - data/governance
   - historic and Indigenous landscapes

---

# 2. Five-Region Canon v0.1

## Region 1 — Glass City Core

**Identity:**  
Glass, photonics, civic research, governance, culture, public data, design, and high-value knowledge work.

**Real-world anchor:**  
Central Toledo, especially downtown and adjacent dense urban districts.

**Boundary logic:**
- Do not assign all of Toledo to Region 1.
- Keep the core centered on civic, research, commercial, cultural, and glass/photonics functions.
- East Toledo's industrial areas should primarily belong to Region 5.
- Research institutions outside the core can appear as nodes rather than requiring the polygon to expand around them.

**Narrative functions:**
- civic AI
- research commercialization
- data governance
- transparency versus surveillance
- public institutions
- cultural identity
- glass as both infrastructure and metaphor

---

## Region 2 — Maumee River Commons

**Identity:**  
River communities, water governance, restoration, public access, recreation, fisheries, low-impact river commerce, and shared watershed identity.

**Real-world anchors:**  
Toledo riverfront → Maumee → Perrysburg → Waterville → Grand Rapids.

**Boundary logic:**
- Treat as a **linear, sinuous river corridor**, not a broad polygon.
- Follow the actual Maumee River, riparian corridor, floodplain, parks, and historic river/canal landscape.
- Allow overlap or transition with Regions 1, 4, and 5.
- The river should act as a connective spine rather than a hard boundary.

**Regional character:**
- "The river is the main street."
- Old locks, towpaths, flood markers, wooded banks, bridges, parks, river towns, fishing, and restoration coexist with sensing and autonomous infrastructure.
- Technology should be embedded in the landscape rather than visually dominating it.

**Core political and cultural issues:**
- upstream/downstream responsibility
- nutrient loading
- water allocation
- restoration finance
- public access
- flood management
- fisheries
- municipal and watershed governance
- agricultural runoff
- environmental monitoring

**Distinctive logic versus Black Swamp Country:**
- **Maumee River Commons = flowing water, communities, transport, public space, and governance**
- **Black Swamp Country = stored water, soils, drainage, agriculture, wetlands, and ecological memory**

These regions should interlock rather than be collapsed into one.

---

## Region 3 — Lake Erie Energy & Security Coast

**Identity:**  
Energy, freshwater security, grid infrastructure, compute, coastal resilience, defense, strategic infrastructure, and Lake Erie operations.

**Real-world anchors:**
- coastal mainland east of Toledo/Oregon
- Davis-Besse
- Oak Harbor
- Camp Perry
- Port Clinton
- Catawba Peninsula

**Boundary logic:**
- Follow the coastal mainland rather than extending broadly inland.
- Keep East Toledo and most of Oregon's industrial landscape primarily in Region 5.
- The coastal marsh landscape around Davis-Besse should act as an important Region 3/4 interlock zone.
- The Toledo water intake is strategically connected to this system but does not need to fall inside the Region 3 land polygon.

**Islands:**
For v0.1, do not create a sixth island region. Show the islands accurately as real geographic reference features:
- North Bass Island
- Middle Bass Island
- South Bass Island
- Put-in-Bay as the community on South Bass Island
- Kelleys Island
- Catawba Peninsula on the mainland

A future **Island Network** may be added later if the islands develop sufficient distinctive culture, governance, or infrastructure.

**Narrative functions:**
- nuclear power
- future advanced nuclear/fusion scenarios
- water intake security
- Great Lakes autonomous patrols
- grid resilience
- coastal data/compute
- defense and Camp Perry
- wetland–energy conflicts
- freshwater sovereignty

---

## Region 4 — Black Swamp Country

**Identity:**  
Agriculture, drainage, wetlands, restoration, nutrient management, biodiversity, rural technology, local autonomy, and the engineered legacy of the Great Black Swamp.

**Real-world anchors:**
- Genoa
- Millbury
- Luckey
- Pemberville
- Graytown
- surrounding agricultural landscape
- Bowling Green as a southwestern/edge anchor

**Boundary logic:**
- Use historic Great Black Swamp hydrology, low-relief topography, modern drainage, agricultural land use, watersheds, wetlands, and settlement pattern as guides.
- Do not simply copy the historic swamp polygon.
- Do not depict Region 4 as one large ecological preserve.
- Much of the region is a working agricultural landscape built on drained wetland soils.

**Reason for the name change:**
"Black Swamp Preserve" was too narrow and implied a protected ecological reserve.  
**Black Swamp Country** is broader and can contain:
- farms
- towns
- drainage districts
- restored wetlands
- biodiversity preserves
- ditches and tile drains
- precision agriculture
- county fairs
- maker culture
- rural microgrids
- mosquito/insect ecology
- nutrient-management infrastructure

**Worldbuilding principle:**
The Great Black Swamp should be treated as both a **historic place and a living hydrological system**. Its "ghost" remains underneath the modern agricultural and urban landscape through:
- drainage engineering
- clay-rich poorly drained soils
- wetlands
- flood storage
- phosphorus transport
- agricultural production
- mosquito habitat
- restoration potential

---

## Region 5 — Great Lakes Industrial Belt

**Identity:**  
Glass manufacturing heritage, rail, port logistics, refinery/heavy industry, automotive mobility, recycling, robotics, strategic materials, and skilled trades.

**Real-world anchors:**
- East Toledo industrial districts
- Oregon industrial/refinery/waste-management corridor
- Northwood
- Rossford
- Walbridge
- Toledo Assembly Complex / Jeep manufacturing
- port and freight infrastructure

**Boundary logic:**
- Expand Region 5 to include East Toledo's industrial landscape.
- Include the Toledo Assembly Complex and future vehicle-production district.
- Follow real industrial corridors, rail, port, logistics, refinery, landfill/waste, and manufacturing geography.
- The region should look like an **irregular network or corridor**, not a smooth oval.
- A MultiPolygon or branched geometry is acceptable.
- Do not absorb entire residential municipalities merely because one industrial facility is located there.

**Place identities within Region 5:**
- **Rossford:** glass heritage and advanced materials
- **Walbridge:** rail
- **Northwood:** logistics and manufacturing
- **East Toledo:** industrial waterfront and port
- **Oregon:** refinery, energy, landfill/waste, remediation, heavy industry
- **Toledo Assembly Complex:** Jeep legacy, advanced mobility, future robotics/field vehicles

**Narrative functions:**
- labor and automation
- unions and apprenticeship
- circular manufacturing
- autonomous freight
- industrial pollution and remediation
- strategic materials recovery
- glass and composites
- mobility systems
- rail/port dependence

---

# 3. Region Removed from v0.1

## Frontier Arc

The earlier six-region concept included a "Frontier Arc."

This should **not** be used in v0.1.

Most of its strongest themes fit naturally within Black Swamp Country:
- precision agriculture
- rural microgrids
- maker culture
- county fairs
- local autonomy
- farm cooperatives
- drone farming
- anti-centralization politics

Five macroregions are sufficient for the initial atlas and provide stronger geographic grounding.

---

# 4. Geographic Accuracy Rules

AI-generated concept maps are useful for composition and brainstorming but **must not be treated as geographic authority**.

The codified base map should use authoritative geospatial data and verified coordinates.

## Known corrections from concept-map iterations

- **Put-in-Bay is a community on South Bass Island**, not an island name.
- Show **North Bass, Middle Bass, and South Bass** separately.
- **Kelleys Island** lies east of the Bass Islands.
- **Catawba is a peninsula/mainland community**, not an offshore island.
- **Genoa must be placed from authoritative data**; earlier generated concept maps misplaced it.
- **Toledo's main water intake must be located from verified GLOS/IOOS/City of Toledo or equivalent authoritative metadata**, not from concept art.
- **Davis-Besse must use NRC-sourced coordinates/location.**
- **East Toledo should primarily be Region 5 where industrial geography supports it.**
- **Toledo Assembly Complex / Jeep should be explicitly represented in Region 5.**

## Mapping rule

> Never infer real-world coordinates from an AI-generated image, approximate label, or remembered location.

If authoritative sources disagree:
- preserve the disagreement
- document source metadata
- flag for QA
- do not silently choose one

---

# 5. Indigenous History and Continuity

Indigenous history should be integrated before the atlas becomes fixed.

The Maumee Valley was a major Indigenous cultural, transportation, diplomatic, and military corridor.

Historically relevant nations include, depending on time and source:
- Wyandot
- Miami
- Ottawa / Odawa
- Potawatomi
- Shawnee
- Delaware / Lenape
- Chippewa / Ojibwe
- Seneca

Important sites and contexts include:
- Fallen Timbers Battlefield
- Fort Miamis
- Fort Meigs
- Maumee Rapids
- the 1817 treaty at the foot of the Maumee Rapids
- Indigenous villages, travel routes, reservations, land cessions, alliances, and removals when adequately sourced

## Mapping guidance

Do **not** create a single timeless "tribal territory" polygon.

Instead create a **time-enabled Indigenous history layer** with dated, sourced features.

Suggested fields:
- feature_name
- feature_type
- nation_or_nations
- start_year
- end_year
- historical_context
- source
- source_quality
- notes

Contemporary descendant nations should be treated as real present-day institutions with historical and ancestral ties, not as generic fictionalized "Great Lakes tribes."

Possible future Glasspunk relationships:
- archaeological consultation
- treaty interpretation
- cultural resource management
- wetland restoration partnerships
- Great Lakes stewardship
- historical landscape recovery
- joint environmental monitoring

---

# 6. Systems Atlas Concept

The regional map is context. The **systems atlas** is the underlying world model.

Systems should be represented as combinations of:
- flows
- nodes
- stocks
- bottlenecks
- dependencies
- feedbacks
- jurisdictional conflicts

Every system should distinguish:

1. **Real 2026 baseline**
2. **Interpreted system structure**
3. **Fictional future scenarios**

---

# 7. Systems Atlas v0.1

## System 1 — Water / Hydrology / Nutrients

**Priority system.**

Core chain:

```text
PRECIPITATION / LAND
        ↓
AGRICULTURE + URBAN LAND
        ↓
DRAINAGE / TRIBUTARIES
        ↓
MAUMEE RIVER
        ↓
MAUMEE BAY
        ↓
WESTERN LAKE ERIE
        ↓
HARMFUL ALGAL BLOOM / ECOLOGICAL RESPONSE
        ↓
TOLEDO WATER INTAKE
        ↓
WATER TREATMENT
        ↓
CITY / INDUSTRY / POPULATION
```

Key themes:
- nitrogen, phosphorus, carbon
- agricultural and urban sources
- tile drainage and ditches
- tributary delivery
- Maumee River flux
- western Lake Erie HABs
- Toledo drinking-water dependency
- wetlands as nutrient-retention and flood-storage infrastructure
- restoration finance
- autonomous sampling
- adaptive drainage

Initial maps:
1. Water Baseline 2026
2. Maumee Nutrient Network
3. Black Swamp Drainage System
4. Lake Erie HAB–Intake Dependency
5. Water System 2050 Scenario

---

## System 2 — Energy / Grid / Compute

Core relationships:
- generation
- transmission
- substations/distribution
- water treatment
- industry
- compute
- communications
- households

Important anchor:
- Davis-Besse

Potential future systems:
- advanced nuclear
- SMRs
- grid-scale batteries
- hydrogen
- transparent photovoltaic glass
- distributed microgrids
- lake-cooled compute
- fusion as a high-uncertainty scenario
- autonomous grid management

Key dependency concept:

```text
ENERGY
  ↓
WATER TREATMENT
INDUSTRY
COMPUTE
COMMUNICATIONS
```

---

## System 3 — Freight / Industry / Material Flows

Treat the Industrial Belt as a **network**, not merely a polygon.

Core nodes:
- Toledo Assembly Complex
- Rossford
- Walbridge
- Northwood
- East Toledo
- Oregon
- Port of Toledo
- rail and interstate corridors

Commodity categories:
- automotive
- glass/composites
- petroleum/fuels
- metals
- aggregate
- agricultural products
- recycled strategic materials
- general freight

Future themes:
- autonomous freight
- electric/hydrogen heavy transport
- strategic materials recovery
- battery recycling
- circular manufacturing
- robotic rail yards
- autonomous Great Lakes shipping

---

## System 4 — Ecology / Biodiversity

Treat ecology as a dynamic system rather than decorative green space.

Core layers:
- wetlands
- marshes
- riparian habitat
- forest patches
- agricultural matrix
- coastal habitat
- bird migration
- fish habitat
- mayflies and aquatic insects
- invasive species
- protected/restored areas

Potential indicators:
- species richness
- abundance
- habitat connectivity
- wetland area
- pollinator abundance
- mayfly emergence
- fish population indicators
- invasive-species pressure

Future themes:
- biodiversity banking
- ecological credits
- automated wildlife monitoring
- genetic archives
- restoration robotics
- sensor networks

---

## System 5 — Exposure / Environmental Health

Build the future Neighborhood Exposure Score from component layers rather than immediately creating one composite index.

Baseline components may include:

### Air
- PM2.5
- ozone
- diesel/freight
- industrial emissions
- wildfire smoke

### Water
- HAB risk
- flood exposure
- drinking-water dependence

### Land / Legacy
- brownfields
- contamination
- industrial legacy
- landfills/waste

### Climate
- heat
- flooding
- humidity
- severe weather

### Agriculture
- pesticide-use proxies where defensible
- farm dust
- nutrient-intensive land-use context

### Social / Capacity
- census-derived vulnerability
- mitigation resources
- mobility and occupation context

Future progression:
- 2035: dense fixed environmental sensors
- 2040s: wearables
- 2050s: longitudinal exposure records
- 2060s+: exposomics, biomarkers, liability, insurance, occupational records

Long-term model architecture:

```text
PLACE-BASED EXPOSURE
+
MOBILITY
+
OCCUPATION
+
PERSONAL SENSOR DATA
+
BIOMARKERS
=
LONGITUDINAL EXPOSURE MODEL
```

---

## System 6 — Data / Sensors / Governance / Security

Model the information layer that observes and controls the physical world.

Functional networks:
- water quality
- river gauges
- weather
- air quality
- ecology
- transportation
- power
- industrial monitoring
- public health
- remote sensing
- communications

Decision chain:

```text
SENSOR
  ↓
NETWORK
  ↓
DATA PLATFORM
  ↓
MODEL / AI
  ↓
DECISION AUTHORITY
  ↓
PHYSICAL ACTION
```

Key conflicts:
- privacy
- surveillance
- data ownership
- algorithmic authority
- cyberattack
- sensor spoofing
- model disagreement
- environmental justice
- public versus private control
- cross-border governance

---

# 8. Governance / Jurisdiction Overlay

Governance should be a cross-cutting overlay, not a sixth geographic region.

Useful boundaries:
- municipalities
- counties
- Ohio
- Michigan
- Ontario / Canada
- watersheds
- port jurisdiction
- military/federal installations
- environmental authorities
- protected areas

Core worldbuilding tension:

> **Ecological system ≠ political boundary**

This mismatch is a major story generator.

---

# 9. System-of-Systems Model

The long-term atlas should connect all systems through explicit dependencies.

Example:

```text
AGRICULTURE
  ↓
NUTRIENT RUNOFF
  ↓
MAUMEE RIVER
  ↓
HAB
  ↓
TOLEDO INTAKE
  ↓
WATER TREATMENT
  ↓
PUBLIC HEALTH
```

Other dependencies:

```text
ENERGY → WATER TREATMENT
ENERGY → INDUSTRY
ENERGY → COMPUTE
COMPUTE → GRID CONTROL
COMPUTE → HAB FORECASTING
COMPUTE → FREIGHT ROUTING
WETLANDS → NUTRIENT RETENTION
WETLANDS → FLOOD STORAGE
RAIL / PORT → INDUSTRY
INDUSTRY → EMPLOYMENT / EXPOSURE / ENERGY DEMAND
```

Each dependency edge should identify its basis:
- observed
- engineering dependency
- scientific inference
- scenario assumption

---

# 10. Time Model

Use explicit scenario time slices:

- **2026** — real-world baseline
- **2035** — transition
- **2050** — emergence
- **2075** — mature Glasspunk
- **2100** — optional stress / long-view scenario

Do not model every system at high resolution immediately.

Use scenario deltas relative to the 2026 baseline.

---

# 11. Provenance / Canon Model

Every mapped feature should distinguish real, historical, inferred, and fictional status.

Suggested fields:

```text
feature_id
system_id
feature_name
feature_type

reality_status:
  real
  historical
  fictional

canon_status:
  verified
  inferred
  scenario
  experimental

valid_from
valid_to
scenario_year

source_name
source_url_or_identifier
retrieved_date
confidence
notes
```

For graph edges:

```text
from_id
to_id
flow_type
flow_direction
capacity
capacity_units
seasonality
failure_consequence
relationship_basis
scenario_modifier
```

Never invent quantitative values merely to populate a table.

---

# 12. Python and R Roles

## Python

Primary role:
- acquisition
- ETL
- coordinate transforms
- spatial joins
- geometry construction
- network construction
- validation
- GeoPackage / GeoJSON export
- reproducible analytical maps

Suggested libraries:
- GeoPandas
- Shapely
- PyProj
- Pyogrio
- Pandas
- NumPy
- NetworkX
- Rasterio / rioxarray
- Matplotlib

## R

Primary role:
- independent validation
- statistical exploration
- hydrology/ecology analysis
- publication-quality rendering
- testing portability of the shared geospatial store

Suggested libraries:
- sf
- terra
- dplyr
- tidyr
- ggplot2
- igraph
- tmap where useful

Do not unnecessarily duplicate ETL logic in both languages.

---

# 13. Shared Spatial Architecture

Recommended system of record:

```text
data/processed/glasspunk_base.gpkg
```

Suggested repository structure:

```text
data/
  raw/
  interim/
  processed/
    networks/

metadata/
  sources.yml
  region_definitions.yml
  systems.yml
  scenario_assumptions.yml

src/
  python/
    acquire_base_data.py
    build_base_layers.py
    build_regions.py
    validate_geography.py
    systems/
      build_water_system.py
      build_energy_system.py
      build_freight_system.py
      build_ecology_system.py
      build_exposure_system.py
      build_data_system.py
      build_dependency_graph.py

  R/
    validate_regions.R
    systems/
      validate_water_system.R
      validate_system_layers.R
      render_water_system.R
      render_ecology_system.R
      render_exposure_system.R

outputs/
  maps/
    systems/
  figures/
  tables/
  qa/

reports/
  location_qa.md
  systems_qa.md
  systems_sources.md
  systems_assumptions.md
```

---

# 14. Cartographic Language

Use analytical cartography first.

**Polygons:** stocks, zones, catchments  
**Lines:** flows, transport, transmission, waterways  
**Points:** facilities, sensors, control nodes  
**Arrows:** directional flow  
**Line width:** capacity/importance only when supported  
**Dashed lines:** future or scenario connections  
**Transparency:** uncertainty or secondary context  

The five fictional regions should appear only as light contextual boundaries when useful.

Do not apply the sketchbook/atlas aesthetic until geography and scientific QA pass.

---

# 15. Systems Map Design Rule

Every systems map should answer a specific question.

Examples:

### Water
> How does material move from Northwest Ohio land into Lake Erie and back into Toledo's drinking-water system?

### Energy
> What infrastructure must function for Toledo's industrial, water, and compute systems to operate?

### Freight
> How do materials move through the regional industrial economy?

### Ecology
> Where do water, habitat, and seasonal biological processes intersect?

### Exposure
> How do environmental hazards become human exposure?

### Data / Governance
> Who observes the system, who owns the data, and who has authority to act?

---

# 16. Implementation Order

Do not build every system at once.

## Phase 1 — Water / Nutrient System
Build completely and validate.

## Phase 2 — Coarse System-of-Systems Graph
Connect major systems at low resolution.

## Phase 3 — Energy + Freight

## Phase 4 — Ecology + Exposure

## Phase 5 — Data / Governance

After each phase:
- run geographic QA
- inspect maps
- document assumptions
- obtain human review
- only then add complexity

---

# 17. First Systems Deliverable

The first complete systems package should be:

1. `01_water_baseline_2026`
2. `02_maumee_nutrient_network`
3. `03_black_swamp_drainage_system`
4. `04_lake_erie_hab_intake_dependency`
5. `05_water_system_2050_scenario`

Plus:
- water system node table
- water system edge table
- sources report
- assumptions report
- QA report
- one spatial/network dependency diagram

---

# 18. Worldbuilding / Story Integration

Each systems map should expose a potential **story engine**.

For example, a water-system map should reveal where these actors become connected:

- farmer
- drainage district
- wetland operator
- watershed scientist
- autonomous sensor fleet
- HAB forecast model
- intake operator
- water-treatment staff
- public-health authority
- neighborhood residents
- insurer / regulator / court

This is where the atlas becomes more than background scenery.

> The region map describes **where people belong**.  
> The systems map describes **what they depend on**.  
> The stories begin where those dependencies fail, conflict, or change.

---

## 19. Current Working Decision

Freeze the five macroregions as **regional canon v0.1** once the real-geography base map passes QA.

Do not continue adjusting region boundaries merely for aesthetic balance.

The next major development step is the first systems layer:

> **Maumee watershed → Black Swamp drainage/agriculture → nutrient flux → western Lake Erie → HAB → Toledo intake → water treatment → public health**

That chain should become the first computational backbone of the Glasspunk world model.
