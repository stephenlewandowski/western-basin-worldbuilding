// Standalone fiction: all content and progress stay on this page.
export type HallQuestion = 'orange' | 'field' | 'location';
export type HallEnding = 'not-tonight' | 'the-place' | 'a-promise';
export interface HallEncounter {
  question: HallQuestion | null;
  locationCompared: boolean;
  cardInspected: boolean;
  fieldRouteAsked: boolean;
  ending: HallEnding | null;
}
export const newHallEncounter = (): HallEncounter => ({ question: null, locationCompared: false, cardInspected: false, fieldRouteAsked: false, ending: null });

export function inspectHallCard(state: HallEncounter): HallEncounter {
  return state.ending || state.cardInspected ? state : { ...state, cardInspected: true };
}

export function askHallQuestion(state: HallEncounter, question: HallQuestion): HallEncounter {
  if (state.ending) return state;
  return { ...state, question, locationCompared: state.locationCompared || question === 'location', fieldRouteAsked: state.fieldRouteAsked || question === 'field' };
}

export function decideHallEncounter(state: HallEncounter, ending: HallEnding): HallEncounter {
  return state.ending ? state : { ...state, ending };
}

const questions: Record<HallQuestion, { title: string; text: string }> = {
  orange: {
    title: 'What does the orange mean?',
    text: `<p>Renata runs a finger along the edge of the orange model band.</p>
      <p>“The model goes right up to this line?”</p><p>“On this card, yes,” the steward says. “It carries the interpretation beyond the blue observation points.”</p>
      <p>“Then stops.”</p><p>“Then this card has no answer. The gray isn’t a second result.”</p>
      <p>“It looks like we’ve been cleared.”</p><p>“It doesn’t mean that.”</p>
      <p>Renata looks at the neat edge. “Then why draw it like a boundary?”</p>
      <p>The steward studies the card. “To make a complicated record easier to read.”</p>
      <p>“It worked.”</p><p>“Until you needed to know about the place just outside it.”</p>`,
  },
  field: {
    title: 'Where did the field crew actually go?',
    text: `<p>At the left-rear receiving hatch, Hannah slides a closed field case and its custody form to the receiving staff. Renata approaches from the open reading floor and stays on the public side.</p>
      <p>“Did you go into this side channel?”</p><p>“Let me show you where we went,” Hannah says.</p>
      <p>Once staff have received the case, Hannah brings a dry copy of her route record to a public reading table. The closed case stays with receiving staff.</p>
      <p>Hannah traces a line on her route record. “Main channel to this crossing. Then we turned back. We didn’t go into your side channel.”</p>
      <p>“But the orange model band goes farther.”</p><p>“That isn’t my route.”</p>
      <p>Renata puts the Water Conditions Card beside the route record. The lines end in different places.</p>
      <p>Renata looks at her daughter’s message. “That distinction is not going to fit in a text.”</p>
      <p>“No,” Hannah says. “It usually doesn’t.”</p>`,
  },
  location: {
    title: 'Check the exact channel',
    text: `<p>Renata opens the photograph. It has a location attachment.</p>
      <p>The steward looks from the photograph to the card. “May I use the attached location to check we mean the same spot?”</p>
      <p>“Does that put our address on the Water Conditions Card?”</p><p>“No. I’ll use it for this comparison. Nothing gets added to the public card.”</p>
      <p>Renata hands over the phone. The steward matches the point carefully.</p>
      <p>“Here, at this bend in the side channel.”</p><p>“Yes. That’s ours.”</p>
      <p>It is not one of the places the field team visited. It is also just beyond the orange model band.</p>
      <p>Renata waits. “That’s it?”</p><p>“That’s what this card can tell you.”</p>
      <p>“And the water?”</p><p>“The card doesn’t know.”</p>`,
  },
};

function renatasMessage(state: HallEncounter): string {
  const messages: Record<HallEnding, [string, string, string]> = {
    'not-tonight': ['Not tonight. This card doesn’t cover our channel.', 'Not tonight. Our channel’s gray. The card can’t tell us.', 'Not tonight. Hannah didn’t go into our channel.'],
    'the-place': ['Wait for me. They can place the spot, but they can’t tell me about the water.', 'Wait for me. They’ve found our spot on the card, but it can’t tell me about the water.', 'Wait for me. Hannah didn’t visit our channel. They can place the spot, but they can’t tell me about the water.'],
    'a-promise': ['The orange band stops before you. Stay on our side.', 'I’ve checked the card. The orange band stops before you. Stay on our side.', 'Hannah stopped at the crossing. The orange band stops before you. Stay on our side.'],
  };
  return messages[state.ending!][state.fieldRouteAsked ? 2 : state.cardInspected ? 1 : 0];
}

export function hallEndingText(state: HallEncounter): { title: string; text: string } | null {
  if (!state.ending) return null;
  if (state.ending === 'not-tonight') return {
    title: 'Not tonight',
    text: `<p>Renata types:</p><blockquote><p>“${renatasMessage(state)}”</p></blockquote>
      <p>Three dots appear. Disappear. Return.</p><blockquote><p>“That’s not what Mara says the map says.”</p></blockquote>
      <p>Renata looks at the orange model band again. “I know.”</p>
      <p>A minute later her daughter sends a picture from the concrete edge. Shoes still on. Someone has drawn a miserable face in the dust beside them.</p>
      <p>Before Renata leaves, the steward submits a wording review for the Water Conditions Card: the gray side channel should not look cleared simply because no field visit is shown there.</p>
      <p>No new measurement appears. Nothing proves Renata made the right decision.</p>
      <p>The cost is an afternoon. For her daughter, that is not nothing.</p>`,
  };
  if (state.ending === 'the-place') return {
    title: 'The place they meant',
    text: `${state.locationCompared
      ? '<p>The point is still where they placed it. Renata asks the steward to keep a private location note for further review; no address goes on the Water Conditions Card.</p>'
      : '<p>Renata lets the steward use the location attachment for a private comparison. The point lands where expected: not among the field team’s blue observation points, and just beyond the orange model band. She asks for a private note for further review; no address goes on the Water Conditions Card.</p>'}
      <p>No field visit is scheduled. No sample appears. No answer arrives.</p>
      <blockquote><p>“${renatasMessage(state)}”</p></blockquote>
      <p>Her daughter replies immediately. “So what am I waiting for?”</p>
      <p>Renata starts an explanation. Deletes it. Types:</p><blockquote><p>“Me.”</p></blockquote>
      <p>By the time she reaches the channel, the other kids have gone. Her daughter is on the warm concrete, shoes beside her, feet still dry.</p>
      <p>She is angry. Renata sits beside her anyway.</p>
      <p>Behind them, the water keeps moving through a place the map can locate but the record has not resolved.</p>`,
  };
  return {
    title: 'A line becomes a promise',
    text: `<p>Renata looks at the Water Conditions Card one more time. The orange model band stops before the side channel.</p>
      <blockquote><p>“${renatasMessage(state)}”</p></blockquote>
      <p>The reply comes almost immediately. “YES”</p>
      <p>As Renata leaves, the steward sends the gray/no-coverage wording for review. It is a request to clarify the same card, not a new observation.</p>
      <p>The kids are already in the water.</p>
      <p>Nothing dramatic happens. No alarm. No one becomes ill. The evening simply continues.</p>
      <p>Later, Renata looks at the card beside the wording-review request. It names the gap her text left out: no direct field observation and no supported model result for the side channel.</p>
      <p>Her daughter looks over her shoulder. “You said it wasn’t in the orange.”</p>
      <p>“I said the orange stopped before it.”</p><p>“That’s the same thing.”</p>
      <p>Renata begins to answer. Then stops.</p><p>To her daughter, it had been the same thing.</p>`,
  };
}

function cardLegend(id: string, includeSafety = true): string {
  return `<section class="water-legend" aria-labelledby="${id}"><h3 id="${id}">Reading the Water Conditions Card</h3>
    <dl><div><dt><span class="card-symbol blue-dot" aria-hidden="true"></span>Blue dot</dt><dd>Direct field visit / observation</dd></div>
    <div><dt><span class="card-symbol orange-band" aria-hidden="true"></span>Orange band</dt><dd>Model-supported extension beyond direct observations</dd></div>
    <div><dt><span class="card-symbol gray-coverage" aria-hidden="true"></span>Gray / no coverage</dt><dd>No answer from this card for that location</dd></div></dl>
    ${includeSafety ? '<p class="card-safety">The card does not determine whether water is safe or unsafe.</p>' : ''}</section>`;
}

type CardRegion = 'blue' | 'orange' | 'gray';
const cardRegions: Record<CardRegion, { label: string; explanation: string }> = {
  blue: { label: 'Blue observation points', explanation: 'These points mark where a field team directly visited during the card’s period.' },
  orange: { label: 'Orange model band', explanation: 'The model carries interpretation beyond those field visits into this band; it is not another visit.' },
  gray: { label: 'Gray side channel', explanation: 'For this side channel, the card supplies neither a direct observation nor a supported model result.' },
};

export function waterConditionsCard(): string {
  return `<dialog id="water-card-dialog" class="water-card-dialog" data-card-selection="gray" aria-labelledby="water-card-title" aria-describedby="water-card-fiction">
    <header class="water-card-header"><div><p class="eyebrow">FICTIONAL STORY ARTIFACT · EDITION 4</p><h2 id="water-card-title">Water Conditions Card</h2></div><button type="button" class="card-close" id="water-card-close" autofocus>Close card <span aria-hidden="true">×</span></button></header>
    <p class="card-context-line">Willow Steps side channel · fictional Toledo, 2075<br>12–14 July · consulted late on 14 July</p>
    <p class="card-focal"><strong>Her daughter’s channel.</strong> Just beyond the orange model band, in the gray side channel.</p>
    <figure class="water-card-map"><svg viewBox="0 0 600 340" role="img" aria-labelledby="water-map-title water-map-desc">
      <title id="water-map-title">Schematic Water Conditions Card: the side channel lies beyond the visits and orange model band</title>
      <desc id="water-map-desc">Three labeled blue circles mark direct field visits along the main channel. An orange patterned band carries modeled interpretation farther along the main channel and partway toward a side channel. The marked place Renata means is in the gray, hatched side channel, past the orange band. None of these colors determines water safety.</desc>
      <defs><pattern id="no-coverage-hatch" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#d3d4d1"/><path d="M0 8L8 0" stroke="#a6aaa7" stroke-width="1"/></pattern><pattern id="model-band-pattern" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#efbb7a"/><circle cx="5" cy="5" r="1" fill="#9a5722"/></pattern></defs>
      <rect width="600" height="340" rx="4" fill="#f4f1e8"/>
      <text x="22" y="29" class="map-small">SCHEMATIC / NOT TO SCALE</text>
      <path d="M28 273C134 276 195 250 257 222S379 176 562 177" fill="none" stroke="url(#no-coverage-hatch)" stroke-width="42"/>
      <g data-card-area="gray" class="map-region map-gray-channel"><path d="M431 116C440 96 458 82 483 63" fill="none" stroke="transparent" stroke-width="48"/><path d="M357 186C391 169 418 147 431 116S458 82 483 63" fill="none" stroke="url(#no-coverage-hatch)" stroke-width="29"/></g>
      <path data-card-area="orange" class="map-region map-orange-band" d="M259 222C306 197 350 183 399 178L395 157C399 149 402 141 405 132" fill="none" stroke="url(#model-band-pattern)" stroke-width="63" stroke-linecap="butt"/>
      <path d="M28 273C134 276 195 250 257 222S379 176 562 177M357 186C391 169 418 147 431 116S458 82 483 63" fill="none" stroke="#6b787c" stroke-width="2" pointer-events="none"/>
      <path d="M238 208V258" stroke="#384c53" stroke-width="5"/><text x="160" y="197">Crossing</text>
      <g data-card-area="blue" class="map-region map-blue-points"><g fill="transparent"><circle cx="75" cy="273" r="22"/><circle cx="155" cy="260" r="22"/><circle cx="231" cy="234" r="22"/></g><g fill="#2675a8" stroke="#fff" stroke-width="3"><circle cx="75" cy="273" r="9"/><circle cx="155" cy="260" r="9"/><circle cx="231" cy="234" r="9"/></g></g>
      <text x="52" y="313" fill="#205e86">Blue observation points</text>
      <path d="M303 141L318 181" stroke="#965219" stroke-width="2"/><text x="182" y="121" fill="#804611">Orange model band</text>
      <g data-card-area="gray" class="map-region map-daughter"><circle cx="457" cy="84" r="24" fill="none" stroke="#fffdf7" stroke-width="7"/><circle cx="457" cy="84" r="19" fill="none" stroke="#203039" stroke-width="4"/><circle cx="457" cy="84" r="4" fill="#203039"/><text x="411" y="48" class="map-person">Renata’s point</text><path d="M471 99L495 113" stroke="#203039" stroke-width="2"/><text x="432" y="136">Exact location</text></g>
      <text x="422" y="238">Side channel</text><text x="422" y="265" fill="#515b5b">Gray / no coverage</text>
      <path d="M441 225L445 114" stroke="#515b5b" stroke-width="1.5" stroke-dasharray="4 4"/>
    </svg><figcaption class="card-reading-trail"><span>Blue visits</span><span aria-hidden="true">→</span><span>Orange extension</span><span aria-hidden="true">→</span><strong>Their channel: gray</strong></figcaption></figure>
    <div class="card-inspection" role="group" aria-label="Inspect a mark on the card">${Object.entries(cardRegions).map(([region, content]) => `<button type="button" data-card-region="${region}" aria-pressed="${region === 'gray'}" aria-controls="water-card-explanation">${content.label}</button>`).join('')}</div>
    <p class="card-explanation" id="water-card-explanation" aria-live="polite" aria-atomic="true">${cardRegions.gray.explanation}</p>
    <p class="card-safety">The card does not determine whether water is safe or unsafe.</p>
    <p class="card-annotation">The ring is a story annotation for the place Renata means, not part of the public edition or another field observation. Tap a mark above or use its button.</p>
    <p id="water-card-fiction" class="card-fiction">An invented place and record for this story. Not real monitoring data, a GIS product or output from the current Model Lab.</p>
    ${cardLegend('water-dialog-legend', false)}
    <div class="card-limits"><p><strong>What it can show:</strong> where direct field visits occurred and where the model supports an interpretation for this period.</p><p><strong>What it cannot show:</strong> an answer for the gray side channel, or whether any water is safe, unsafe, clean or contaminated.</p></div>
    <p class="card-source">Fictional edition 4 · WC-04. Basis: invented field-route log and model interpretation record. The story is inspired by separate observations, models and versioned records in the project; these dots and this band are not project measurements or Model Lab results.</p>
  </dialog>`;
}

export function readingHallScene(): string {
  return `<section class="section-shell hall-scene orange-band-scene" id="story" aria-labelledby="orange-band-title">
    <div class="section-head"><div><p class="eyebrow accent">A STANDALONE INTERACTIVE ENCOUNTER · TOLEDO, 2075</p><h2 id="orange-band-title" tabindex="-1">The<br><em>Orange Band.</em></h2></div><p>Her daughter wants to wade. Renata needs an answer the card cannot give her.</p></div>
    <div class="scene-layout"><div class="scene-prose">
      <p>Renata stops at the Basin Reading Hall because her daughter wants to wade in the little side channel behind their building.</p>
      <p>At the front-left public counter lies the latest <strong>Water Conditions Card</strong>: a short summary for a particular place and period. It tries to turn a complicated record into something people can use.</p>
      <p>Blue dots mark places a field team actually visited. An orange model band carries the interpretation beyond those visits. Then gray: this card supplies neither a direct observation nor a supported model result for that place.</p>
      <p>Renata’s side channel lies just beyond the orange band.</p>
      <p>Her phone vibrates. A photograph: several kids beside the water after a hot afternoon.</p>
      <blockquote class="scene-message"><p>“Mum. Mara says we’re outside the orange part. Can we go in?”</p></blockquote>
      <p>The steward turns the card toward her. “Show me which place you mean.”</p>
      <p>Beyond the counter, the reading floor is open. The instrument spine rises on the right; staff and service routes run behind its rooms. Renata stays on the public side.</p>
      <p class="scene-note">An imagined encounter in a developing fictional Hall. The card, place, period and people are invented; no new canon or real water finding is established.</p>
    </div><div class="scene-play">
      ${cardLegend('water-story-legend')}
      <button type="button" class="water-card-open" id="water-card-open" aria-haspopup="dialog" aria-controls="water-card-dialog">Open the Water Conditions Card <span aria-hidden="true">↗</span></button>
      <p class="scene-prompt">Ask a question or inspect the card before deciding. You can reread the conversations.</p>
      <div class="scene-options" aria-label="Optional conversations">${Object.entries(questions).map(([id, question]) => `<button type="button" class="scene-choice" data-hall-question="${id}" aria-expanded="false" aria-controls="orange-detail">${question.title}<span aria-hidden="true">↗</span></button>`).join('')}</div>
      <div id="orange-detail" class="scene-detail" tabindex="-1" hidden></div>
      <p class="scene-prompt">Another message lights the phone.</p><blockquote class="scene-message"><p>“We brought the old towels. Mara’s already taken her shoes off.”</p></blockquote>
      <fieldset class="scene-ending" id="orange-choices"><legend>Your daughter is waiting for an answer.</legend>
        <button type="button" data-hall-ending="not-tonight">Tell her to stay out for today</button>
        <button type="button" data-hall-ending="the-place" id="location-decision">Ask her to wait while the Hall checks the exact location</button>
        <button type="button" data-hall-ending="a-promise">Tell her they are outside the orange area</button>
      </fieldset>
      <div id="orange-outcome" class="scene-outcome" tabindex="-1" hidden></div>
      <button type="button" id="orange-restart" class="scene-restart" hidden>Start the encounter again</button>
    </div></div>${waterConditionsCard()}
  </section>`;
}

export function mountReadingHallScene(): void {
  const scene = document.querySelector<HTMLElement>('#story');
  if (!scene || scene.dataset.mounted) return;
  scene.dataset.mounted = 'true';
  const detail = scene.querySelector<HTMLElement>('#orange-detail')!;
  const outcome = scene.querySelector<HTMLElement>('#orange-outcome')!;
  const restart = scene.querySelector<HTMLButtonElement>('#orange-restart')!;
  const opener = scene.querySelector<HTMLButtonElement>('#water-card-open')!;
  const dialog = scene.querySelector<HTMLDialogElement>('#water-card-dialog')!;
  const close = scene.querySelector<HTMLButtonElement>('#water-card-close')!;
  const controls = scene.querySelectorAll<HTMLButtonElement>('[data-hall-question], [data-hall-ending]');
  const locationDecision = scene.querySelector<HTMLButtonElement>('#location-decision')!;
  let state = newHallEncounter();

  function selectCardRegion(region: CardRegion): void {
    dialog.dataset.cardSelection = region;
    dialog.querySelectorAll<HTMLButtonElement>('[data-card-region]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.cardRegion === region)));
    dialog.querySelector<HTMLElement>('#water-card-explanation')!.textContent = cardRegions[region].explanation;
  }
  dialog.querySelectorAll<HTMLButtonElement>('[data-card-region]').forEach(button => {
    button.addEventListener('click', () => selectCardRegion(button.dataset.cardRegion as CardRegion));
  });
  dialog.querySelector('svg')!.addEventListener('click', event => {
    const region = event.target instanceof Element ? event.target.closest('[data-card-area]')?.getAttribute('data-card-area') as CardRegion | undefined : undefined;
    if (region) selectCardRegion(region);
  });

  opener.addEventListener('click', () => {
    state = inspectHallCard(state);
    selectCardRegion('gray');
    dialog.scrollTop = 0;
    dialog.showModal();
    document.body.classList.add('water-card-is-open');
    close.focus({ preventScroll: true });
  });
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab' || event.ctrlKey || event.altKey || event.metaKey) return;
    const targets = [...dialog.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input:not([disabled]), [tabindex="0"]')];
    const first = targets[0]; const last = targets[targets.length - 1];
    if (!first) return;
    if ((!event.shiftKey && document.activeElement === last) || (event.shiftKey && document.activeElement === first) || !dialog.contains(document.activeElement)) {
      event.preventDefault(); (event.shiftKey ? last : first).focus();
    }
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('water-card-is-open');
    opener.focus({ preventScroll: true });
  });

  scene.querySelectorAll<HTMLButtonElement>('[data-hall-question]').forEach(button => {
    button.addEventListener('click', () => {
      const next = askHallQuestion(state, button.dataset.hallQuestion as HallQuestion);
      if (next === state) return;
      state = next;
      const question = questions[state.question!];
      scene.querySelectorAll<HTMLButtonElement>('[data-hall-question]').forEach(control => control.setAttribute('aria-expanded', String(control === button)));
      detail.innerHTML = `<h3>${question.title}</h3>${question.text}`;
      detail.hidden = false;
      // A comparison already made stays made; the second ending does not repeat it.
      if (state.locationCompared) locationDecision.textContent = 'Ask her to wait for you';
      detail.focus();
    });
  });
  scene.querySelectorAll<HTMLButtonElement>('[data-hall-ending]').forEach(button => {
    button.addEventListener('click', () => {
      const next = decideHallEncounter(state, button.dataset.hallEnding as HallEnding);
      if (next === state) return;
      state = next;
      const ending = hallEndingText(state)!;
      outcome.innerHTML = `<p class="eyebrow">THE AFTERNOON CONTINUES</p><h3>${ending.title}</h3>${ending.text}`;
      outcome.hidden = false; restart.hidden = false;
      controls.forEach(control => { control.disabled = true; });
      outcome.focus();
    });
  });
  restart.addEventListener('click', () => {
    state = newHallEncounter();
    controls.forEach(control => { control.disabled = false; });
    scene.querySelectorAll('[data-hall-question]').forEach(control => control.setAttribute('aria-expanded', 'false'));
    locationDecision.textContent = 'Ask her to wait while the Hall checks the exact location';
    detail.innerHTML = ''; detail.hidden = true;
    outcome.innerHTML = ''; outcome.hidden = true; restart.hidden = true;
    scene.querySelector<HTMLElement>('#orange-band-title')!.focus();
  });
}
