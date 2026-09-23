import './style.css';
import { essays, type Essay, type EssayKey } from './content';

const root = document.querySelector<HTMLDivElement>('#app');
if (!root) throw new Error('Atlas root is missing');

const base = import.meta.env.BASE_URL;
const path = (suffix = '') => `${base}${suffix}`;
const repo = 'https://github.com/stephenlewandowski/western-basin-worldbuilding';
const source = (file: string) => `${repo}/blob/main/${file}`;
const page = document.body.dataset.page ?? 'home';

function nav(active: string): string {
  const item = (label: string, href: string, key: string) =>
    `<a href="${path(href)}" ${active === key ? 'aria-current="page"' : ''}>${label}</a>`;
  return `<a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="header-inner">
      <a class="brand" href="${path()}"><span class="brand-mark" aria-hidden="true">WB<span>•</span></span><span>WESTERN BASIN<br><strong>WORLDBUILDING</strong></span></a>
      <nav class="top-nav" aria-label="Main navigation">
        ${item('Home', '', 'home')}${item('Atlas', '#essays', 'atlas')}${item('Methods & credits', 'methods/', 'methods')}${item('Roadmap', 'roadmap/', 'roadmap')}
      </nav>
    </div></header>`;
}

function footer(): string {
  return `<footer class="site-footer"><div class="footer-inner">
    <div><span class="eyebrow">Western Basin Worldbuilding</span><p>An illustrated research and speculative worldbuilding project rooted in Toledo, the Maumee watershed, and western Lake Erie.</p></div>
    <div class="footer-links"><a href="${path('methods/')}">Methods & credits</a><a href="${path('roadmap/')}">Roadmap</a><a href="${repo}">Research repository ↗</a><a href="${path('game/')}">Vesper Station game ↗</a></div>
    <p class="footer-bottom">Atlas Preview v0.1 · Editorial status: September 2026 · Real geography first; fictional interpretation second.</p>
  </div></footer>`;
}

function layout(content: string, active: string): string {
  return `${nav(active)}<main id="main">${content}</main>${footer()}`;
}

function card(essay: Essay): string {
  return `<a class="essay-card" href="${path(essay.slug)}">
    <div class="card-image"><img src="${essay.cover}" alt="${essay.coverAlt}" loading="lazy" /></div>
    <div class="card-content"><span class="eyebrow">${essay.number} / ${essay.status}</span><h3>${essay.title}</h3><p>${essay.subtitle}</p><span class="card-link">Read the visual essay <span aria-hidden="true">↗</span></span></div>
  </a>`;
}

function home(): string {
  return layout(`<section class="hero"><div class="hero-inner">
    <div class="hero-copy"><p class="eyebrow accent">AN ILLUSTRATED REGIONAL & SYSTEMS ATLAS · PREVIEW v0.1</p>
      <h1>The future<br>has a <em>watershed.</em></h1>
      <p class="hero-deck">A grounded look at the places and systems around Toledo and western Lake Erie—and at the lives that might grow from them.</p>
      <div class="hero-actions"><a class="button button-primary" href="#essays">Explore four studies <span aria-hidden="true">↓</span></a><a class="text-link" href="${path('methods/')}">How to read this atlas <span aria-hidden="true">↗</span></a></div>
    </div>
    <div class="hero-art"><div class="hero-art-frame"><img src="${essays[0].cover}" alt="A geographic pathway map from the Maumee watershed toward western Lake Erie" /><span class="art-label">01 / FROM FIELD TO LAKE</span></div><div class="coordinate">41° N / 83° W<br>WESTERN LAKE ERIE BASIN</div></div>
  </div></section>
  <section class="intro-section section-shell"><div class="section-label"><span class="rule-number">I</span> THE IDEA</div>
    <div class="intro-grid"><h2>Start with the place.<br><em>Follow the connections.</em></h2><div><p>Toledo sits where the Maumee River, Lake Erie, agriculture, drinking water, industry, freight, energy, ecology, and public institutions meet. Those connections shape what can plausibly happen next.</p><p>This project moves from a sourced model of the real basin to possible futures and an inhabited world. Each step is labeled so observation, scenario, and invention remain clear. <em>The Glass Basin</em> is a working name for that future-facing Atlas; its final title remains open.</p></div></div>
    <div class="process-line" aria-label="Project sequence"><span>REAL PLACE</span><b>→</b><span>CONNECTED SYSTEMS</span><b>→</b><span>POSSIBLE FUTURES</span><b>→</b><span>LIVED WORLD</span></div>
  </section>
  <section id="essays" class="essays-section section-shell"><div class="section-head"><div><div class="section-label"><span class="rule-number">II</span> THE ATLAS</div><h2>Four ways into<br>the basin.</h2></div><p>These accepted Phase 17A prototypes are working components for a larger Atlas. Open a study to see its figures at full size, its evidence status, and its limits.</p></div>
    <div class="card-grid">${essays.map(card).join('')}</div>
  </section>
  <section class="status-band"><div class="section-shell status-grid"><div><p class="eyebrow accent">CURRENT WORK / SEPTEMBER 2026</p><h2>From model<br>to lived world.</h2></div><div><p>The scientific foundation is accepted and frozen through Phase 16. Phase 17A’s four visual prototypes are accepted. Phase 17B’s future-world translation is complete as development material. Phase 17C is active, with role and story seeds accepted for development.</p><a class="button button-outline" href="${path('roadmap/')}">See the roadmap <span aria-hidden="true">↗</span></a></div></div></section>
  <section class="section-shell approach-section"><div class="section-label"><span class="rule-number">III</span> READING KEY</div><h2>What kind of claim<br>am I looking at?</h2><div class="key-grid"><div><span class="key-letter evidence">E</span><h3>Evidence / model</h3><p>Sourced or reproducibly derived information about the real basin.</p></div><div><span class="key-letter scenario">S</span><h3>Scenario</h3><p>A plausible future condition used for exploration, never a forecast.</p></div><div><span class="key-letter canon">C</span><h3>Canon</h3><p>A deliberate fictional choice. This preview makes no new canon.</p></div><div><span class="key-letter sketch">K</span><h3>Sketch</h3><p>Provisional visual or narrative development.</p></div></div><a class="text-link" href="${path('methods/')}">Read the methods and credits <span aria-hidden="true">↗</span></a></section>`, 'home');
}

function essayView(essay: Essay): string {
  const index = essays.findIndex((item) => item.key === essay.key);
  const next = essays[(index + 1) % essays.length];
  return layout(`<div class="essay-page"><section class="essay-hero section-shell">
    <a class="back-link" href="${path()}#essays">← All visual essays</a>
    <div class="essay-header-grid"><div><p class="eyebrow accent">ATLAS STUDY ${essay.number} / ${essay.place.toUpperCase()}</p><h1>${essay.title}</h1><p class="essay-subtitle">${essay.subtitle}</p><div class="status-pill">${essay.status}</div></div><p class="essay-lead">${essay.lead}</p></div>
    </section><div class="section-shell"><figure class="cover-figure"><a href="${essay.cover}" target="_blank" rel="noopener" aria-label="Open the lead figure full size"><img src="${essay.cover}" alt="${essay.coverAlt}" /></a><figcaption>Lead figure · Open image for full size <span aria-hidden="true">↗</span></figcaption></figure></div>
    <section class="section-shell reading-section"><div class="reading-side"><span class="eyebrow">THE READER'S QUESTION</span><h2>${essay.question}</h2></div><div class="prose">${essay.reading.map((paragraph) => `<p>${paragraph}</p>`).join('')}</div></section>
    <section class="section-shell panel-section"><div class="section-head"><div><div class="section-label"><span class="rule-number">${essay.number}</span> VISUAL SEQUENCE</div><h2>Read the panels.</h2></div><p>Click a figure to inspect its labels at full size. The sequence moves from place or form to the relationships that organize it.</p></div>
      <div class="panel-grid">${essay.panels.map((panel) => `<figure class="panel"><a href="${panel.image}" target="_blank" rel="noopener" aria-label="Open ${panel.title} full size"><img src="${panel.image}" alt="${panel.alt}" loading="lazy" /></a><figcaption><strong>${panel.title}</strong><span>${panel.caption}</span></figcaption></figure>`).join('')}</div>
    </section><section class="section-shell boundary-section"><div class="boundary-box"><span class="eyebrow">INTERPRETIVE BOUNDARY</span><p>${essay.boundary}</p></div><div class="source-box"><span class="eyebrow">FOLLOW THE WORK</span><ul>${essay.sources.map(({ label, path: file }) => `<li><a href="${source(file)}">${label} ↗</a></li>`).join('')}</ul><small>Source links lead to the project repository. Access depends on repository visibility.</small></div></section>
    <a class="next-essay" href="${path(next.slug)}"><span class="eyebrow">NEXT STUDY / ${next.number}</span><strong>${next.title} <span aria-hidden="true">↗</span></strong></a>
  </div>`, 'atlas');
}

function methods(): string {
  return layout(`<section class="plain-hero section-shell"><p class="eyebrow accent">THE WORK BEHIND THE IMAGES</p><h1>Methods<br><em>& credits.</em></h1><p>This preview is an editorial selection from a larger research repository. Its figures show what the project can support and where interpretation begins.</p></section>
  <section class="section-shell method-block"><div class="section-label"><span class="rule-number">01</span> FOUR CLAIM TYPES</div><div class="method-grid"><div><h2>Keep the layers legible.</h2><p>Every figure carries an evidence status and a medium. A map, schematic, model, or concept drawing answers a different question; its appearance does not change the status of the underlying claim.</p></div><div class="definition-list"><div><b class="evidence">E</b><span><strong>Evidence / model</strong>Sourced observation or reproducibly derived current-system information.</span></div><div><b class="scenario">S</b><span><strong>Scenario</strong>A qualitative future exploration. It is not a prediction or a probability.</span></div><div><b class="canon">C</b><span><strong>Canon</strong>A chosen fact of the fictional setting. No new canon is created in this preview.</span></div><div><b class="sketch">K</b><span><strong>Sketch</strong>Provisional design, character, or narrative material.</span></div></div></div></section>
  <section class="section-shell method-block"><div class="section-label"><span class="rule-number">02</span> SOURCE TO FIGURE</div><div class="method-grid"><div><h2>Research remains traceable.</h2><p>The accepted science packages use public-source records, builders, validators, manifests, reviews, and freeze records. The Phase 17A illustrations add reader-facing interpretation while keeping their source gates and limitations documented.</p></div><div class="prose"><p>The research spans water, geology, energy, freight, ecology, health, climate, governance, population, technology, and their dependencies. Phase 14 organizes these into 13 Atlas system families; Phase 16 tests bounded stress pathways.</p><p>Qualitative lines and colors do not encode measured load, probability, performance, or severity unless a figure explicitly says so. A scenario diagram does not certify a real deployment or future outcome.</p><p><a href="${source('metadata/sources.yml')}">Source registry ↗</a> · <a href="${source('reports/README.md')}">Validation and report index ↗</a> · <a href="${source('docs/canon_status.md')}">Canon status ↗</a></p></div></div></section>
  <section class="section-shell method-block"><div class="section-label"><span class="rule-number">03</span> CREDITS & RIGHTS</div><div class="method-grid"><div><h2>Built from shared records,<br>drawn for this Atlas.</h2><p>Original site design, editorial text, and prototype drawings are part of Western Basin Worldbuilding. Source data and third-party imagery retain their own terms and attribution.</p></div><div class="prose"><p>Research sources documented in the repository include <a href="https://www.usgs.gov/3d-hydrography-program/access-3dhp-data-products">USGS hydrography ↗</a>, <a href="https://www.epa.gov/tmdl/epas-approval-ohios-maumee-watershed-nutrient-total-maximum-daily-load">US EPA's Maumee nutrient TMDL ↗</a>, <a href="https://coastalscience.noaa.gov/science-areas/habs/hab-forecasts/lake-erie/">NOAA's Lake Erie HAB work ↗</a>, and <a href="https://toledo.oh.gov/departments/public-works/water/water-treatment">City of Toledo water treatment ↗</a>, alongside other public records. Individual figure manifests and source reports identify the inputs used for each prototype.</p><p>The current Toledo intake crib coordinate uses the U.S. Coast Guard Light List, corroborating NOAA/NDBC observation evidence, and aerial review. The third-party source photograph is omitted from this web build because its reuse rights are not confirmed. Great Black Swamp held geometry and its reference image are also excluded.</p><p>The repository's MIT license covers its original code and documentation; it does not relicense third-party data or imagery. See the <a href="${source('docs/references/DATA_AND_ASSET_LICENSING.md')}">data and asset licensing notes ↗</a> and each essay’s source links for detail.</p></div></div></section>
  <section class="section-shell end-cta"><p class="eyebrow">CONTINUE EXPLORING</p><h2>Four studies. One connected basin.</h2><a class="button button-primary" href="${path()}#essays">Browse the Atlas <span aria-hidden="true">↗</span></a></section>`, 'methods');
}

function roadmap(): string {
  return layout(`<section class="plain-hero section-shell"><p class="eyebrow accent">PROJECT ROADMAP / REVIEWED SEPTEMBER 2026</p><h1>From a basin model<br>to an <em>inhabited world.</em></h1><p>This page tracks the current work. Earlier phase briefs preserve their at-the-time wording; the status record and canon register carry the latest disposition.</p></section>
  <section class="section-shell roadmap-section"><div class="section-label"><span class="rule-number">01</span> WHERE WE ARE</div><div class="timeline">
    <div class="timeline-item"><span class="timeline-status done">FROZEN</span><div><h2>Phases 1–16 <small>Scientific & systems foundation</small></h2><p>Environmental, infrastructure, population, health, governance, technology, shared Atlas ontology, and bounded cross-system stress tests are complete, accepted, and frozen.</p></div></div>
    <div class="timeline-item"><span class="timeline-status done">ACCEPTED</span><div><h2>Phase 17A <small>Atlas prototype pattern</small></h2><p>Four static visual sets are accepted as analytical and concept components. Visual Grammar v0.3 is accepted for use; final Atlas styling and page composition are still open.</p></div></div>
    <div class="timeline-item"><span class="timeline-status done">ACCEPTED</span><div><h2>Phase 17B <small>Initial future-world translation</small></h2><p>Fifteen seed units and seven lived-world condition packets are complete and accepted for development. Their future conditions remain scenario or sketch material, without canon promotion.</p></div></div>
    <div class="timeline-item"><span class="timeline-status active">ACTIVE</span><div><h2>Phase 17C <small>Character & narrative architecture</small></h2><p>Ten unnamed roles, nine relationships, and six narrative-thread seeds are accepted for development. No protagonist set, names, biographies, scenes, or new canon have been selected.</p></div></div>
    <div class="timeline-item"><span class="timeline-status future">NEXT</span><div><h2>Later Atlas work <small>Editorial selection & production</small></h2><p>Shape a coherent illustrated reading sequence, decide which places and viewpoints to develop, and establish final visual and narrative conventions. Phase 17D has not begun.</p></div></div>
  </div></section>
  <section class="status-band"><div class="section-shell status-grid"><div><p class="eyebrow accent">OPEN BOUNDARIES</p><h2>What remains<br>undecided.</h2></div><div><p>The Great Black Swamp geometry remains on hold and noncanonical. The crib's physical location is resolved, but the future retrofit is speculative. Phase 17B and 17C material has not been promoted to fictional canon. This preview is a curated publication layer, not a new science or canon decision.</p><a class="button button-outline" href="${source('PROJECT_STATUS.md')}">Detailed status record ↗</a></div></div></section>
  <section class="section-shell end-cta"><p class="eyebrow">START WITH THE WORK</p><h2>See the accepted visual studies.</h2><a class="button button-primary" href="${path()}#essays">Explore the Atlas <span aria-hidden="true">↗</span></a></section>`, 'roadmap');
}

const essay = essays.find((item) => item.key === page as EssayKey);
root.innerHTML = essay ? essayView(essay) : page === 'methods' ? methods() : page === 'roadmap' ? roadmap() : home();
