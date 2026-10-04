import fieldMap from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1a_geographic_flow_map.png';
import cribSketch from '../../assets/atlas/visual-refresh/crib_blueprint.webp';
import farmScene from '../../assets/phase17d/hf03/hf03_maumee_bio_ag_2075_hero_wide.webp';
import industryScene from '../../assets/phase17d/hf04/hf04_industrial_metabolism_2075_hero_wide.webp';

export type EssayKey = 'field' | 'crib' | 'farm' | 'industry';

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
  boundary: string;
  sources: { label: string; path: string }[];
}

export const essays: Essay[] = [
  {
    key: 'field', number: '01', slug: 'atlas/field-to-lake/', title: 'From Field to Lake',
    subtitle: 'A watershed is a sequence of places, processes, and boundaries.',
    place: 'Maumee watershed → western Lake Erie', status: 'SOURCED GEOGRAPHY / QUALITATIVE PATHWAYS', cover: fieldMap,
    coverAlt: 'Analytical map of pathways from the Maumee watershed toward western Lake Erie.',
    lead: 'Follow a constituent from field and drainage system through the river network to a receiving water. The route is grounded in sourced geography; the diagram keeps uncertain processes and lake response distinct.',
    question: 'What can we trace, and where does the explanation stop?',
    reading: [
      'The geographic map introduces the route. It distinguishes mapped waterways from explanatory connections so that a diagrammatic line does not become an invented channel.',
      'The reading sections move from location to process: movement, transformation, and the receiving-water boundary. Separate tracks prevent different constituents from being treated as one interchangeable load.',
      'A pathway to the lake is not a prediction of harmful algal blooms. The model does not turn every upstream change into a deterministic lake outcome.'
    ],
    boundary: 'Mapped geography and explanatory connections remain distinct. Pathways do not quantify every load or predict the receiving lake’s response.',
    sources: [
      { label: 'Original research plates and source records', path: 'outputs/atlas/prototypes/2_1_from_field_to_lake' },
      { label: 'Study scope and source record', path: 'docs/phase_briefs/phase17a_prototype_2_1_from_field_to_lake.md' },
      { label: 'Validation report', path: 'outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_validation_report.md' }
    ]
  },
  {
    key: 'crib', number: '02', slug: 'atlas/toledo-crib/', title: 'The Toledo Intake Crib',
    subtitle: 'How a real asset might persist through an imagined future.',
    place: 'Lake Erie Energy & Security Coast', status: 'EXISTING STRUCTURE + FUTURE CONCEPT', cover: cribSketch,
    coverAlt: 'Ink blueprint study pairing an approximate older intake crib with an imagined equipment layer.',
    lead: 'A verified physical landmark anchors this study. The current structure is drawn approximately; the 2075 retrofit is a concept layered onto it, not a design proposal for the real water works.',
    question: 'What remains recognizable when a utility structure changes?',
    reading: [
      'The present intake crib is a real offshore asset, with its physical position resolved at 41.699444, −83.259167. Nearby monitoring and legacy dataset coordinates refer to different records.',
      'The reconstruction preserves recognizable form while openly labeling inferred geometry. No measured dimensions were available for the drawing.',
      'The future layer adds sensing, communications, access, and service equipment around an older core. It remains tied to people, power, maintenance, and institutions.'
    ],
    boundary: 'The physical coordinate is verified. The drawing is approximate and non-engineering; the 2075 changes are design concepts. The third-party reference photograph is excluded from this website while its reuse rights remain unconfirmed.',
    sources: [
      { label: 'Original research plates and source records', path: 'outputs/atlas/prototypes/2_3_toledo_crib' },
      { label: 'Coordinate resolution', path: 'reports/toledo_water_intake_crib_coordinate_resolution.md' },
      { label: 'Technical validation record', path: 'outputs/atlas/prototypes/2_3_toledo_crib/2_3_validation_report.md' }
    ]
  },
  {
    key: 'farm', number: '03', slug: 'atlas/farm-2075/', title: 'Farm 2075',
    subtitle: 'A working landscape with water, nutrients, labor, and repair in view.',
    place: 'Maumee River Commons / Black Swamp Country', status: 'SCENARIO AND DESIGN CONCEPT', cover: farmScene,
    coverAlt: 'Related composite farm illustration with open fields, a working cultivation seam and an old drainage gate.',
    lead: 'This is a synthetic Western Basin farm unit, not a real parcel or a forecast. It explores how familiar field agriculture could coexist with water controls, habitat, power equipment, and the access needed to keep them working.',
    question: 'What has to fit together for an adapted farm to keep operating?',
    reading: [
      'Agriculture remains the primary land use. Drainage structures, storage, habitat strips, service roads, and equipment occupy space and require upkeep.',
      'Water and nutrients cross the farm boundary. A management device is not an automatic promise of a particular yield or water-quality result.',
      'Spatial relationships and operating routines answer different questions. The reading sections separate land use, decisions, maintenance and outside dependencies; original research plates remain in the source record.'
    ],
    boundary: 'No real parcel, adoption rate, yield, nutrient-removal efficiency, profitability, or exact future location is claimed. “Black Swamp Country” is an interpretive region; held Great Black Swamp geometry is not used.',
    sources: [
      { label: 'Original research plates and source records', path: 'outputs/atlas/prototypes/4_3_farm_2075' },
      { label: 'Technical validation record', path: 'outputs/atlas/prototypes/4_3_farm_2075/4_3_validation_report.md' },
      { label: 'Scenario background', path: 'reports/phase17b_lived_world_condition_packets.md' }
    ]
  },
  {
    key: 'industry', number: '04', slug: 'atlas/industrial-exchange/', title: 'Industrial Exchange',
    subtitle: 'A more connected district still depends on the outside world.',
    place: 'Great Lakes Industrial Belt', status: 'SCENARIO AND DESIGN CONCEPT', cover: industryScene,
    coverAlt: 'Related composite crane hall with removable equipment, distinct material bays and external freight.',
    lead: 'A speculative 2075 district tests whether industrial exchange can be shown without turning every residual into a resource or every connection into self-sufficiency.',
    question: 'When does a residual become a usable input?',
    reading: [
      'The district sketch places legacy and advanced manufacturing, recovery, water, energy, ecology, freight, and maintenance in one working landscape.',
      'An exchange needs characterization, treatment, standards, quality assurance, a compatible user, and operating agreements. Some residuals still leave the district.',
      'The outside arrows matter: regional fuel, water, materials, freight, product markets, and off-site treatment remain part of the system.'
    ],
    boundary: 'This is a synthetic district. The selected links are qualitative scenarios or sketches, without throughput, capacity, economic viability, compatibility, or continuous-operation claims.',
    sources: [
      { label: 'Original research plates and source records', path: 'outputs/atlas/prototypes/5_3_industrial_exchange' },
      { label: 'Technical validation record', path: 'outputs/atlas/prototypes/5_3_industrial_exchange/5_3_validation_report.md' },
      { label: 'Study methods and findings', path: 'reports/phase17a_prototype_findings_and_production_pattern.md' }
    ]
  }
];
