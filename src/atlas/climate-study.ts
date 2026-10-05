import indicators from '../../data/climate/indicators.json';
import projections from '../../data/climate/local_projections.json';
import { connectionExplorer } from './connection-charts';

const repo = 'https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/';
const base = import.meta.env.BASE_URL;
export const climateIndicators = indicators;
export const localClimateProjections = projections;
const families = [
  { id: 'air', title: 'Air temperature', unit: '°C', scope: 'Toledo Express airport · annual daily midpoint', note: 'Mean of daily high and low temperatures, using complete paired years. This differs from the official NOAA normal and cannot describe a shaded street or a hot loading yard.', rows: indicators.air.map(r => ({year:r.year, value:r.mean_daily_midpoint_c, coverage:`${r.paired_days}/${r.expected_days} paired days`})) },
  { id: 'hot', title: 'Hot days / warm nights', unit: 'days', scope: 'Toledo Express airport · daily high / minimum', note: 'Hot days: daily high at least about 90°F (32.2°C in the source). Warm nights: daily minimum at least about 70°F (21.1°C), a proxy rather than hourly night exposure.', rows: indicators.air.map(r => ({year:r.year, value:r.hot_days, secondary:r.warm_nights, coverage:`${r.paired_days}/${r.expected_days} paired days`})) },
  { id: 'spells', title: 'Hot spells', unit: 'days', scope: 'Toledo Express airport · longest annual spell', note: 'Three or more consecutive days with a high at least about 90°F. This project definition does not include humidity and is not a heat-health warning. Missing days break a spell; incomplete annual summaries are withheld.', rows: indicators.air.map(r => ({year:r.year, value:r.longest_hot_spell_days, coverage:`${r.paired_days}/${r.expected_days} paired days`})) },
  { id: 'lake', title: 'Lake surface temperature', unit: '°C', scope: 'Whole Lake Erie · June–August surface average', note: 'NOAA GLSEA is a satellite-derived surface analysis with smoothing where imagery is missing. A lake average supplies neither a western-basin depth profile nor oxygen, bloom or intake conditions.', rows: indicators.lake_surface.map(r => ({year:r.year, value:r.summer_mean_c, coverage:`${r.summer_days}/92 summer days`})) },
  { id: 'ice', title: 'Ice cover', unit: '%', scope: 'Whole Lake Erie · annual maximum coverage', note: 'The greatest lake-wide extent reached in each ice year. This is not a winter average, duration, ice thickness or a western-basin-only measure. Low-ice and high-ice winters both remain visible.', rows: indicators.ice.map(r => ({year:r.year, value:r.maximum_percent, coverage:'Annual maximum from NOAA GLERL'})) },
];
type Family = typeof families[number];

function figure(family: Family, selected: number): string {
  const valid = family.rows.flatMap(r => r.value === null ? [] : [r.value]);
  const lo = family.unit === '°C' ? Math.floor(Math.min(...valid)-1) : 0;
  const hi = Math.ceil(Math.max(...valid)+1);
  const first = family.rows[0].year, last = family.rows.at(-1)!.year;
  const x = (year:number) => 65 + (year-first)/(last-first)*620;
  const y = (value:number) => 220 - (value-lo)/(hi-lo)*175;
  let pen = false;
  const line = family.rows.map(r => {
    if (r.value === null) { pen = false; return ''; }
    const start = pen ? 'L' : 'M'; pen = true;
    return `${start}${x(r.year).toFixed(1)},${y(r.value).toFixed(1)}`;
  }).join(' ');
  const current = family.rows.find(r => r.year === selected)!;
  return `<svg viewBox="0 0 730 265" role="img" aria-label="${family.scope}, ${first} to ${last}. Values are available in the record table below; gaps mean incomplete records.">
    <text x="65" y="24">${family.unit} · ${family.unit === '°C' ? 'axis does not start at zero' : 'zero-based axis'}</text>
    ${[lo, (lo+hi)/2, hi].map(v => `<line x1="65" y1="${y(v)}" x2="685" y2="${y(v)}" class="climate-grid"/><text x="52" y="${y(v)+5}" text-anchor="end">${v.toFixed(1)}</text>`).join('')}
    <path d="${line}" class="climate-line"/>
    ${current.value === null ? '' : `<circle cx="${x(selected)}" cy="${y(current.value)}" r="7" class="climate-point"/>`}
    <text x="65" y="249">${first}</text><text x="375" y="249" text-anchor="middle">${Math.round((first+last)/2)}</text><text x="685" y="249" text-anchor="end">${last}</text>
  </svg>`;
}

function explorer(family: Family, year: number): string {
  const row = family.rows.find(r => r.year === year)!;
  const fmt = (value: number|null) => value === null ? 'Withheld: incomplete year' : `${Number(value.toFixed(2))} ${family.unit}`;
  const air = indicators.air.find(r => r.year === year);
  const lake = indicators.lake_surface.find(r => r.year === year);
  const extra = family.id === 'hot' ? `<p>Warm-night proxy: <strong>${fmt('secondary' in row ? row.secondary as number|null : null)}</strong></p>` : family.id === 'spells' && air ? `<p>${air.hot_spell_events ?? '—'} events · ${air.hot_spell_days ?? '—'} days in spells · hottest event’s mean high: ${air.hottest_spell_mean_max_c === null ? '—' : air.hottest_spell_mean_max_c+'°C'}</p>` : family.id === 'lake' && lake ? `<p>Annual surface mean: <strong>${lake.annual_mean_c?.toFixed(2) ?? '—'}°C</strong> · ${lake.valid_days} daily values</p>` : '';
  return `<div class="climate-controls"><label for="climate-year">Choose a year</label><select id="climate-year">${family.rows.map(r => `<option value="${r.year}" ${r.year===year?'selected':''}>${r.year}${r.value===null?' · incomplete':''}</option>`).join('')}</select></div>
    <div class="climate-readout" aria-live="polite"><p class="eyebrow">${year} / ${family.scope}</p><h3>${fmt(row.value)}</h3>${extra}<p>${row.coverage}</p></div>
    <figure class="climate-history"><div class="climate-plot-scroll" tabindex="0" role="region" aria-label="Scrollable climate history chart">${figure(family, year)}</div><figcaption>Observed history · Scroll sideways on a small screen, or read the table below. Connected points aid reading; no fitted trend or future line. Missing annual values remain gaps.</figcaption></figure>
    <p class="climate-definition">${family.note}</p>
    <details><summary>Read the values as a table</summary><div class="climate-table-scroll" tabindex="0" role="region" aria-label="Scrollable climate record table"><table><caption>${family.scope}</caption><thead><tr><th scope="col">Year</th><th scope="col">Value (${family.unit})</th>${family.id==='hot'?'<th scope="col">Warm nights</th>':''}<th scope="col">Coverage</th></tr></thead><tbody>${family.rows.map(r=>`<tr><th scope="row">${r.year}</th><td>${r.value === null ? 'Incomplete' : Number(r.value.toFixed(2))}</td>${family.id==='hot'?`<td>${'secondary' in r ? r.secondary ?? 'Incomplete' : '—'}</td>`:''}<td>${r.coverage}</td></tr>`).join('')}</tbody></table></div></details>`;
}

function localProjectionStudy(): string {
  const situations=[
    ['Moderate forcing','A shaded route, cooler room and earlier shift become everyday infrastructure.'],
    ['Higher forcing','More hot days and warm nights put cooling access and work schedules under greater pressure.'],
    ['Very high forcing stress test','Test a hot spell alongside poor air and an electricity peak. Their coincidence is a fictional scene condition, not an inevitable forecast.'],
  ];
  const n=(value:number)=>value.toFixed(1);
  return `<div id="local-projections"><p class="eyebrow">FIRST LOCAL SAMPLE / LUCAS COUNTY, OHIO</p><p class="prose">Three published LOCA2-derived model series now supply a small county-scale comparison: <strong>2061–2090 versus 1991–2020</strong>. Each model gets equal weight in this calculation. The values describe long-term modeled conditions, not the weather in a particular 2075 scene.</p><div class="climate-scenarios">${projections.scenarios.map((scenario,i)=>{
    const s=scenario.summary;
    return `<article><p class="eyebrow">${['SSP2-4.5','SSP3-7.0','SSP5-8.5'][i]} / THREE PUBLISHED SERIES</p><h3>${situations[i][0]}</h3><p><strong>+${n(s.annual_temperature.change_c.mean)}°C</strong> annual warming<br><span class="climate-small">Selected-series change: +${n(s.annual_temperature.change_c.sample_min)} to +${n(s.annual_temperature.change_c.sample_max)}°C</span></p><p><strong>${n(s.hot_days.future.mean)} hot days/year</strong><br><span class="climate-small">Daily highs ≥90°F · modeled county average<br>Baseline: ${n(s.hot_days.baseline.mean)} days/year</span></p><p><strong>${n(s.warm_nights.future.mean)} warm-night proxy days/year</strong><br><span class="climate-small">Daily minima ≥70°F · baseline: ${n(s.warm_nights.baseline.mean)}</span></p><p class="climate-small">${situations[i][1]}</p></article>`;
  }).join('')}</div><details><summary>Inspect the three model series and cooling proxy</summary><div class="climate-table-scroll" role="region" tabindex="0" aria-label="Scrollable local projection sample"><table><caption>Lucas County · 2061–2090 versus modeled 1991–2020 · county-average counts can be fractional</caption><thead><tr><th scope="col">Path / published model</th><th scope="col">Annual warming °C</th><th scope="col">Summer warming °C</th><th scope="col">Future hot days/year</th><th scope="col">Future warm-night proxy/year</th><th scope="col">Cooling degree-days: baseline → future (°F·days, base65°F)</th></tr></thead><tbody>${projections.scenarios.flatMap(s=>s.series.map(r=>`<tr><th scope="row">${s.path}<br>${r.model}</th><td>+${n(r.metrics.annual_temperature.change_c)}</td><td>+${n(r.metrics.summer_temperature.change_c)}</td><td>${n(r.metrics.hot_days.future)}</td><td>${n(r.metrics.warm_nights.future)}</td><td>${n(r.metrics.cooling_degree_days.baseline)} → ${n(r.metrics.cooling_degree_days.future)}</td></tr>`)).join('')}</tbody></table></div></details><p class="climate-boundary">The selected series are IPSL-CM6A-LR, MPI-ESM1-2-HR and MRI-ESM2-0. Their min/max is a <strong>three-series sample range</strong>, not a confidence interval or the full LOCA2 ensemble. These are NOAA/Esri CRIS county spatial summaries: fractional counts are expected. Individual realization IDs and the exact upstream release are not exposed; equal weight here does not establish member balance. The modeled baseline joins 1991–2014 historical data with 2015–2020 from each corresponding pathway. Do not add county changes to the airport normal and call that a station forecast. Cooling degree-days are a climate proxy, not electricity demand. <a href="${repo}reports/glass_city_summer_and_local_climate_2026-10-05.md">Extraction, definitions and limits ↗</a> · <a href="https://cris.climate.gov/pages/about-the-data">CRIS methods ↗</a></p><p class="prose"><a class="text-link" href="${base}atlas/glass-city-2075/#summer-scene">Spend a fictional summer afternoon in Glass City: The Usual Table ↗</a></p></div>`;
}

export function climateStudy(): string {
  return `<div class="climate-page"><section class="essay-hero section-shell"><a class="back-link" href="${base}#essays">← All studies</a><p class="eyebrow accent">OBSERVED HISTORY / FUTURE CONDITIONS</p><h1>Climate &amp;<br><em>Thermal Regime.</em></h1><p class="essay-subtitle">A hotter world changes where people wait, when work happens, and what the lake can tell us.</p><p class="prose">Start with an airport thermometer and the lake’s surface and ice records. Then follow heat through streets, water, electricity and working lives. The observations below are real; the 2075 places are imagined responses.</p><nav class="climate-jump" aria-label="Study sections"><a href="#observed-climate">Observed history</a><a href="#future-climate">2075 scenarios</a><a href="#climate-coupling">Connected systems</a><a href="#climate-places">Places &amp; people</a><a href="#climate-sources">Sources</a></nav></section>
  <section id="observed-climate" class="section-shell climate-section"><div class="section-head"><div><p class="eyebrow">01 / THE RECORD</p><h2>Five readings.<br>Different boundaries.</h2></div><p>Toledo Express’s official 1991–2020 normal is <strong>52.2°F</strong>, with <strong>18.7 days a year at or above 90°F</strong>. Our daily-record warm-night proxy averages <strong>10.2 nights a year</strong>. These describe this station and period, not today’s neighborhood exposure.</p></div><div class="climate-family-buttons" role="group" aria-label="Choose an observed climate indicator">${families.map((f,i)=>`<button type="button" data-climate-family="${f.id}" aria-pressed="${i===0}">${f.title}</button>`).join('')}</div><div id="climate-explorer">${explorer(families[0],2023)}</div><p class="climate-boundary">The retained 2024 and 2025 airport records have missing or rejected days; complete annual air statistics are withheld. Lake and ice records have their own coverage. NOAA’s official normal is a separate adjusted product from our daily midpoint history. <a href="${repo}data/climate/README.md">Definitions and quality flags ↗</a></p></section>
  <section id="future-climate" class="section-shell climate-section"><p class="eyebrow">02 / SCENARIOS, NOT A SINGLE 2075 TEMPERATURE</p><h2>Choose the pressure.<br>Then design the response.</h2><p class="prose">Published Great Lakes regional context gives warming of <strong>3–6°F in 2040–2059</strong> and <strong>6–11°F in 2080–2099</strong>, relative to 1980–1999. Those rounded GLISA ranges are regional context, not Toledo projections or a value to interpolate to 2075. <a href="${indicators.future_scenarios.regional_air_context.url}">Regional synthesis ↗</a></p>${localProjectionStudy()}<p class="climate-boundary">Infrastructure, access and adaptation are separate choices; an SSP does not determine a neighborhood’s services. Parent LOCA2 includes 27 models at approximately 6 km; this county sample uses three published series. Lake scenarios still need a lake model: GLARM-Proj1 is a separate candidate with RCP4.5/RCP8.5, a 2000–2019 baseline and ice biases. RCP and SSP labels are not interchangeable. Street exposure and future lake conditions have not been extracted here.</p></section>
  <section id="climate-coupling" class="section-shell climate-section"><p class="eyebrow">03 / CLIMATE MOVES THROUGH THE WORLD</p><h2>A hot day reaches<br>more than the pavement.</h2><p class="prose">Cooling helps people cope, but also adds load to the grid. Poor outdoor air can change whether a building opens its windows. The lake carries seasonal heat forward. Select the connections below to follow the conditions and decisions.</p></section>${connectionExplorer('climate','climate')}
  <section class="section-shell climate-section"><div class="climate-lake-note"><h2>A shallow lake can still stratify.</h2><p>Western Lake Erie usually mixes repeatedly. In Pigeon Bay, five monitored sites nevertheless recorded vertical temperature differences above 2°C during 45%, 54% and 25% of June–September in 2021–2023. Recorded hypoxic episodes accompanied stratification; many involved colder central-basin water moving in.</p><p>This local study does not establish a basin-wide frequency or prove that warming caused the episodes. Surface temperature cannot supply oxygen at depth. Wind, depth, mixing, incoming water and oxygen demand matter alongside heat. <a href="https://doi.org/10.1016/j.jglr.2025.102596">Kuai &amp; Wells, 2025 ↗</a></p></div></section>
  <section id="climate-places" class="section-shell climate-section"><p class="eyebrow">04 / FIVE PLACES, FIVE ORDINARY RESPONSES</p><h2>Weather becomes<br>something people do.</h2><div class="climate-place-grid">${[
    ['glass-city-2075','Glass City','A missing canopy panel leaves the queue in the sun. Someone moves the stools before the repair begins.','Solar control, glare, shade continuity, warm-night recovery and cooled refuges.'],
    ['lake-erie-energy-security-coast-2075','The working coast','A crew compares a surface reading with a recorder from intake depth. The shaded bench fills at noon.','Variable ice, seasonal heat storage, episodic stratification, intake context and competing cooling loads.'],
    ['maumee-bio-ag-2075','Maumee Bio-Ag','The gate needed clearing after rain. A week later, the same crew is deciding how much water to keep.','Crop heat, evapotranspiration, warm nights, dry intervals, extreme rain and field-work shade.'],
    ['industrial-metabolism-2075','Industrial Metabolism','A discretionary cycle waits until the electricity peak passes; the essential line keeps running.','Process heat, worker exposure, qualified heat recovery, storage, ventilation and task-specific flexibility.'],
    ['basin-reading-hall','The Basin Reading Hall','An airport report, a shaded sensor and a paved loading area seem to give three temperatures. A visitor asks which one describes her shift.','Sensor representativeness, privacy, cooling information and separate conditioning for people, instruments and records.'],
  ].map(([slug,title,story,systems])=>`<article><h3><a href="${base}atlas/${slug}/">${title} ↗</a></h3><p>${story}</p><p class="climate-small">${systems}</p></article>`).join('')}</div><p class="climate-boundary">These small situations are future design seeds, not newly established canon or active encounters. Existing artwork remains unchanged and has no inferred temperature. Future scenes will name their season, thermal condition, clothing needs and one ordinary adaptation.</p></section>
  <section id="climate-sources" class="section-shell boundary-section"><div class="boundary-box"><h2>What is ready / What comes next</h2><p>Observed station, lake-surface and maximum-ice histories are reproducible from small retained NOAA snapshots. Street exposure, humidity-based heat stress, lake-depth profiles, local air quality, cooling access and actual grid peaks need separate observations.</p><p>These indicators do not change Model Lab mathematics or create an empirical watershed forecast. Climate can eventually supply dated boundary conditions; flow, nutrients and lake response still require their own compatible records.</p></div><div class="source-box"><p class="eyebrow">FOLLOW THE EVIDENCE</p><ul>
    <li><a href="${repo}reports/climate_integration_2026-10-05.md">Climatology and data-readiness report ↗</a></li><li><a href="${repo}data/climate/indicators.json">Machine-readable indicators ↗</a></li>
    <li><a href="https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals">NOAA station normals ↗</a> · <a href="https://glisa.umich.edu/climate-data/great-lakes-climatologies/">GLISA climatologies ↗</a></li>
    <li><a href="https://coastwatch.glerl.noaa.gov/satellite-data-products/lake-surface-temperature/">NOAA GLSEA surface analysis ↗</a> · <a href="https://www.glerl.noaa.gov/data/ice/">NOAA lake ice ↗</a></li>
    <li><a href="https://nca2023.globalchange.gov/chapter/5/">NCA5 energy ↗</a> · <a href="https://nca2023.globalchange.gov/chapter/24/">NCA5 Midwest ↗</a></li>
    <li><a href="${indicators.future_scenarios.air_candidate.url}">LOCA2 provenance ↗</a> · <a href="https://gmd.copernicus.org/articles/15/4425/2022/">Coupled lake-model methods ↗</a></li>
    </ul><p class="climate-small">Prototype edition · 5 October 2026. Retained histories end in 2025; this is not a live warning service.</p></div></section></div>`;
}

export function climatePlaceNote(page: string): string {
  const notes: Record<string,string> = {
    'glass-city': 'In The Usual Table, a missing panel puts Leena and Jo’s weekly meeting in the sun. A longer shaded route, a shared room and the shopkeeper’s awning change their afternoon in different ways. Solar control, ventilation, cooled refuges and condensate handling remain design questions; the illustration supplies no cooling-performance measurement.',
    'industrial-metabolism': 'A hotter shift makes process heat, cooled breaks and regional electricity peaks part of the same working day. Future details can distinguish rejected heat from usable recovered heat and show which discretionary cycles can wait. Protective clothing still follows the task; an open freight door does not establish adequate cooling or clean air.',
    'maumee-bio-ag': 'Heat, dry intervals and heavy rain ask different things of the same gate and field. Future scenes can show shaded rest at the service seam, earlier field work, crop heat and water-allocation decisions. Drainage is not automatically drought management, and farm-water choices do not determine a lake bloom.',
    'lake-erie-coast': 'Warm summers and variable ice change the questions a lake crew asks. Surface averages, intake-depth temperatures and oxygen records remain distinct. Onshore cooling loads may compete with compute and industry for capacity; lake cooling and heat rejection require their own checks. Wind and open water do not establish comfortable working conditions.',
    'reading-hall': 'Heat can enter this room as an ordinary question: why does the airport report differ from a shaded neighborhood sensor or a sunlit loading area? The public floor, instruments, compute and preserved records have different conditioning needs. Future shade or cooling access must fit the established public counter, field-return threshold and service routes.',
  };
  return notes[page] ? `<section class="section-shell climate-place-note"><p class="eyebrow">SEASONS &amp; WORK</p><h2>Heat changes the routine.</h2><p>${notes[page]}</p><a class="text-link" href="${base}atlas/climate-thermal-regime/">Explore Climate &amp; Thermal Regime ↗</a><p class="climate-small">Future design direction. Existing images remain seasonal studies without measured thermal conditions.</p></section>` : '';
}

export function mountClimateStudy(): void {
  let family = families[0], year = 2023;
  const container = document.querySelector<HTMLDivElement>('#climate-explorer');
  if (!container) return;
  const revealPoint = () => {
    const viewport = container.querySelector<HTMLElement>('.climate-plot-scroll');
    const point = container.querySelector<SVGCircleElement>('.climate-point');
    if (viewport && point && viewport.scrollWidth > viewport.clientWidth) {
      viewport.scrollLeft += point.getBoundingClientRect().x - viewport.getBoundingClientRect().x - viewport.clientWidth * .7;
    }
  };
  revealPoint();
  document.querySelectorAll<HTMLButtonElement>('[data-climate-family]').forEach(button => {
    button.addEventListener('click', () => {
      family = families.find(f => f.id === button.dataset.climateFamily)!;
      year = Math.max(family.rows[0].year, Math.min(year, family.rows.at(-1)!.year));
      document.querySelectorAll('[data-climate-family]').forEach(b => b.setAttribute('aria-pressed', String(b===button)));
      container.innerHTML = explorer(family,year);
      revealPoint();
    });
  });
  container.addEventListener('change', event => {
    if (!(event.target instanceof HTMLSelectElement)) return;
    year = Number(event.target.value);
    container.innerHTML = explorer(family,year);
    revealPoint();
    container.querySelector<HTMLSelectElement>('#climate-year')?.focus();
  });
}
