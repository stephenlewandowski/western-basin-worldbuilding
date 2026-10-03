import fullPage from '../../assets/phase17d/hf05/comic/before_the_last_bus.webp';
import panel1 from '../../assets/phase17d/hf05/comic/panel_1.webp';
import panel2 from '../../assets/phase17d/hf05/comic/panel_2.webp';
import panel3 from '../../assets/phase17d/hf05/comic/panel_3.webp';
import panel4 from '../../assets/phase17d/hf05/comic/panel_4.webp';
import panel5 from '../../assets/phase17d/hf05/comic/panel_5.webp';
import panel6 from '../../assets/phase17d/hf05/comic/panel_6.webp';

export const comicPanels = [
  { image: panel1, description: 'Renata asks at the timber counter of a bright civic hall. Stepped instrument rooms rise on the right; a paper sun peeks from her bag.',
    dialogue: 'Toledo, 2075. Five minutes to the bus. Renata: Is our channel in this water report? My daughter wants a picnic.' },
  { image: panel2, description: 'The steward points at one of two river records. Renata listens, holding a pencil.',
    dialogue: "Steward: These visits covered the river. Your channel isn't on this sheet. Renata: Then let's put it on the question." },
  { image: panel3, description: 'Hannah hands a form to a receiving clerk beside a closed cooler. Renata stays on the public floor.',
    dialogue: "Hannah: I can show where I went. Not where I didn't." },
  { image: panel4, description: 'A technician behind the staff rail works on the yellow wheel beneath a compact instrument cabinet. The room and frame stay fixed.',
    dialogue: 'Technician: A whole new instrument. Same old wheel.' },
  { image: panel5, description: 'Back at the public counter, Renata folds a location slip and receives a pending request receipt.',
    dialogue: 'Steward: A private location note? Renata: Yes. Keep our address off the public copy. Receipt: PENDING.' },
  { image: panel6, description: 'On the bus, Renata smiles at her daughter’s yellow paper sun, now wearing the pending receipt like a hat. The river is outside.',
    dialogue: 'Not an answer yet. Something she can come back for.' },
] as const;

export function comicPage(base: string, repo: string): string {
  return `<article class="section-shell comic-page">
    <a class="back-link" href="${base}atlas/basin-reading-hall/">← The Basin Reading Hall</a>
    <h1>Before the<br><em>Last Bus.</em></h1>
    <p class="comic-place">Toledo and the western Lake Erie basin, 2075.</p>
    <ol class="comic-panels" aria-label="Six comic panels in reading order">${comicPanels.map((panel, i) => `<li><img src="${panel.image}" width="${i % 2 === 0 ? 498 : 496}" height="${i < 2 ? 480 : i < 4 ? 441 : 513}" alt="Panel ${i + 1}. ${panel.description} ${panel.dialogue}" ${i < 2 ? 'fetchpriority="high"' : 'loading="lazy"'} /></li>`).join('')}</ol>
    <div class="comic-after"><p>An imagined Western Basin encounter.</p><div><a href="${base}atlas/basin-reading-hall/#story">Choose what Renata takes home ↗</a><a href="${base}atlas/maumee-bio-ag-2075/">Explore the working landscape upstream ↗</a><a href="${fullPage}" target="_blank" rel="noopener">Open the full comic page ↗</a><a href="${repo}/blob/main/stories/before_the_last_bus.md">Story and image record ↗</a></div></div>
    <details class="comic-transcript"><summary>Text transcript</summary>${comicPanels.map((panel, i) => `<p><strong>Panel ${i + 1}.</strong> ${panel.description} ${panel.dialogue}</p>`).join('')}</details>
  </article>`;
}
