import data from '../../assets/atlas/region/region_explorer.json';
import watershedPlate from '../../outputs/atlas/prototypes/2_1_from_field_to_lake/2_1a_geographic_flow_map.png';
import geologyPlate from '../../outputs/maps/systems/06_geology_resources_2026.png';
import energyPlate from '../../outputs/maps/systems/11_energy_grid_compute_baseline_2026.png';
import freightPlate from '../../outputs/maps/systems/17_freight_industry_material_flows_2026.png';
import { observedFlowExplorer, mountObservedFlow } from './observed-flow';

const base = import.meta.env.BASE_URL;
const path = (suffix: string) => `${base}${suffix}`;
const source = (suffix: string) => `https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/${suffix}`;

const regions = [
  { id: 'glass', name: 'Glass City Core', hook: 'Shared streets. Civic rooms. The work of repair.', text: 'Toledo’s glass and industrial inheritance meets public life. An old wall, a service rib and a room for asking questions can carry the same city into different futures.', places: 'Toledo and its civic, cultural and glassmaking connections.', question: 'Who gets to pass through when the roof needs repair?', links: [['Glass City 2075', 'atlas/glass-city-2075/'], ['The Reading Hall encounters', 'atlas/basin-reading-hall/#story']] },
  { id: 'river', name: 'Maumee River Commons', hook: 'River towns connected by water and responsibility.', text: 'A river corridor ties upstream communities to Toledo and the lake. Public access, monitoring and ordinary river life share a landscape with consequences that travel downstream.', places: 'The Maumee corridor, including Waterville, Maumee, Perrysburg and Toledo; upstream context remains visible.', question: 'Whose record describes the place you actually use?', links: [['Before the Last Bus', 'atlas/basin-reading-hall/#story'], ['The Return Visit', 'atlas/basin-reading-hall/#return-visit']] },
  { id: 'swamp', name: 'Black Swamp Country', hook: 'Productive fields. Drainage gates. Wetland memory.', text: 'Working soils, drainage, farms and remaining wetland relationships shape this regional identity. It is a place of cultivation and maintenance, with an ecological history that has not disappeared.', places: 'Northwest Ohio’s agricultural and drainage landscape. This identity is not a surveyed historical swamp boundary.', question: 'What happens when the old gate will not close?', links: [['Maumee Bio-Ag 2075', 'atlas/maumee-bio-ag-2075/'], ['A possible farm', 'atlas/farm-2075/']] },
  { id: 'coast', name: 'Energy & Security Coast', hook: 'Exposed workplaces. Infrastructure. Lake weather.', text: 'Mainland towns, marshes, energy infrastructure and offshore water connections meet the lake. Maintenance and access matter when a workplace is exposed to wind and water.', places: 'The mainland coast east of Toledo/Oregon toward Port Clinton and the Catawba Peninsula. The offshore crib is a connected landmark.', question: 'What has to keep working when the weather closes in?', links: [['Lake Erie Coast 2075', 'atlas/lake-erie-energy-security-coast-2075/'], ['The intake crib study', 'atlas/toledo-crib/']] },
  { id: 'industry', name: 'Great Lakes Industrial Belt', hook: 'Materials. Skilled trades. A decision before reuse.', text: 'Industrial yards, rail, port interfaces and processing sites form connected workplaces. Regional character follows corridors and nodes; it does not turn whole residential municipalities into a factory zone.', places: 'East Toledo, Oregon, Rossford, Walbridge and Northwood connections, with materials interfaces farther inland.', question: 'Who decides whether something can be used again?', links: [['Industrial Metabolism 2075', 'atlas/industrial-metabolism-2075/'], ['Industrial Exchange', 'atlas/industrial-exchange/']] },
];

const plates = [
  { id: 'watershed', title: 'Water: from field to lake', image: watershedPlate, alt: 'Retained geographic watershed plate with physical channels and separately distinguished analytical connections', text: 'Read the river network and its watershed context. This earlier research plate distinguishes analytical connections from physical channels; line width gives no nutrient quantity. Its Toledo label uses a water-treatment anchor; the interactive map uses a municipality representative.', source: 'outputs/atlas/prototypes/2_1_from_field_to_lake/2_1_source_manifest.json', study: 'atlas/field-to-lake/', studyLabel: 'Follow the pathway study', question: 'Where can water and its passengers move?' },
  { id: 'ground', title: 'Ground: geology and materials', image: geologyPlate, alt: 'Retained geology and materials map with carbonate bedrock, Woodville and Genoa lime processing, Elmore processing and Luckey remediation', text: 'Carbonate bedrock, lime processing and industrial legacies give the landscape material character. Bedrock is generalized at 1:500,000; Elmore is processing, not a local beryllium mine. Luckey is a cleanup legacy.', source: 'reports/materials_system_sources.md', study: 'atlas/maumee-bio-ag-2075/', studyLabel: 'Enter an imagined agricultural landscape', question: 'What is local, and what has to arrive from elsewhere?' },
  { id: 'energy', title: 'Coast: energy, grid and compute', image: energyPlate, alt: 'Retained regional energy map showing selected generation, grid context, storage, loads and a planned compute project', text: 'A retained 2026 baseline brings infrastructure into view. Capacity and planned projects do not establish actual delivery, present operating status or a route powering an imagined building.', source: 'reports/energy_system_sources.md', study: 'atlas/lake-erie-energy-security-coast-2075/', studyLabel: 'Enter the imagined working coast', question: 'Which dependencies sit behind an illuminated room?' },
  { id: 'freight', title: 'Movement: freight and industry', image: freightPlate, alt: 'Retained freight map of public rail and road corridors, a port address anchor and selected materials sites', text: 'Port, rail and road context explains the region’s working connections. A line on this map does not establish a shipment, customer contract, schedule or volume.', source: 'reports/freight_system_sources.md', study: 'atlas/industrial-metabolism-2075/', studyLabel: 'Enter the imagined crane hall', question: 'What crosses the boundary of a working place?' },
];

function regionCard(id: string): string {
  const region = regions.find(item => item.id === id)!;
  return `<p class="eyebrow accent">OVERLAPPING REGIONAL IDENTITY</p><h2>${region.name}</h2><p class="region-hook">${region.hook}</p><p>${region.text}</p><p class="region-place">${region.places}</p><blockquote>${region.question}</blockquote><p class="eyebrow">IMAGINED FUTURES INSPIRED BY THIS REGION</p><div class="region-links">${region.links.map(([title, route]) => `<a href="${path(route)}">${title} ↗</a>`).join('')}</div><small>These are composite scenes and design studies, without exact future-site pins.</small>`;
}

function landmarkCard(id: string): string {
  const place = data.landmarks.find(item => item.id === id)!;
  const kind = place.kind === 'municipality' ? 'Municipality representative' : place.kind === 'gauge' ? 'Observation station' : place.kind === 'structure' ? 'Physical structure' : 'Retained facility / asset anchor';
  const file = place.kind === 'municipality' ? 'data/processed/analysis/population_settlement_nodes.csv' : place.kind === 'gauge' ? 'outputs/model_lab/observations/waterville_observation_manifest.json' : place.kind === 'energy' ? 'data/processed/networks/energy_system_nodes.csv' : place.kind === 'material' ? 'data/processed/networks/materials_system_nodes.csv' : place.source_id;
  return `<span class="eyebrow">${kind}</span><h3>${place.title}</h3><p>${place.note}</p><a href="${source(file)}">Location source ↗</a>${id === 'waterville' ? ` · <a href="#river-record">Inspect the daily flow ↓</a>` : id === 'crib' ? ` · <a href="${path('atlas/toledo-crib/')}">Open the structure study ↗</a>` : ''}`;
}

export function regionExplorer(): string {
  return `<section class="plain-hero section-shell map-heading"><p class="eyebrow accent">MAPS / A REAL PLACE, POSSIBLE FUTURES</p><h1>Know the ground.<br><em>Find a story.</em></h1><p>Start with the real basin: its river towns, working coast and industrial connections. Choose a regional reading, follow a landmark, then enter an imagined place in 2075.</p><nav class="map-jump-links" aria-label="On this page"><a href="#basin">Map &amp; regional character ↓</a><a href="#earlier-maps">Earlier research maps ↓</a><a href="#river-record">A real river record ↓</a></nav></section>
    <section id="basin" class="section-shell region-explorer" aria-label="Basin map and regional readings">
      <div class="region-controls" aria-label="Choose a regional reading">${regions.map(region => `<button type="button" data-region="${region.id}" aria-pressed="${region.id === 'river'}">${region.name}</button>`).join('')}</div><a class="region-read-link" href="#region-detail">Read this region ↓</a>
      <div class="region-layout"><div class="map-column"><div class="map-toolbar"><span class="eyebrow">REAL GEOGRAPHY</span><div aria-label="Map view"><button type="button" data-map-view="basin" aria-pressed="true">Whole basin</button><button type="button" data-map-view="coast" aria-pressed="false">Toledo &amp; coast</button></div></div>
        <svg class="basin-map" viewBox="0 0 ${data.width} ${data.height}" role="group" aria-labelledby="map-title map-description"><title id="map-title">Maumee watershed and western Lake Erie</title><desc id="map-description">Seven watershed areas, selected physical waterways and eleven sourced landmarks. Use the buttons below for the same landmarks. Regional readings highlight associated places without territorial boundaries.</desc><rect x="-2000" y="-2000" width="6000" height="6000" fill="#e9e2cf"/>
        <g class="map-basins">${data.basins.map(basin => `<path d="${basin.path}" fill-rule="evenodd"><title>${basin.name} watershed ${basin.id}</title></path>`).join('')}</g><path class="map-lake" d="${data.lake}" fill-rule="evenodd"/><path class="map-rivers" d="${data.rivers}"/><text class="map-water-label" x="785" y="180" text-anchor="middle">LAKE ERIE</text>
        <g class="map-landmarks">${data.landmarks.map(place => `<g role="button" tabindex="0" data-landmark="${place.id}" aria-label="Inspect ${place.title}" aria-pressed="${place.id === 'toledo'}" transform="translate(${place.x} ${place.y})"><circle class="map-hit" r="14"/><circle class="map-dot ${place.kind === 'gauge' ? 'is-gauge' : ''}" r="${place.kind === 'gauge' ? 7 : 5}"/><title>${place.title}</title></g>`).join('')}</g><text id="map-selected-label" class="map-selected-label" x="${data.landmarks[0].x + 15}" y="${data.landmarks[0].y - 15}">Toledo</text><g class="map-orientation"><path d="M72 116V65M62 80L72 65L82 80"/><text x="72" y="51" text-anchor="middle">N</text></g></svg>
        <p class="map-key"><span class="key-watershed">▰</span> Watershed areas <span class="key-river">━</span> Selected physical waterways <span class="key-landmark">●</span> Real anchors <span class="key-gauge">◉</span> Observation station</p>
        <p class="map-note">Select a point or use the place buttons. This is a generalized drawing; channel widths carry no flow quantity. Smaller channels and much tile drainage are omitted.</p>
        <div class="landmark-controls" aria-label="Inspect a real landmark">${data.landmarks.map(place => `<button type="button" data-place="${place.id}" aria-pressed="${place.id === 'toledo'}">${place.title}</button>`).join('')}</div><div class="landmark-detail" id="landmark-detail" aria-live="polite">${landmarkCard('toledo')}</div>
      </div><aside id="region-detail" class="region-detail" aria-live="polite">${regionCard('river')}</aside></div>
      <details class="map-source-note"><summary>Map sources and geographic limits</summary><p>Retained USGS hydrography and watershed boundaries, Census municipality representatives, source-specific facility anchors and the resolved Coast Guard intake crib location. The local drawing is generalized from latitude/longitude; it supplies no surveyed dimensions. Only physical waterways with stream order at least 5 are drawn. Analytical network connectors and inferred routing relations are excluded.</p><p>The five regional identities overlap conceptually. Black Swamp Country supplies no historical swamp polygon; the candidate boundary remains unresolved. Selecting a region changes the reading and highlighted anchors, rather than the geography.</p><p><a href="${source('assets/atlas/region/source_manifest.json')}">Render derivative and source hashes ↗</a> · <a href="${path('methods/')}">Methods and credits</a></p></details>
    </section>
    ${observedFlowExplorer()}
    <section id="earlier-maps" class="section-shell map-library"><div class="section-head"><div><p class="eyebrow accent">THE RESEARCH MAP COLLECTION</p><h2>One landscape.<br><em>Different questions.</em></h2></div><p>Earlier maps bring the ground, infrastructure and movement back into the Atlas. These retained research plates keep their original labels and dated limits. Open a plate to read it at full size.</p></div><div class="plate-controls" aria-label="Choose a research map">${plates.map((plate, i) => `<button type="button" data-plate="${plate.id}" aria-pressed="${i === 0}">${plate.title}</button>`).join('')}</div><div id="plate-detail">${plateCard('watershed')}</div></section>
    <section class="section-shell map-next"><p class="eyebrow">THREE WAYS TO KEEP EXPLORING</p><div class="reading-order-grid"><article><h3>Enter a place.</h3><p>Four illustrated futures and a developing Reading Hall turn regional constraints into workplaces, devices and ordinary lives.</p><a href="${path('#futurescapes')}">Choose a futurescape ↗</a></article><article><h3>Follow a person.</h3><p>A report, a picnic channel and a bus to catch: the Reading Hall encounters make the limits of a record matter to someone.</p><a href="${path('atlas/basin-reading-hall/#story')}">Play Before the Last Bus ↗</a></article><article><h3>Inspect an assumption.</h3><p>Model Lab’s saved synthetic cases test routing and conservation. Its local explorer keeps unresolved quantities visible in the ledger.</p><a href="${path('#model-lab')}">Find the Model Lab ↗</a></article></div></section>`;
}

function plateCard(id: string): string {
  const plate = plates.find(item => item.id === id)!;
  return `<div class="plate-reading"><h3>${plate.question}</h3><p>${plate.text}</p><p><a href="${source(plate.source)}">Research source record ↗</a> · <a href="${path(plate.study)}">${plate.studyLabel} ↗</a></p></div><figure><a href="${plate.image}" target="_blank" rel="noopener" aria-label="Open ${plate.title} full size"><img src="${plate.image}" alt="${plate.alt}" loading="lazy" /></a><figcaption>Retained research plate · Original labeling and source notes preserved. Open image for full size ↗</figcaption></figure>`;
}

export function mountRegionExplorer(): void {
  let selectedRegion = 'river';
  const setView = (view: string) => {
    document.querySelector('.basin-map')!.setAttribute('viewBox', view === 'coast' ? '530 145 450 378' : `0 0 ${data.width} ${data.height}`);
    document.querySelectorAll<HTMLButtonElement>('[data-map-view]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.mapView === view)));
  };
  const selectPlace = (id: string) => {
    const place = data.landmarks.find(item => item.id === id)!;
    if (document.querySelector('[data-map-view="coast"][aria-pressed="true"]') && (place.x < 530 || place.y < 145 || place.x > 980 || place.y > 523)) setView('basin');
    document.querySelectorAll<HTMLElement>('[data-place], [data-landmark]').forEach(button => button.setAttribute('aria-pressed', String((button.dataset.place ?? button.dataset.landmark) === id)));
    document.querySelector('#landmark-detail')!.innerHTML = landmarkCard(id);
    const label = document.querySelector('#map-selected-label')!;
    label.textContent = place.title;
    label.setAttribute('x', String(place.x + 15));
    label.setAttribute('y', String(place.y - 15));
  };
  const selectRegion = (id: string) => {
    selectedRegion = id;
    document.querySelectorAll<HTMLButtonElement>('[data-region]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.region === id)));
    document.querySelector('#region-detail')!.innerHTML = regionCard(id);
    for (const place of data.landmarks) {
      document.querySelector<SVGGElement>(`[data-landmark="${place.id}"]`)!.classList.toggle('region-associated', place.regions.includes(selectedRegion));
    }
    if (!data.landmarks.find(place => place.id === document.querySelector('[data-place][aria-pressed="true"]')?.getAttribute('data-place'))?.regions.includes(id)) {
      selectPlace(data.landmarks.find(place => place.regions.includes(id))!.id);
    }
  };
  document.querySelectorAll<HTMLButtonElement>('[data-region]').forEach(button => button.addEventListener('click', () => selectRegion(button.dataset.region!)));
  document.querySelectorAll<HTMLElement>('[data-place], [data-landmark]').forEach(button => {
    const select = () => selectPlace((button.dataset.place ?? button.dataset.landmark)!);
    button.addEventListener('click', select);
    if (button.dataset.landmark) button.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(); }
    });
  });
  document.querySelectorAll<HTMLButtonElement>('[data-map-view]').forEach(button => button.addEventListener('click', () => {
    setView(button.dataset.mapView!);
    // Keep the selected label visible when changing focus to the coast.
    if (button.dataset.mapView === 'coast') {
      const current = data.landmarks.find(place => place.id === document.querySelector('[data-place][aria-pressed="true"]')?.getAttribute('data-place'))!;
      if (current.x < 530 || current.y < 145 || current.x > 980 || current.y > 523) selectPlace('toledo');
    }
  }));
  document.querySelectorAll<HTMLButtonElement>('[data-plate]').forEach(button => button.addEventListener('click', () => {
    document.querySelector('#plate-detail')!.innerHTML = plateCard(button.dataset.plate!);
    document.querySelectorAll<HTMLButtonElement>('[data-plate]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
  }));
  const requested = new URLSearchParams(location.search).get('region');
  selectRegion(regions.some(region => region.id === requested) ? requested! : selectedRegion);
  mountObservedFlow();
}
