// A self-contained fiction scene. No scores, timers, storage or external requests.
const conversations = {
  editions: {
    title: 'The earlier edition',
    text: `<p>The steward sets two folders on the wood. The newer one includes a later visit and a clearer map key. The earlier one is still here; its corners have gone soft.</p><p>“So the first one was wrong?” Renata asks.</p><p>“Its label was too easy to read as a promise. These visits cover different periods. We should explain that.”</p><p>Renata thinks of a perfectly accurate opening-hours notice that once cost her an entire evening.</p>`,
  },
  field: {
    title: 'Hannah’s second visit',
    text: `<p>At the receiving hatch, Hannah is negotiating a cooler over a threshold that was apparently designed by someone without a cooler. It stays closed. A clerk checks the seal and takes the custody form.</p><p>“Did your route include the little channel behind the flats?” Renata asks.</p><p>“I don’t know which channel you mean. I can tell you where I went.” Hannah wipes one boot on the mat. “And where the van couldn’t go.”</p><p>Renata marks the place on a folded slip. “Keep our home address off the public copy.” The steward takes it for the private handoff. Neither has an answer about the water yet. Hannah asks whether the bus still stops by the ceramics shop.</p>`,
  },
  maintenance: {
    title: 'The empty berth',
    text: `<p>Behind the staff rail, a technician nudges an instrument cabinet along a low trolley. The room and its frame stay put. A yellow wheel refuses to turn.</p><p>“Every expensive machine,” she says to nobody in particular, “eventually meets a cheap wheel.”</p><p>A small sign says this compartment is unavailable. Renata asks whether that makes the reading on the wall untrustworthy.</p><p>“It tells you which instrument isn’t available now,” the steward says. “The published record has its own dates and method.” The technician finds a pencil behind her ear and uses it to point at the offending wheel.</p>`,
  },
} as const;

export function readingHallScene(): string {
  return `<section class="section-shell hall-scene" id="story">
    <div class="section-head"><div><p class="eyebrow accent">A SHORT INTERACTIVE STORY · TOLEDO, 2075</p><h2>Before the<br><em>last bus.</em></h2></div><p>Play Renata. Look around, choose what to ask, then decide what to take home.</p></div>
    <div class="scene-layout"><div class="scene-prose"><p>Renata has a transit card, three shirts to photograph for resale, and a paper sun her daughter has asked her to carry “so it sees somewhere new.” The sun is beginning to lose a ray.</p><p>Her daughter wants a picnic by the little channel behind their building. Renata stops at the Basin Reading Hall to ask what the latest river water report covers. Yesterday’s edition is still in the cabinet.</p><p>“Does this include the little channel behind our building?” she asks.</p><p>The steward shows her that this sheet leaves their channel out, then moves a chair toward the counter. Somewhere behind the instrument-room rail, a trolley makes the noise of a very small train.</p><p>Outside, her bus waits on its return run. Five minutes until it leaves. She has time for a question.</p><p class="scene-note">An imagined scene using provisional characters from the story workshop. Choices stay in this page.</p></div>
    <div class="scene-play"><p class="eyebrow">WHAT DO YOU ASK ABOUT?</p><div class="scene-options" id="scene-options">${Object.entries(conversations).map(([key, value]) => `<button type="button" class="scene-choice" data-clue="${key}" aria-pressed="false">${value.title}<span aria-hidden="true">↗</span></button>`).join('')}</div>
    <div id="scene-detail" class="scene-detail" tabindex="-1"><p>Choose a conversation. You can return to the others.</p></div>
    <fieldset class="scene-ending"><legend>What will Renata take home?</legend><button type="button" data-ending="public">A request for a clearer public note</button><button type="button" data-ending="private">A private location request</button><button type="button" data-ending="bus">Her question, for another day</button></fieldset>
    <div id="scene-outcome" class="scene-outcome" tabindex="-1" hidden></div>
    <button type="button" id="scene-restart" class="scene-restart" hidden>Start the scene again</button></div></div>
  </section>`;
}

export function mountReadingHallScene(): void {
  const scene = document.querySelector<HTMLElement>('.hall-scene');
  if (!scene) return;
  const detail = scene.querySelector<HTMLElement>('#scene-detail')!;
  const outcome = scene.querySelector<HTMLElement>('#scene-outcome')!;
  const restart = scene.querySelector<HTMLButtonElement>('#scene-restart')!;
  const seen = new Set<string>();
  scene.querySelectorAll<HTMLButtonElement>('[data-clue]').forEach(button => {
    button.addEventListener('click', () => {
      const clue = button.dataset.clue as keyof typeof conversations;
      const dialogue = conversations[clue];
      seen.add(clue);
      button.setAttribute('aria-pressed', 'true');
      detail.innerHTML = `<h3>${dialogue.title}</h3>${dialogue.text}`;
      detail.focus({ preventScroll: true });
    });
  });
  scene.querySelectorAll<HTMLButtonElement>('[data-ending]').forEach(button => {
    button.addEventListener('click', () => {
      const context = seen.has('field') ? 'She writes the question Hannah helped her sharpen: which channel, and which visit?'
        : seen.has('editions') ? 'She writes both edition dates, so the question survives the next handoff.'
        : 'She writes the channel’s name and asks which place and period the finding covers.';
      const endings: Record<string, [string, string]> = {
        public: ['A question other people can find', `<p>${context} The steward takes a request for a clearer public scope note. Renata leaves her building’s exact location off the public copy.</p><p>The receipt is marked pending. Nobody changes the finding at the counter.</p><p>On the bus, her daughter’s paper sun acquires a small receipt for a hat. Renata imagines someone else reading a better notice before losing an evening to it.</p>`],
        private: ['A small, folded map', `<p>${context} Renata marks the location on a folded slip for the responsible office. The public desk keeps the question; her home address stays off the public copy and goes through the private handoff.</p><p>She has a request number and no promise of an answer tonight. Following up will mean finding time for another visit.</p><p>Outside, Hannah catches the same bus. They discuss the ugly green bowl Hannah and her old roommate both want to keep.</p>`],
        bus: ['A question kept', `<p>Renata copies the edition date into her phone. No request is filed. The question will travel home with her, unfinished.</p><p>The steward gives her a blank slip anyway. “For when you come back.”</p><p>She catches the bus, photographs one shirt in the window light, and sends her daughter a picture of the paper sun visiting the river. For once, a small patch of open time stays open.</p>`],
      };
      const [title, text] = endings[button.dataset.ending!];
      outcome.innerHTML = `<p class="eyebrow">RENATA LEAVES THE HALL</p><h3>${title}</h3>${text}<p><a class="text-link" href="#return-visit">Continue with The Return Visit →</a></p>`;
      outcome.hidden = false;
      restart.hidden = false;
      outcome.focus({ preventScroll: true });
    });
  });
  restart.addEventListener('click', () => {
    seen.clear();
    scene.querySelectorAll('[data-clue]').forEach(button => button.setAttribute('aria-pressed', 'false'));
    detail.innerHTML = '<p>Choose a conversation. You can return to the others.</p>';
    outcome.hidden = true;
    outcome.innerHTML = '';
    restart.hidden = true;
    scene.querySelector<HTMLButtonElement>('[data-clue]')!.focus({ preventScroll: true });
  });
}
