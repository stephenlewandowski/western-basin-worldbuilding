// A short sequel to a filed request, independent of the withdrawn comic.
const conversations = {
  card: {
    title: 'Compare the two cards',
    text: `<p>The old sheet has a broad heading. The new card names the visited reach and marks the side channel “not visited.” Its visit dates match the old sheet.</p><p>“The caption changed,” the steward says. “We hadn’t visited your channel then. We still haven’t.”</p><p>“But now the blank has a label.” Renata folds her copy around the shirt. The public card has no home address on it.</p>`,
  },
  wait: {
    title: 'Ask what Hannah needs',
    text: `<p>At the left-rear receiving hatch, a clerk is taking a closed cooler and its custody form. Hannah points toward a reading table on the public floor, away from the case.</p><p>“After this handoff, we can match your sketch to my route notes,” she tells Renata. “I can put the place on a route request. That doesn’t book a visit.”</p><p>Renata looks at the bus outside. “And it won’t tell me what the water’s like.”</p><p>“No. It will tell us we’re talking about the same place.” Hannah still has to finish the handoff. The map check has not happened yet.</p>`,
  },
} as const;

export function returnVisitScene(): string {
  return `<section class="section-shell hall-scene" id="return-visit">
    <div class="section-head"><div><p class="eyebrow accent">ANOTHER AFTERNOON · TOLEDO, 2075</p><h2>The<br><em>Return Visit.</em></h2></div><p>A clearer card is ready. Hannah needs a little longer. Someone is waiting for Renata at the next bus.</p></div>
    <div class="scene-layout"><div class="scene-prose"><p>Renata did bring the slip back. Today she has come to collect the revised card. Her daughter has repaired the paper sun with two mismatched rays and far too much tape.</p><p>A blue shirt lies folded in her bag. Its buyer is waiting at the next stop; they have finally found an afternoon when both can make it.</p><p>At the front-left counter, the steward puts the old sheet beside the new card. The little channel is now plainly marked “not visited.” The finding and visit dates have not changed. Her question has changed what other readers can see.</p><p>Across the room, the instrument spine rises on the right. A trolley rolls smoothly behind the staff rail. Someone has finally replaced its yellow wheel.</p><p>Renata takes her copy. She can catch the bus now, or wait for Hannah to check the place she marked. The picnic question is still open. This afternoon isn’t.</p></div>
    <div class="scene-play"><p class="eyebrow">BEFORE YOU DECIDE</p><div class="scene-options">${Object.entries(conversations).map(([key, value]) => `<button type="button" class="scene-choice" data-return-clue="${key}" aria-pressed="false">${value.title}<span aria-hidden="true">↗</span></button>`).join('')}</div>
    <div id="return-detail" class="scene-detail" tabindex="-1"><p>Look at the card or ask what waiting would accomplish.</p></div>
    <fieldset class="scene-ending" id="return-choices"><legend>What can Renata finish today?</legend><button type="button" data-return-ending="leave">Take the card and catch the bus</button><button type="button" data-return-ending="stay">Stay for Hannah’s location check</button></fieldset>
    <div id="return-outcome" class="scene-outcome" tabindex="-1" hidden></div>
    <button type="button" id="return-restart" class="scene-restart" hidden>Start this visit again</button></div></div>
  </section>`;
}

export function mountReturnVisitScene(): void {
  const scene = document.querySelector<HTMLElement>('#return-visit');
  if (!scene) return;
  const detail = scene.querySelector<HTMLElement>('#return-detail')!;
  const outcome = scene.querySelector<HTMLElement>('#return-outcome')!;
  const restart = scene.querySelector<HTMLButtonElement>('#return-restart')!;
  const buttons = scene.querySelectorAll<HTMLButtonElement>('[data-return-clue], [data-return-ending]');
  let finished = false;
  scene.querySelectorAll<HTMLButtonElement>('[data-return-clue]').forEach(button => {
    button.addEventListener('click', () => {
      if (finished) return;
      const dialogue = conversations[button.dataset.returnClue as keyof typeof conversations];
      button.setAttribute('aria-pressed', 'true');
      detail.innerHTML = `<h3>${dialogue.title}</h3>${dialogue.text}`;
      detail.focus({ preventScroll: true });
    });
  });
  scene.querySelectorAll<HTMLButtonElement>('[data-return-ending]').forEach(button => {
    button.addEventListener('click', () => {
      if (finished) return;
      finished = true;
      const leave = button.dataset.returnEnding === 'leave';
      const title = leave ? 'A shirt changes hands' : 'The place on the map';
      const text = leave
        ? `<p>Renata leaves with the dated clarification. Hannah has not checked her location sketch; that task will wait. The public correction is already on the counter for the next reader.</p><p>At the next stop, the buyer holds the blue shirt against herself. “That’s the color I wanted.” She transfers the agreed price, then helps Renata unstick a sun-ray from the fabric.</p><p>On the way home, Renata rehearses what to tell her daughter: the card is clearer, but it still can’t answer their picnic question. At least this errand is finished.</p>`
        : `<p>When the cooler handoff is finished, Hannah joins Renata at the public reading table. The closed case stays with receiving staff. Hannah lays out her route notes; Renata opens the location sketch with its address corner still folded under. They match the branch she means. Her home address stays off the public card.</p><p>“Here,” Hannah says, adding the place to a route request. “This is the next thing I can ask for.” A request is no booked visit, and they have made no new measurement.</p><p>The bus pulls away beyond the glazing. Renata messages the buyer: “I’ve missed it. Could we try tomorrow?” The reply comes: “Saturday. I work tomorrow.” The blue shirt goes back into her bag.</p><p>Renata has a clearer card, a place checked against Hannah’s notes and a shirt to carry until Saturday. She turns the paper sun toward the window while they fold the map.</p>`;
      outcome.innerHTML = `<p class="eyebrow">THE AFTERNOON CONTINUES</p><h3>${title}</h3>${text}`;
      outcome.hidden = false;
      restart.hidden = false;
      buttons.forEach(control => { control.disabled = true; });
      outcome.focus({ preventScroll: true });
    });
  });
  restart.addEventListener('click', () => {
    finished = false;
    buttons.forEach(control => { control.disabled = false; });
    scene.querySelectorAll('[data-return-clue]').forEach(button => button.setAttribute('aria-pressed', 'false'));
    detail.innerHTML = '<p>Look at the card or ask what waiting would accomplish.</p>';
    outcome.hidden = true;
    outcome.innerHTML = '';
    restart.hidden = true;
    scene.querySelector<HTMLButtonElement>('[data-return-clue]')!.focus({ preventScroll: true });
  });
}
