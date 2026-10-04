import data from '../../assets/atlas/region/region_explorer.json';

export const flowDays = data.flow;
export const cubicFeetToCubicMetres = (flow: number): number => flow * 0.028316846592;
export const flowDayIndex = (date: string): number => flowDays.findIndex(day => day.date === date);
export const highFlowIndex = flowDays.reduce((best, day, i) => day.flow > flowDays[best].flow ? i : best, 0);
export const lowFlowIndex = flowDays.reduce((best, day, i) => day.flow < flowDays[best].flow ? i : best, 0);
const base = import.meta.env.BASE_URL;
const repo = 'https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/';
const x = (index: number) => 68 + index / (flowDays.length - 1) * 712;
const y = (flow: number) => 265 - flow / 70000 * 235;
const whole = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 });
const converted = new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 });
const dateLabel = (date: string) => new Date(`${date}T12:00:00Z`).toLocaleDateString('en-US', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });

function readout(index: number): string {
  const day = flowDays[index];
  return `<p class="eyebrow">${dateLabel(day.date)} / DAILY MEAN</p><p class="flow-number">${whole.format(day.flow)} <span>ft³/s</span></p><p class="flow-converted">≈ ${converted.format(cubicFeetToCubicMetres(day.flow))} m³/s</p><p class="flow-status"><strong>${day.approval === 'approved' ? 'Approved' : 'Provisional'} in the retained snapshot</strong>${day.estimated ? ' · Estimated value' : ''}<br><small>Original qualifiers: ${day.qualifiers}</small></p>`;
}

export function observedFlowExplorer(): string {
  const line = flowDays.map((day, index) => `${index === 0 ? 'M' : 'L'}${x(index).toFixed(2)},${y(day.flow).toFixed(2)}`).join('');
  return `<section id="river-record" class="section-shell river-record"><div class="section-head"><div><p class="eyebrow accent">OBSERVATION / USGS WATERVILLE</p><h2>A day on<br><em>the Maumee.</em></h2></div><p>How much water passed this gauge? Choose a day from the complete 2025 record. These are historical USGS daily means, kept with their source flags; they give the map a measured point of reference.</p></div><div class="flow-layout"><div><details class="flow-trend"><summary>Show the year’s flow curve</summary><svg class="flow-chart" viewBox="0 0 820 310" role="img" aria-labelledby="flow-title flow-description"><title id="flow-title">Waterville daily mean discharge, 2025</title><desc id="flow-description">365 daily values on a linear scale from zero to seventy thousand cubic feet per second. The highest daily mean in this year is April 4. The selected day and its exact value are provided below.</desc>${[0, 35000, 70000].map(flow => `<path class="flow-grid" d="M68 ${y(flow)}H780"/><text x="59" y="${y(flow) + 4}" text-anchor="end">${whole.format(flow)}</text>`).join('')}<text x="68" y="16">DAILY MEAN · ft³/s</text><path class="flow-line" d="${line}"/>${flowDays.map((day, index) => day.estimated ? `<path class="flow-estimated" d="M${x(index)} ${y(day.flow) - 4}l-4 7h8Z"/>` : day.approval === 'provisional' ? `<circle class="flow-provisional" cx="${x(index)}" cy="${y(day.flow)}" r="2.4"/>` : '').join('')}<path id="flow-cursor" class="flow-cursor" d="M${x(highFlowIndex)} 25V265"/><circle id="flow-selected" class="flow-selected" cx="${x(highFlowIndex)}" cy="${y(flowDays[highFlowIndex].flow)}" r="5"/>${[['Jan', 0], ['Apr', 90], ['Jul', 181], ['Oct', 273], ['Dec', 334]].map(([month, index]) => `<text x="${x(Number(index))}" y="292" text-anchor="middle">${month}</text>`).join('')}</svg><p class="flow-chart-key">Solid line: daily means · ○ Provisional · ▲ Estimated · Flags describe the September 2026 download.</p></details><label class="flow-slider-label" for="flow-day">Choose a day in 2025</label><input id="flow-day" type="range" min="0" max="364" value="${highFlowIndex}" aria-valuetext="${dateLabel(flowDays[highFlowIndex].date)}"/><div class="flow-day-controls"><button type="button" id="flow-previous">← Previous day</button><label>Date <input id="flow-date" type="date" min="2025-01-01" max="2025-12-31" value="${flowDays[highFlowIndex].date}" /></label><button type="button" id="flow-next">Next day →</button></div><div class="flow-presets" aria-label="Visit an example day"><button type="button" data-flow-day="${highFlowIndex}">Highest daily mean</button><button type="button" data-flow-day="${lowFlowIndex}">Lowest daily mean</button><button type="button" data-flow-day="0">An estimated day</button><button type="button" data-flow-day="${flowDayIndex('2025-11-19')}">A provisional day</button></div></div><div id="flow-readout" class="flow-readout" aria-live="polite" aria-atomic="true">${readout(highFlowIndex)}</div></div>
    <div class="science-bridge"><div><p class="eyebrow">ONE SCIENTIFIC PRINCIPLE</p><h3>Water passing.<br>What is it carrying?</h3><p>Discharge is water volume passing a point per unit time. Nutrient mass transported depends on both the water movement and its changing concentration.</p><p class="science-equation">Transported mass = ∫ C(t) Q(t) dt</p><p>C is concentration, Q is discharge; add their product over time. Compatible concentration measurements are needed before a nitrogen or phosphorus load can be estimated. This flow record alone does not tell Renata whether her picnic channel is safe.</p><p><a href="https://pubs.usgs.gov/of/2007/1080/of-2007-1080/methods.html">USGS nutrient-flux methods ↗</a> · <a href="${base}atlas/basin-reading-hall/#story">Meet Renata at the Reading Hall ↗</a></p></div><div><p class="eyebrow">HOW THE NUMBER REACHES THE SCREEN</p><p>Streamgages record water level; site-specific measurement relationships help compute discharge. Daily means summarize a day, rather than its instantaneous peaks. The unit conversion changes the scale, not the information: 1 ft³/s = 0.028316846592 m³/s.</p><p>One station’s retained record is separate from Model Lab’s synthetic routing cases. It supplies no mapped flood extent, lake-wide nutrient load or 2075 forecast. Estimated values may also be approved; neither flag is an uncertainty interval.</p><p><a href="https://www.usgs.gov/mission-areas/water-resources/science/streamgaging-basics">USGS streamgaging basics ↗</a> · <a href="${base}#model-lab">Inspect the synthetic Model Lab ↗</a></p></div></div>
    <details class="map-source-note"><summary>Observation source, flags and download</summary><p>USGS station 04193500, Maumee River at Waterville, Ohio. Parameter 00060; daily mean statistic 00003. The complete January–December 2025 series has 365 days: 322 approved, 43 provisional and 13 estimated (overlapping approval). Snapshot retrieved 3 September 2026. “Highest” and “lowest” refer only to daily means in this year, rather than all-time records. Converted values are rounded to three significant digits.</p><p><a href="https://waterdata.usgs.gov/monitoring-location/04193500/">USGS station ↗</a> · <a href="${repo}outputs/model_lab/observations/waterville_daily_flow_2025.csv">Original daily values and flags ↗</a> · <a href="${repo}outputs/model_lab/observations/waterville_observation_manifest.json">Observation manifest ↗</a> · <a href="${base}methods/#observed-flow">Observation methods and limits</a></p></details></section>`;
}

export function mountObservedFlow(): void {
  const slider = document.querySelector<HTMLInputElement>('#flow-day')!;
  const date = document.querySelector<HTMLInputElement>('#flow-date')!;
  const previous = document.querySelector<HTMLButtonElement>('#flow-previous')!;
  const next = document.querySelector<HTMLButtonElement>('#flow-next')!;
  const select = (index: number) => {
    if (!Number.isInteger(index) || index < 0 || index >= flowDays.length) return;
    const day = flowDays[index];
    slider.value = String(index);
    slider.setAttribute('aria-valuetext', `${dateLabel(day.date)}: ${whole.format(day.flow)} cubic feet per second`);
    date.value = day.date;
    previous.disabled = index === 0;
    next.disabled = index === flowDays.length - 1;
    document.querySelector('#flow-readout')!.innerHTML = readout(index);
    document.querySelector('#flow-cursor')!.setAttribute('d', `M${x(index)} 25V265`);
    document.querySelector('#flow-selected')!.setAttribute('cx', String(x(index)));
    document.querySelector('#flow-selected')!.setAttribute('cy', String(y(day.flow)));
  };
  slider.addEventListener('input', () => select(Number(slider.value)));
  date.addEventListener('change', () => { const index = flowDayIndex(date.value); select(index === -1 ? Number(slider.value) : index); });
  previous.addEventListener('click', () => select(Number(slider.value) - 1));
  next.addEventListener('click', () => select(Number(slider.value) + 1));
  document.querySelectorAll<HTMLButtonElement>('[data-flow-day]').forEach(button => button.addEventListener('click', () => select(Number(button.dataset.flowDay))));
  select(highFlowIndex);
}
