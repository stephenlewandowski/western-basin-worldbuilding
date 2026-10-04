/** Reader diagrams derived from retained study builders. Positions are editorial,
 * not geography or measurements. Sources and limits travel with every chart. */
export type ConnectionKind = 'flow' | 'possible' | 'information' | 'dependency' | 'context' | 'sequence' | 'membership';
export interface ConnectionNode { id: string; title: string; subtitle: string; detail: string; x: number; y: number }
export interface ConnectionEdge { from: string; to: string; kind: ConnectionKind; label: string; detail?: string }
export interface ConnectionChart { id: string; title: string; intro: string; limit: string; source: string; nodes: ConnectionNode[]; edges: ConnectionEdge[] }
export const connectionKinds: Record<ConnectionKind, string> = {
  flow: 'Physical movement', possible: 'Possible exchange', information: 'Information',
  dependency: 'Operating requirement', context: 'Context / condition', sequence: 'Reading sequence', membership: 'Represented process',
};
const node = (id: string, title: string, subtitle: string, x: number, y: number, detail = subtitle): ConnectionNode => ({ id, title, subtitle, detail, x, y });
const edge = (from: string, to: string, kind: ConnectionKind, label: string, detail?: string): ConnectionEdge => ({ from, to, kind, label, detail });
const fieldSource = 'src/python/atlas/build_spread_2_1_field_to_lake.py';
const farmSource = 'src/python/atlas/build_spread_4_3_farm_2075.py';
const industrySource = 'outputs/atlas/prototypes/5_3_industrial_exchange/5_3_source_manifest.json';
const fieldLimit = 'Generalized relationships, with unknown quantities. Equal line widths give no load, rate, travel time or removal efficiency.';
const farmLimit = 'A synthetic farm, without a real parcel, yield, capture efficiency or demonstrated closure. Water and nutrient movement differ.';
const industryLimit = 'A synthetic district. Connections establish no operating route, throughput, compatibility, environmental benefit or self-sufficiency.';

const processNames = ['Mobilization', 'Transport', 'Retention / transformation', 'Delivery', 'Discharge', 'Receiving-water context'];
const represented = [[1], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 3, 4, 5], [1, 2, 3]];
const tracks = ['Water / carrier', 'Phosphorus', 'Nitrogen', 'Carbon / organic matter', 'Sediment'];

const field: ConnectionChart[] = [
  { id: 'water-route', title: 'From field to lake', intro: 'Follow the generalized water route. Select a place or connection to read its role.', source: fieldSource, limit: fieldLimit,
    nodes: [
      node('field', 'Landscape / field', 'Mobilization near the source', 40, 70),
      node('drainage', 'Drainage / small channel', 'Transport; retention may occur', 390, 70),
      node('tributary', 'Tributary', 'Movement and transformation', 740, 70),
      node('river', 'Maumee River', 'Conveyance toward the nearshore', 1090, 70),
      node('bay', 'Maumee Bay / nearshore', 'Delivery meets receiving water', 1440, 70),
      node('lake', 'Western Lake Erie', 'Physical, chemical, biological context', 1790, 70),
    ], edges: [
      edge('field', 'drainage', 'flow', 'Conveyance', 'Mobilization belongs near this first transition. This is not one measured field event.'),
      edge('drainage', 'tributary', 'flow', 'Conveyance', 'Transport is context across drainage, tributary and river. Retention or transformation may occur at multiple stages.'),
      edge('tributary', 'river', 'flow', 'Conveyance', 'A generalized connection, without a mapped route for one constituent or a measured quantity.'),
      edge('river', 'bay', 'flow', 'Delivery', 'Water and constituents reach a nearshore interface; their rates and fates are separate questions.'),
      edge('bay', 'lake', 'flow', 'Conveyance', 'Lake response depends on receiving-water conditions. Bloom formation is not an inevitable consequence.'),
    ] },
  { id: 'constituent-processes', title: 'Constituents & processes', intro: 'Select a constituent to highlight the process categories represented in the retained source. These connections are membership, not a serial route.', source: 'outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_constituent_process_matrix.csv', limit: 'A missing connection means “not represented in this source,” rather than absence in nature. Shared processes establish no identical rates, forms or fates. Carbon here is organic matter, not a greenhouse-gas inventory.',
    nodes: [
      ...tracks.map((title, i) => node(`track-${i}`, title, i === 0 ? 'Carrier, separate from constituents' : 'Select to inspect represented processes', 50, 45 + i * 185)),
      ...processNames.map((title, i) => node(`process-${i}`, title, 'Source represents this process category', 780, 45 + i * 190)),
    ], edges: represented.flatMap((processes, i) => processes.map(j => edge(`track-${i}`, `process-${j}`, 'membership', 'Represented', 'Process presence is not a measured rate or a claim that this constituent traverses every stage.'))) },
  { id: 'lake-boundary', title: 'At the receiving water', intro: 'Delivery and lake conditions meet. Follow the interaction rather than assuming a direct nutrient-to-bloom result.', source: fieldSource, limit: 'Can contribute to bloom-favorable conditions, without inevitable bloom formation. Harmful algal blooms are receiving-water context, not a transported constituent.',
    nodes: [node('delivery', 'Watershed delivery', 'What arrives from the watershed', 40, 50), node('conditions', 'Receiving-water conditions', 'Physical, chemical and biological', 40, 370), node('interaction', 'Interaction', 'Delivery meets the lake’s conditions', 440, 210), node('favorable', 'Possible bloom-favorable conditions', 'A conditional outcome', 880, 210)],
    edges: [edge('delivery', 'interaction', 'context', 'Meets'), edge('conditions', 'interaction', 'context', 'Shapes context'), edge('interaction', 'favorable', 'possible', 'Can contribute', 'Not inevitable bloom formation; no direct nutrient-to-HAB causal edge is supplied.')] },
];

const laneNames = ['Water', 'Nutrients', 'Energy', 'Ecology', 'Data / control', 'Maintenance'];
const laneInputs = ['Precipitation / supplemental water', 'Nutrient / material inputs', 'Grid / fuel / replacement energy', 'Regional habitat context', 'Data / institutional dependencies', 'Crew / parts / service'];
const laneWork = ['Field → drainage → wetland/storage', 'Soil → crop → retention opportunity', 'Solar/storage → pumps, cultivation, sensing', 'Buffers, perennial strips, wetland', 'Sensor → record → human decision → gate', 'Inspect → repair → replace modules'];
const laneOutputs = ['Downstream water export', 'Products / residuals / nutrient export', 'Grid exchange / residuals', 'Habitat interface / uncertain response', 'Records / decisions / governance', 'Service requests / residuals'];
const laneKinds: ConnectionKind[] = ['flow', 'flow', 'flow', 'context', 'information', 'dependency'];
const farm: ConnectionChart[] = [
  { id: 'farm-water', title: 'Water, reuse & decisions', intro: 'The water route stays open and external water remains necessary. The record, decision and maintenance chain is separate from water movement. Retention or transformation may occur at multiple stages, without complete removal.', source: farmSource, limit: farmLimit,
    nodes: [node('soil', 'Field / soil', 'Annual crops; water as carrier', 40, 50), node('drain', 'Controlled drainage', 'Ditches, gates, managed timing', 390, 50), node('store', 'Wetland / storage', 'Partial reuse; not closure', 740, 50), node('downstream', 'Downstream interface', 'Export remains possible', 1090, 50), node('reuse', 'Supplemental reuse', 'Greenhouse or selected field uses', 560, 380), node('sensor', 'Sensing', 'Water, soil and weather records', 40, 710), node('decision', 'Human-supervised decision', 'Gates, pumps or a work order', 560, 710), node('maintenance', 'Maintenance', 'Inspect, clean and replace', 1090, 710)],
    edges: [edge('soil', 'drain', 'flow', 'Water carrier'), edge('drain', 'store', 'flow', 'Water carrier'), edge('store', 'downstream', 'flow', 'Downstream export'), edge('drain', 'reuse', 'possible', 'Partial water reuse'), edge('store', 'reuse', 'possible', 'Water reuse'), edge('sensor', 'decision', 'information', 'Record / signal'), edge('decision', 'maintenance', 'dependency', 'Work required')]
  },
  { id: 'farm-operations', title: 'The operating network', intro: 'Read across a lane from outside input to work to outside output. Select a middle card to inspect connections between lanes.', source: farmSource, limit: farmLimit,
    nodes: laneNames.flatMap((name, i) => [node(`in-${i}`, laneInputs[i], `${name} · outside input`, 40, 40 + i * 225), node(`work-${i}`, name, laneWork[i], 530, 40 + i * 225), node(`out-${i}`, laneOutputs[i], `${name} · outside output`, 1020, 40 + i * 225)]),
    edges: [...laneNames.flatMap((_, i) => [edge(`in-${i}`, `work-${i}`, laneKinds[i], 'Input / context'), edge(`work-${i}`, `out-${i}`, laneKinds[i], 'Output / interface')]), edge('work-0', 'work-3', 'context', 'Water / habitat'), edge('work-1', 'work-3', 'context', 'Nutrient conditions'), edge('work-4', 'work-0', 'information', 'Signal / record'), edge('work-0', 'work-5', 'dependency', 'Service required')]
  },
];

const industry: ConnectionChart[] = [
  { id: 'exchange-network', title: 'The exchange network', intro: 'Inspect selected connections between district functions and the outside world. Possible exchanges remain conditional.', source: industrySource, limit: industryLimit,
    nodes: [
      node('grid', 'Regional grid / fuel', 'Outside energy input', 40, 40), node('supply', 'Water / chemistry supply', 'Outside operating input', 40, 290), node('materials', 'Regional materials market', 'Outside material input', 40, 540), node('freight', 'Regional freight boundary', 'Incoming and outgoing movement', 40, 790),
      node('energy', 'Energy hub / storage', 'Energy services; outside supply', 440, 40), node('treatment', 'Water / wastewater treatment', 'Suitability and discharge conditions', 440, 290), node('legacy', 'Legacy industrial plant', 'Residual and thermal interfaces', 440, 540), node('logistics', 'Freight / logistics', 'Movement crosses the boundary', 440, 790),
      node('manufacture', 'Manufacturing / remanufacturing', 'Requires qualified inputs', 940, 40), node('greenhouse', 'Greenhouse / controlled environment', 'Possible water and heat interfaces', 940, 290), node('recovery', 'Materials recovery / sorting', 'Qualification is required before use', 940, 540), node('ecology', 'Ecological / stormwater edge', 'Managed discharge / receiving edge', 940, 790),
      node('products', 'Product markets', 'Products and components leave', 1440, 40), node('offsite', 'Off-site treatment / discharge', 'Unsuitable residuals can leave', 1440, 540),
      node('data', 'Data / coordination', 'Records, QA and monitoring', 40, 1130), node('contracts', 'Contracts / standards / QA', 'Institutional requirements', 530, 1130), node('service', 'Service / maintenance', 'Repair and replacement', 1020, 1130), node('core', 'Operating core', 'Selected district functions collectively', 1510, 1130, 'A collective maintenance target from the semantic registry, not another facility or an inferred all-to-all service network.'),
    ], edges: [
      edge('grid', 'energy', 'flow', 'Electricity / energy'), edge('supply', 'treatment', 'flow', 'Water / chemistry'), edge('materials', 'legacy', 'flow', 'Materials / parts'), edge('freight', 'logistics', 'flow', 'Freight movement'),
      edge('energy', 'manufacture', 'flow', 'Energy service'), edge('energy', 'greenhouse', 'flow', 'Energy service'), edge('energy', 'treatment', 'flow', 'Energy service'), edge('legacy', 'recovery', 'flow', 'Residual / waste heat'),
      edge('recovery', 'manufacture', 'possible', 'Qualified material', 'Qualification, specification and a compatible user are required. A residual is not automatically usable.'), edge('legacy', 'greenhouse', 'possible', 'Thermal interface', 'Temperature, timing, distance and compatibility remain unresolved.'), edge('treatment', 'greenhouse', 'possible', 'Treated-water reuse', 'Suitability and operating conditions must be established.'),
      edge('recovery', 'offsite', 'flow', 'Unsuitable residual'), edge('treatment', 'offsite', 'flow', 'Discharge'), edge('treatment', 'ecology', 'flow', 'Managed discharge'), edge('manufacture', 'products', 'flow', 'Products / parts'), edge('logistics', 'freight', 'flow', 'Outbound freight'),
      edge('data', 'legacy', 'information', 'Information / control'), edge('data', 'recovery', 'information', 'Records / QA'), edge('data', 'treatment', 'information', 'Records / monitoring'), edge('contracts', 'manufacture', 'dependency', 'Institutional need'), edge('contracts', 'treatment', 'dependency', 'Institutional need'), edge('service', 'core', 'dependency', 'Repair / replacement', 'The registry defines maintenance toward district functions. No exhaustive per-facility service arrows are inferred.'),
    ] },
  { id: 'residual-qualification', title: 'Before reuse', intro: 'Two possible routes: thermal service and recovered material. Select each step; residuals may leave at every stage.', source: 'src/python/atlas/build_spread_5_3_industrial_exchange.py', limit: industryLimit,
    nodes: [
      node('heat', 'Waste heat / rejected stream', 'Thermal residual', 40, 40), node('heat-check', 'Characterize / treat', 'Temperature, timing, exchange condition', 390, 40), node('heat-recover', 'Recoverable thermal service', 'Only if suitable', 740, 40), node('heat-qualify', 'Qualify the service', 'Distance, timing and quality checks', 1090, 40), node('heat-use', 'Possible new use', 'Greenhouse or process heat', 1440, 40),
      node('residual', 'Sorted / suitable residual', 'Material residual', 40, 410), node('material-check', 'Characterize / reprocess', 'Composition, condition, traceability', 390, 410), node('fraction', 'Recoverable fraction', 'Reprocessed material', 740, 410), node('material-qualify', 'Qualify the material', 'Specification, QA, contract', 1090, 410), node('material-use', 'Possible new input', 'Remanufacturing component', 1440, 410),
      node('exit', 'Residual / outside handling', 'Waste, discharge, off-site treatment', 740, 780, 'Every stage can reject or send material onward for outside handling. No chain necessarily completes.'), node('support', 'Standards, records & upkeep', 'Monitoring, contracts, maintenance', 1440, 780),
    ], edges: [
      ...[['heat','heat-check','heat-recover','heat-qualify','heat-use'],['residual','material-check','fraction','material-qualify','material-use']].flatMap(ids => ids.slice(0,-1).map((id, i) => edge(id, ids[i+1], 'possible', i === 2 ? 'Qualification' : 'If suitable'))),
      ...['heat','heat-check','heat-recover','heat-qualify','heat-use','residual','material-check','fraction','material-qualify','material-use'].map(id => edge(id, 'exit', 'possible', 'May leave', 'Rejection, unsuitable-material handling or off-site treatment remains possible at this stage.')),
      edge('support', 'heat-qualify', 'dependency', 'Requirements'), edge('support', 'material-qualify', 'dependency', 'Requirements'),
    ] },
  { id: 'open-district', title: 'An open district', intro: 'Read the external inputs, outward interfaces and the coordination needed to keep a district working.', source: 'src/python/atlas/build_spread_5_3_industrial_exchange.py', limit: industryLimit,
    nodes: [node('grid', 'Regional grid / fuel', 'Energy enters', 40, 40), node('materials', 'Materials / components', 'Inputs enter', 40, 270), node('water', 'Water / chemistry', 'Operating input', 40, 500), node('freight', 'Freight / logistics', 'Movement across the boundary', 40, 730), node('core', 'Synthetic operating core', 'Industry, recovery, water and energy', 650, 390), node('products', 'Product markets', 'Products leave', 1250, 40), node('residuals', 'Off-site residual treatment', 'Unsuitable material can leave', 1250, 390), node('watershed', 'Watershed / regional infrastructure', 'Outward receiving interfaces', 1250, 730), node('coordination', 'Coordination', 'Contracts, standards, monitoring, QA', 650, 40, 'Operating agreements, regulation/permitting and data sharing are requirements, rather than physical pipes.'), node('maintenance', 'Maintenance / replacement', 'People, parts and stopped time', 650, 730)],
    edges: [edge('grid','core','flow','Energy input'),edge('materials','core','flow','Material input'),edge('water','core','flow','Water / chemistry'),edge('freight','core','flow','Freight'),edge('core','products','flow','Products'),edge('core','residuals','possible','Outside handling'),edge('core','watershed','context','Receiving interface'),edge('coordination','core','dependency','Operating agreements'),edge('maintenance','core','dependency','Repair / replacement')]
  },
];
const crib: ConnectionChart[] = [{ id: 'crib-continuity', title: 'What persists, changes & arrives', intro: 'Read the interpretation from an older structure to altered ways of working and imagined additions. Arrows express a reading sequence, not material flow.', source: 'src/python/atlas/build_spread_2_3_toledo_crib.py', limit: 'Verified physical location: 41.699444, −83.259167. Geometry is approximate; future equipment is speculative, without measured dimensions or performance.',
  nodes: [node('persists','Persists','Site, crib body and lake setting',40,70),node('modified','Modified','Access, monitoring, operating posture',440,70),node('added','Added / imagined','Data, resilience and service layer',840,70)], edges:[edge('persists','modified','sequence','Interpretation'),edge('modified','added','sequence','Interpretation')]
}];

const coast: ConnectionChart[] = [{
  id: 'coast-power-custody', title: 'Power, compute & long obligations',
  intro: 'Follow electricity through the shared grid. Heat and fuel stewardship take separate paths; future supply and reuse remain possibilities.',
  source: 'reports/lake_erie_coast_context_2026-10-04.md',
  limit: 'A qualitative regional reading, not a feeder map, current dispatch, cooling budget or waste shipment. Lines give no quantity. Fusion and heat reuse are conditional; the named sites are not shown sharing one circuit.',
  nodes: [
    node('fission', 'Fission generation', 'Davis-Besse is a present-day anchor', 50, 60, 'Davis-Besse near Oak Harbor supplies the regional grid. Its current license ends in 2037, rather than establishing the same unit in 2075. New generation would need separate decisions.'),
    node('grid', 'Shared regional grid', 'Delivery, agreements and other users', 430, 60, 'The 2026 Vistra–Meta announcement provides a commercial relationship. Grid supply is shared; this chart identifies no private line or verified local data-center route.'),
    node('compute', 'Possible compute halls', 'Electricity becomes work and heat', 810, 60, 'A future load needs an interconnection, reliable service and its own cooling system. Other users still need power; flexible batch work is different from work that cannot wait.'),
    node('heat', 'Waste heat', 'Most consumed electricity ends here', 1190, 60, 'A hypothetical 10 MW facility drawing continuously for 24 hours uses 240 MWh. Heat quantity alone establishes no useful recovery temperature, local recipient or water demand.'),
    node('fusion', 'Possible fusion addition', 'A distinct future installation', 50, 430, 'Conditional on dependable commercial generation, licensing, fuel/materials handling and maintenance. A fusion device is not a converted Davis-Besse reactor.'),
    node('cooling', 'Cooling & water budgets', 'Plant and compute systems differ', 430, 430, 'Davis-Besse already uses a tower with Lake Erie makeup water. Closed-cycle cooling still has water relationships. Compute cooling needs its own budget; no shared loop is established.'),
    node('habitat', 'Lake & habitat conditions', 'Fish, wetland and migration work', 810, 430, 'Intake/discharge, thermal effects and habitat are separate from radiological monitoring. Records and institutional decisions are needed; energy availability guarantees no ecological improvement.'),
    node('heat-use', 'Possible heat customer', 'Temperature, distance, timing matter', 1190, 430, 'A compatible heat user might share a future district, but available heat is not automatically usable heat. Buildings and pipes shown as concepts establish no measured benefit.'),
    node('fuel', 'Spent fission fuel', 'Obligation survives retirement', 50, 800, 'Earlier fission fuel needs continuing management even if a later coast adds fusion. Dry storage is interim custody, not disposal.'),
    node('custody', 'Licensed custody & records', 'Storage, inspection, responsibility', 430, 800, 'Staff, records and authorized transport remain necessary. Recycling can leave residual radioactive waste. Fusion has its own tritium and activated-material obligations.'),
    node('destination', 'Authorized disposition', 'A destination and separate decisions', 810, 800, 'A future lawful transfer or disposal pathway needs licensing and community decisions. This is neither a local repository proposal nor a claim that a destination is available.'),
  ], edges: [
    edge('fission', 'grid', 'flow', 'Grid electricity', 'A general present-day relationship; no amount, dispatch or future unit lifetime is supplied.'),
    edge('fusion', 'grid', 'possible', 'Future grid contribution', 'Technology and local deployment must first become dependable; no forecast is implied.'),
    edge('grid', 'compute', 'possible', 'Future load service', 'An agreement and a physical route are different. No direct generator-to-center edge bypasses the grid.'),
    edge('compute', 'heat', 'flow', 'Energy dissipates', 'This is a physical principle, not a measured regional heat flow.'),
    edge('heat', 'heat-use', 'possible', 'Conditional recovery', 'Requires compatible temperature, distance, equipment and demand.'),
    edge('fission', 'cooling', 'dependency', 'Heat rejection'),
    edge('fusion', 'cooling', 'dependency', 'Design-specific thermal work', 'Requirements depend on the eventual device; no cooling design is chosen.'),
    edge('compute', 'cooling', 'dependency', 'Own cooling requirement'),
    edge('habitat', 'cooling', 'context', 'Ecological conditions matter', 'A relationship to examine, not a measured causal impact or an assurance of protection.'),
    edge('fission', 'fuel', 'flow', 'Spent-fuel obligation'),
    edge('fuel', 'custody', 'dependency', 'Continuing stewardship'),
    edge('fusion', 'custody', 'dependency', 'Separate materials handling', 'Activated materials and tritium do not erase the earlier fission fuel.'),
    edge('custody', 'destination', 'possible', 'Lawful future transfer', 'No destination, route or disposal performance is established.'),
  ],
}];

export const connectionCharts = { field, farm, industry, crib, coast };
