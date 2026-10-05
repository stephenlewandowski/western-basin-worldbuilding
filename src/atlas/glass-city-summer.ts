import sceneImage from '../../assets/atlas/glass-city-summer/the_usual_table.webp';

export type SummerChoice = 'arcade' | 'market' | 'shop';
export const chooseSummerEnding = (current: SummerChoice|null, next: SummerChoice): SummerChoice => current ?? next;
const endings: Record<SummerChoice,{title:string,text:string}> = {
  arcade: {title:'The long way round',text:`<p>They take the public arcade, away from the exposed stretch. Leena sends the others a picture of the entrance.</p><p>Jo carries the cushion all the way to a table overlooking the loading yard.</p><p>“We’re upgrading,” she says, putting it on the less steady chair.</p><p>A reversing cart interrupts Leena’s most elaborate complaint about the walk. The others arrive while she is still trying to finish it.</p><p>They start late. Nobody has eaten the good peach.</p>`},
  market: {title:'One game, more players',text:`<p>In the market room, a fan turns over the shared tables. At the next one, two children are arguing over a paper game board.</p><p>“We’ll never hear ourselves think,” Jo says.</p><p>“You don’t need to think. You need to stop losing.”</p><p>The first domino has barely touched the table when a child asks what they’re playing.</p><p>Jo begins explaining. Leena cuts the peaches. Their friends arrive and find every chair occupied.</p><p>They finish only one game. By then, everybody knows which peach was the good one.</p>`},
  shop: {title:'This afternoon, then',text:`<p>The shopkeeper looks at the domino box.</p><p>“That table rocks.”</p><p>“So does Jo. We’ll manage.”</p><p>“This afternoon, then. Keep the doorway clear.”</p><p>Leena folds cardboard under one leg. Jo claims the steadier chair. Their friends find them by following the argument.</p><p>Halfway through the game, the shopkeeper comes out with a mug.</p><p>“You’re holding the double six.”</p><p>Jo looks offended. “Is this a repair shop or a surveillance operation?”</p><p>Leena slides over a peach. The shopkeeper pulls up an empty crate.</p>`},
};

export function summerEnding(choice: SummerChoice): {title:string,text:string} { return endings[choice]; }

export function glassCitySummerScene(): string {
  return `<section id="summer-scene" class="section-shell summer-scene"><p class="eyebrow accent">A SUMMER AFTERNOON / INTERACTIVE FICTION</p><h2>The Usual Table</h2><p class="summer-deck">Six peaches, a box of dominoes, and a patch of shade that isn’t there today.</p><figure><a href="${sceneImage}" target="_blank" rel="noopener" aria-label="Open the summer scene illustration full size"><img src="${sceneImage}" alt="Two friends with peaches, dominoes and a seat cushion at a sunlit public table beneath a missing patterned canopy panel; a separate repair bay is cordoned behind them, and a shop's striped awning shades another table" loading="lazy"/></a><figcaption>New summer scene · Composite Toledo-derived fiction, July 2075. The empty cassette opens a patch of sun; no measured cooling performance or exact future temperature is depicted.</figcaption></figure>
    <div class="summer-opening prose"><p>Toledo, July 2075. Early afternoon. Hard sunlight, very little breeze.</p><p>Leena has brought six peaches and the dominoes. It’s her first Friday afternoon off in three weeks.</p><p>She and Jo always meet at the little public table beneath the glass roof. Today a panel has been removed. Its empty frame puts a bright patch across their table.</p><p>Behind the barriers, two workers prepare the replacement. The public diversion goes around the work. It is open. It is also in full sun.</p><p>Jo arrives with their usual cushion. She puts it on the bench, then picks it up again.</p><p>“Tell the sun we were here first.”</p><p>Leena sets down a domino. The table is already warm. Sitting here will mean chasing the shrinking shadow across the bench.</p><p>Nearby, the old repair shop has its own striped awning. The little table underneath belongs to the shop.</p><p>Farther along the public route, an arcade makes a longer shaded loop. The market room has shared tables indoors.</p><p>Their friends will arrive soon. Jo looks into the bag.</p><p>“Don’t eat the good peach.”</p><p>Leena looks too. That narrows it down.</p></div>
    <div data-summer-play><h3>Where will they spend the afternoon?</h3><div class="summer-choices"><button type="button" data-summer-choice="arcade"><strong>Take the longer shaded route</strong><span>A different public table; a longer walk.</span></button><button type="button" data-summer-choice="market"><strong>Move into the market room</strong><span>Shared indoor tables; a noisier afternoon.</span></button><button type="button" data-summer-choice="shop"><strong>Ask to use the shop’s shade</strong><span>A nearby table; permission belongs to the shopkeeper.</span></button></div></div><div data-summer-ending tabindex="-1" aria-live="polite" hidden></div>
    <p class="summer-boundary">A short fictional encounter. No score, timer or saved state. The heat, characters, arcade and market room are scene inventions; this afternoon is not a local climate projection. <a href="${import.meta.env.BASE_URL}atlas/climate-thermal-regime/#local-projections">Explore the separate climate evidence ↗</a></p></section>`;
}

export function mountGlassCitySummer(): void {
  const scene=document.querySelector<HTMLElement>('#summer-scene');
  if(!scene) return;
  const play=scene.querySelector<HTMLElement>('[data-summer-play]')!;
  const ending=scene.querySelector<HTMLElement>('[data-summer-ending]')!;
  let choice: SummerChoice|null=null;
  scene.querySelectorAll<HTMLButtonElement>('[data-summer-choice]').forEach(button=>button.addEventListener('click',()=>{
    if(choice) return;
    choice=chooseSummerEnding(choice,button.dataset.summerChoice as SummerChoice);
    const result=summerEnding(choice);
    play.hidden=true;
    ending.innerHTML=`<h3>${result.title}</h3><div class="prose">${result.text}</div><button type="button" class="button button-outline" data-summer-restart>Try another afternoon</button>`;
    ending.hidden=false; ending.focus();
    ending.querySelector<HTMLButtonElement>('[data-summer-restart]')!.addEventListener('click',()=>{
      choice=null; ending.innerHTML=''; ending.hidden=true; play.hidden=false;
      play.querySelector<HTMLButtonElement>('[data-summer-choice]')!.focus();
    });
  }));
}

export function glassCitySummerTeaser(): string {
  const href=`${import.meta.env.BASE_URL}atlas/glass-city-2075/#summer-scene`;
  return `<section class="section-shell story-teaser"><div><p class="eyebrow accent">STORIES / A GLASS CITY SUMMER AFTERNOON</p><h2>The<br><em>Usual Table.</em></h2><p>Leena has brought peaches and dominoes. Jo has brought the cushion. A missing roof panel has given their table to the sun.</p><p>Choose a different place to spend their afternoon. A short, standalone encounter in Glass City, 2075.</p><a class="button button-primary" href="${href}">Play The Usual Table ↗</a></div><a class="story-teaser-art" href="${href}" aria-label="Play The Usual Table"><img src="${sceneImage}" alt="Friends with peaches and dominoes at a table in hard summer sun beneath an empty canopy frame" loading="lazy"/><span>GLASS CITY · SUMMER SHADE AND COMPANY</span></a></section>`;
}
