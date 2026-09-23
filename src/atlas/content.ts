import fieldMap from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1a_geographic_flow_map.png';
import fieldProcess from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1b_process_schematic.png';
import fieldConstituents from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1c_constituent_pathways.png';
import fieldBoundary from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1d_receiving_water_boundary.png';
import cribStructure from '../../outputs/atlas/prototypes/2_3_toledo_crib/2_3b_current_structure.png';
import cribRetrofit from '../../outputs/atlas/prototypes/2_3_toledo_crib/2_3c_2075_retrofit.png';
import cribPersistence from '../../outputs/atlas/prototypes/2_3_toledo_crib/2_3d_persistence.png';
import farmUnit from '../../outputs/atlas/prototypes/4_3_farm_2075/4_3a_farm_unit_2075.png';
import farmWater from '../../outputs/atlas/prototypes/4_3_farm_2075/4_3b_water_nutrient_management.png';
import farmAssembly from '../../outputs/atlas/prototypes/4_3_farm_2075/4_3c_farm_system_assembly.png';
import farmLogic from '../../outputs/atlas/prototypes/4_3_farm_2075/4_3d_operating_logic.png';
import industryDistrict from '../../outputs/atlas/prototypes/5_3_industrial_exchange/5_3a_industrial_district.png';
import industryNetwork from '../../outputs/atlas/prototypes/5_3_industrial_exchange/5_3b_exchange_network.png';
import industryInput from '../../outputs/atlas/prototypes/5_3_industrial_exchange/5_3c_residual_to_input.png';
import industryOpen from '../../outputs/atlas/prototypes/5_3_industrial_exchange/5_3d_open_system_governance.png';

export type EssayKey = 'field' | 'crib' | 'farm' | 'industry';

export interface Panel {
  title: string;
  image: string;
  alt: string;
  caption: string;
}

export interface Essay {
  key: EssayKey;
  number: string;
  slug: string;
  title: string;
  subtitle: string;
  place: string;
  status: string;
  cover: string;
  coverAlt: string;
  lead: string;
  question: string;
  reading: string[];
  panels: Panel[];
  boundary: string;
  sources: { label: string; path: string }[];
}

export const essays: Essay[] = [
  {
    key: 'field', number: '01', slug: 'atlas/field-to-lake/', title: 'From Field to Lake',
    subtitle: 'A watershed is a sequence of places, processes, and boundaries.',
    place: 'Maumee watershed → western Lake Erie', status: 'EVIDENCE / MODEL', cover: fieldMap,
    coverAlt: 'Analytical map of pathways from the Maumee watershed toward western Lake Erie.',
    lead: 'Follow a constituent from field and drainage system through the river network to a receiving water. The route is grounded in accepted geography; the diagram keeps uncertain processes and lake response distinct.',
    question: 'What can we trace, and where does the explanation stop?',
    reading: [
      'The first panel gives the geographic route. It distinguishes mapped waterways from explanatory connections so that a diagrammatic line does not become an invented channel.',
      'The next panels move from location to process: movement, transformation, and the receiving-water boundary. Separate tracks prevent different constituents from being treated as one interchangeable load.',
      'A pathway to the lake is not a prediction of harmful algal blooms. The accepted model does not turn every upstream change into a deterministic lake outcome.'
    ],
    panels: [
      { title: 'A · Geographic pathway', image: fieldMap, alt: 'Map panel showing the western basin field-to-lake pathway and the Maumee receiving-water interface.', caption: 'Start with real geography; analytical connectors are marked as such.' },
      { title: 'B · Process', image: fieldProcess, alt: 'Process schematic separating watershed transport and transformation stages.', caption: 'The schematic explains relationships rather than asserting a measured flow at every link.' },
      { title: 'C · Constituents', image: fieldConstituents, alt: 'Comparison panel showing distinct constituent pathways.', caption: 'Different constituents have different paths and limits of inference.' },
      { title: 'D · Boundary', image: fieldBoundary, alt: 'Receiving-water boundary diagram for the Maumee Bay and western Lake Erie interface.', caption: 'The model marks the interface at which further claims need separate evidence.' }
    ],
    boundary: 'This prototype is an accepted static analytical set. Its animation experiment was not accepted as an Atlas product because it added little beyond the still figures.',
    sources: [
      { label: 'Prototype brief', path: 'docs/phase_briefs/phase17a_prototype_2_1_from_field_to_lake.md' },
      { label: 'Validation report', path: 'outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_validation_report.md' }
    ]
  },
  {
    key: 'crib', number: '02', slug: 'atlas/toledo-crib/', title: 'The Toledo Intake Crib',
    subtitle: 'How a real asset might persist through an imagined future.',
    place: 'Lake Erie Energy & Security Coast', status: 'EVIDENCE → SKETCH', cover: cribRetrofit,
    coverAlt: 'Approximate drawing of the Toledo intake crib with clearly marked speculative 2075 additions.',
    lead: 'A verified physical landmark anchors this study. The current structure is drawn approximately; the 2075 retrofit is a concept layered onto it, not a design proposal for the real water works.',
    question: 'What remains recognizable when a utility structure changes?',
    reading: [
      'The present intake crib is a real offshore asset, with its physical position resolved at 41.699444, −83.259167. Nearby monitoring and legacy dataset coordinates refer to different records.',
      'The reconstruction preserves recognizable form while openly labeling inferred geometry. No measured dimensions were available for the drawing.',
      'The future layer adds sensing, communications, access, and service equipment around an older core. It remains tied to people, power, maintenance, and institutions.'
    ],
    panels: [
      { title: 'A · Approximate structure', image: cribStructure, alt: 'Approximate axonometric interpretation of the existing Toledo water intake crib.', caption: 'An inferred form, drawn from the reference asset without measured dimensions.' },
      { title: 'B · 2075 retrofit concept', image: cribRetrofit, alt: 'Concept drawing showing small sensor, communication, and service additions to the crib.', caption: 'New equipment accumulates around the existing structure.' },
      { title: 'C · Persistence', image: cribPersistence, alt: 'Three-part diagram labeling what persists, what changes, and what is added.', caption: 'Persists / modified / added is the core reading rule for this future.' }
    ],
    boundary: 'The physical coordinate is verified. The drawing is approximate and non-engineering; the 2075 changes are sketch material. The third-party reference photograph is excluded from this website while its reuse rights remain unconfirmed.',
    sources: [
      { label: 'Coordinate resolution', path: 'reports/toledo_water_intake_crib_coordinate_resolution.md' },
      { label: 'Prototype validation', path: 'outputs/atlas/prototypes/2_3_toledo_crib/2_3_validation_report.md' }
    ]
  },
  {
    key: 'farm', number: '03', slug: 'atlas/farm-2075/', title: 'Farm 2075',
    subtitle: 'A working landscape with water, nutrients, labor, and repair in view.',
    place: 'Maumee River Commons / Black Swamp Country', status: 'SCENARIO / SKETCH', cover: farmUnit,
    coverAlt: 'Synthetic future farm unit with field blocks, drainage, energy, and habitat elements.',
    lead: 'This is a synthetic Western Basin farm unit, not a real parcel or a forecast. It explores how familiar field agriculture could coexist with water controls, habitat, power equipment, and the access needed to keep them working.',
    question: 'What has to fit together for an adapted farm to keep operating?',
    reading: [
      'Agriculture remains the primary land use. Drainage structures, storage, habitat strips, service roads, and equipment occupy space and require upkeep.',
      'Water and nutrients cross the farm boundary. A management device is not an automatic promise of a particular yield or water-quality result.',
      'The blockout tests spatial relationships while the schematics describe routines, external inputs, and governance. Those media answer different questions.'
    ],
    panels: [
      { title: 'A · Farm unit', image: farmUnit, alt: 'Synthetic 2075 farm unit plan showing field agriculture and selected additions.', caption: 'A future farm assembled from recognizable Western Basin functions.' },
      { title: 'B · Water and nutrients', image: farmWater, alt: 'Diagram of selected water and nutrient management interfaces.', caption: 'Controls and flows remain conditional and connected to the watershed.' },
      { title: 'C · System assembly', image: farmAssembly, alt: 'Low fidelity blockout of farm structures, land uses, and access.', caption: 'A simple spatial test makes access and coexistence visible.' },
      { title: 'D · Operating logic', image: farmLogic, alt: 'Diagram of labor, maintenance, inputs, and operating dependencies for the farm.', caption: 'Operations include repair, service, and outside resources.' }
    ],
    boundary: 'No real parcel, adoption rate, yield, nutrient-removal efficiency, profitability, or exact future location is claimed. “Black Swamp Country” is an interpretive region; held Great Black Swamp geometry is not used.',
    sources: [
      { label: 'Prototype validation', path: 'outputs/atlas/prototypes/4_3_farm_2075/4_3_validation_report.md' },
      { label: 'Phase 17B lived-world packets', path: 'reports/phase17b_lived_world_condition_packets.md' }
    ]
  },
  {
    key: 'industry', number: '04', slug: 'atlas/industrial-exchange/', title: 'Industrial Exchange',
    subtitle: 'A more connected district still depends on the outside world.',
    place: 'Great Lakes Industrial Belt', status: 'SCENARIO / SKETCH', cover: industryNetwork,
    coverAlt: 'Selected qualitative connections among future industrial facilities and external systems.',
    lead: 'A speculative 2075 district tests whether industrial exchange can be shown without turning every residual into a resource or every connection into self-sufficiency.',
    question: 'When does a residual become a usable input?',
    reading: [
      'The district sketch places legacy and advanced manufacturing, recovery, water, energy, ecology, freight, and maintenance in one working landscape.',
      'An exchange needs characterization, treatment, standards, quality assurance, a compatible user, and operating agreements. Some residuals still leave the district.',
      'The outside arrows matter: regional fuel, water, materials, freight, product markets, and off-site treatment remain part of the system.'
    ],
    panels: [
      { title: 'A · District', image: industryDistrict, alt: 'Synthetic industrial district plan with old and new manufacturing, utilities, freight, and ecology.', caption: 'A spatial sketch that keeps old infrastructure and service access in place.' },
      { title: 'B · Exchange network', image: industryNetwork, alt: 'Qualitative network connecting district nodes and outside systems.', caption: 'Selected relationships are shown without quantities or performance claims.' },
      { title: 'C · Qualification', image: industryInput, alt: 'Diagram showing stages from residual through characterization and qualification to possible use.', caption: 'Residual ≠ recoverable resource ≠ qualified input.' },
      { title: 'D · Open system', image: industryOpen, alt: 'Governance and maintenance diagram with inputs and outputs crossing the district boundary.', caption: 'Contracts, monitoring, repair, and external systems keep the district connected.' }
    ],
    boundary: 'This is a synthetic district. The selected links are qualitative scenarios or sketches, without throughput, capacity, economic viability, compatibility, or continuous-operation claims.',
    sources: [
      { label: 'Prototype validation', path: 'outputs/atlas/prototypes/5_3_industrial_exchange/5_3_validation_report.md' },
      { label: 'Phase 17A synthesis', path: 'reports/phase17a_prototype_findings_and_production_pattern.md' }
    ]
  }
];
