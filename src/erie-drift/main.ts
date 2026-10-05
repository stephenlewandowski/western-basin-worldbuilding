import './style.css';
import lakeArt from '../../assets/erie-drift/lake-morning.webp';
import { createState, grounds, weather, getGround, targetDepth, targetLane, keptCount, speciesName,
  launch, visit, cast, strike, setRig, setDepth, tick, decideCatch, anotherDrift, openChart, returnHome,
  ending, MAX_CASTS, BASKET, marinas, seasons, rigs, baits, fishInfo, tripCost, canVisit, returnReserve, solarRate, score, setBait, type Rig, type Bait, type MarinaId, type Season, type GroundId, type Weather } from './logic';
import { Renderer, drawSounder, drawDrift } from './render';

const base=import.meta.env.BASE_URL;
const root=document.querySelector<HTMLDivElement>('#app')!;
root.innerHTML=`<a class="skip" href="#controls">Skip to game controls</a>
<header class="mast"><a href="${base}">← Western Basin Atlas</a><span>LAKE ERIE · 2075</span><a href="#field-guide">How to play</a></header>
<main id="main"><div class="title-row"><div><p class="eyebrow">A SMALL DAY ON A BIG LAKE</p><h1>Erie <em>Drift.</em></h1></div><p class="deck">Find your water.<br>Bring back a story.</p></div>
<div class="outing-bar" aria-label="Outing status"><div><span>CONDITIONS</span><strong id="weather-name"></strong></div><div><span>BATTERY / HOME RESERVE</span><strong id="energy"></strong><meter id="charge" min="0" max="100" value="100" aria-label="Battery charge"></meter></div><div><span>DRIFTS USED</span><strong id="casts"></strong></div><div><span>FOR SUPPER</span><strong id="basket"></strong></div><div><span>CATCH SCORE</span><strong id="score"></strong></div></div>
<div class="play-layout"><section class="lake-column" aria-label="Lake view"><div class="stage-wrap"><canvas id="lake" tabindex="0" role="img" aria-label="Illustrated composite lake chart. Choose grounds with the nearby buttons." aria-describedby="canvas-help"></canvas><span class="chart-stamp" id="view-label">YOUR LITTLE CORNER OF THE LAKE</span></div>
<div class="radio"><span class="radio-dot" aria-hidden="true"></span><p id="message" role="status" aria-live="polite"></p></div>
<div class="preferences"><button type="button" id="pause" disabled>Pause</button><label><input type="checkbox" id="assist" checked> Relaxed timing</label><label><input type="checkbox" id="sound"> Sound</label><label><input type="checkbox" id="motion"> Less motion</label></div>
<p id="canvas-help" class="small">All actions have buttons. On the lake view: Space casts, strikes or changes reel/ease; P pauses. Arrow keys choose a starting lane before casting.</p>
<details class="logbook"><summary>Your catch journal <span id="journal-count">0</span></summary><div id="journal"><p>The first page is still dry.</p></div></details></section>
<aside id="controls" class="controls" aria-label="Fishing controls" tabindex="-1"><div id="panel"></div><button type="button" id="panel-pause" hidden>Pause fishing</button></aside></div>
<section id="field-guide" class="field-guide"><p class="eyebrow">A FEW THINGS TO KNOW</p><h2>The lake has a rhythm.</h2><div class="guide-grid"><article><h3>Find a drift</h3><p>Choose a ground, a rig and a starting lane. Gold echoes mark fish in this game. The drift sketch shows whether your boat will pass through them. Match your line depth to the sounder.</p></article><article><h3>Feel for the bite</h3><p>Try minnows near the bottom for perch, a spinner with nightcrawlers for walleye, or a soft-plastic jig around rock for bass. A float and worms suit bluegill in the bays. When the prompt says bite, strike. Then reel while the fish rests and ease when it pulls.</p></article><article><h3>Make a day of it</h3><p>Eight drifts and room for three fish in the supper basket. Change grounds while charge permits, or head home early. Your best fish of each species adds to the score: 50 points plus length × a species factor. Kept and released catches score equally; invasive encounters are logged for the fictional dock team. Relaxed timing holds bite prompts and forgives line mistakes. Pause whenever you want.</p></article></div>
<details class="grounding"><summary>The real lake behind this little game</summary><p>The fishing rhythms draw on <a href="https://dam.assets.ohio.gov/image/upload/ohiodnr.gov/documents/wildlife/fishing/Pub5276_LakeErieFishingGuide_Web.pdf">Ohio DNR’s Lake Erie fishing guide</a>. Real place names anchor a schematic map: Maumee Bay, Toledo Intake, Niagara Reef, South Bass, Kelleys Island and East Harbor. Historical <a href="https://community.walleye.com/western-lake-erie-fishing-reports/15151-fishing.html">local fishing reports</a> supply lore, not live advice. Positions, depth readings, catch odds and the solar-electric 2075 boat are authored. Battery percentages are game units, not a range estimate. Solar tops up only during an active drift, never while paused or waiting on a bite. The three-fish basket is a household goal, not a real fishing regulation. This is a game, not a navigation chart, monitoring record or fisheries forecast.</p><p>Explore <a href="${base}atlas/lake-erie-energy-security-coast-2075/">the working coast</a>, <a href="${base}maps/">the basin maps</a> and <a href="${base}atlas/climate-thermal-regime/">real climate records</a>. Game rules do not use Model Lab results. The optional snakehead encounter imagines a future introduction; <a href="https://nas.er.usgs.gov/queries/greatLakes/FactSheet.aspx?HUCNumber=DGreatLakes&Potential=Y&Species_ID=2265&Type=2">USGS/NOAA treats it as a potential Great Lakes invader</a>. Invasive encounters use a fictional dock-review action, not real-world handling instructions. Marina names are present-day anchors, not promises about 2075 facilities. The painted view is shared scenic artwork, not a photograph of each ground.</p><p><a href="https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/docs/erie_drift_sources.md">Place, species and source record ↗</a></p></details></section>
</main><footer>ERIE DRIFT · An experimental Western Basin outing · <a href="${base}game/">Also play Vesper Station</a></footer>`;
const el=<T extends HTMLElement=HTMLElement>(id:string)=>document.getElementById(id) as T;
const panel=el('panel'),canvas=el<HTMLCanvasElement>('lake');
const image=new Image();image.src=lakeArt;
const renderer=new Renderer(canvas,image);
let state=createState(Date.now()),lastPhase='',lastEvent=-1,lastFrame=performance.now(),animationTime=0,lastUi=0,lastPaint=0,paintedPause=false;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');el<HTMLInputElement>('motion').checked=reduced.matches;
const active=()=>['drifting','bite','fight'].includes(state.phase);
const laneName=(lane:number)=>lane===-1?'Inner':lane===0?'Middle':'Outer';
const button=(action:string,label:string,primary=false,disabled=false)=>`<button type="button" data-action="${action}" ${primary?'data-primary class="primary"':''} ${disabled?'disabled':''}>${label}</button>`;
const depthControl=()=>`<label class="depth-label" for="depth">Line depth <output id="depth-label" for="depth">${state.depth.toFixed(1)} m</output></label><input id="depth" type="range" min="0.5" max="${getGround(state).depth}" step="0.5" value="${state.depth}" aria-describedby="echo-text">`;
function instrumentation(){return `<div class="instrument"><div class="instrument-title"><span>SOUNDER</span><span>Bottom ${getGround(state).depth} m</span></div><canvas id="sounder" aria-hidden="true"></canvas><p id="echo-text">Echoes around ${targetDepth(state).toFixed(1)} m. Your line is the pale dot.</p></div><div class="instrument drift-instrument"><div class="instrument-title"><span>YOUR DRIFT</span><span>Wind carries the boat →</span></div><canvas id="drift" aria-hidden="true"></canvas><p id="lane-text">Echoes favor the ${laneName(targetLane(state)).toLowerCase()} lane.</p></div>`;}
function setupSelectors(){return `<div class="kit-fields"><label for="marina">Starting marina<select id="marina">${Object.entries(marinas).map(([id,m])=>`<option value="${id}" ${state.marina===id?'selected':''}>${m.name}</option>`).join('')}</select></label><p id="marina-note" class="small">${marinas[state.marina].note}</p><label for="season">Season<select id="season">${Object.entries(seasons).map(([id,v])=>`<option value="${id}" ${state.season===id?'selected':''}>${v.name}</option>`).join('')}</select></label></div>`;}
function tackleSelectors(){return `<div class="kit-fields"><label for="rig">Tackle<select id="rig">${Object.entries(rigs).map(([id,r])=>`<option value="${id}" ${state.rig===id?'selected':''}>${r.name}</option>`).join('')}</select></label><label for="bait">Bait<select id="bait">${rigs[state.rig].baits.map(id=>`<option value="${id}" ${state.bait===id?'selected':''}>${baits[id]}</option>`).join('')}</select></label><p class="small">${rigs[state.rig].note}</p></div>`;}
function renderPanel(){
  const s=state,g=getGround(s);
  if(s.phase==='dock')panel.innerHTML=`<p class="eyebrow">01 / THE LANDING</p><h2>A boat. A friend.<br>A free afternoon.</h2><p>You’ve borrowed <em>Little Else</em>, a patched-up electric fishing boat. Jo has the sandwiches. You promised fish for supper.</p><p class="companion">“No pressure,” Jo says, putting a tin of beans under the seat.</p>${setupSelectors()}<fieldset class="weather-options"><legend>Pick your day</legend>${(Object.keys(weather) as Weather[]).map(id=>`<label><input type="radio" name="weather" value="${id}" ${s.weather===id?'checked':''}><span><strong>${weather[id].name}</strong><small>${weather[id].text}</small></span></label>`).join('')}</fieldset><p id="solar-note" class="small"></p><label class="scenario-option"><input type="checkbox" id="speculative" ${s.speculative?'checked':''}> Include a speculative 2075 snakehead encounter</label><p class="small">Off by default. A possible future introduction, not an established Lake Erie population claim.</p>${button('launch','Push off →',true)}<p class="small">A short, complete outing. No account or saved progress. Start with relaxed timing, then try a more demanding day.</p>`;
  else if(s.phase==='chart')panel.innerHTML=`<p class="eyebrow">02 / FIND YOUR WATER</p><h2>${s.casts>=MAX_CASTS?'Time for supper.':'Where shall we try?'}</h2><p>${s.casts>=MAX_CASTS?'Eight drifts is a day well spent. Jo is looking at the landing.':'Six familiar places. Charge covers the trip out and a protected reserve for home. Choose one on the chart or below.'}</p><div class="ground-list">${grounds.map(ground=>`<button type="button" data-ground="${ground.id}" ${!canVisit(s,ground.id)?'disabled':''}><span class="ground-number">0${grounds.indexOf(ground)+1}</span><span><strong>${ground.name}</strong><small>${ground.subtitle}</small><small>${tripCost(s,ground.id)}% to travel${!canVisit(s,ground.id)?' · beyond today’s range':' · return charge reserved'}</small></span><span aria-hidden="true">↗</span></button>`).join('')}</div>${button('home','Return to the landing',s.casts>=MAX_CASTS)}<p class="small">Solar adds a little charge while you drift. It will not refill the boat while menus are open. Travel and battery costs are compressed game rules.</p>`;
  else if(s.phase==='rig')panel.innerHTML=`<p class="eyebrow">03 / SET UP THE DRIFT</p><h2>${g.name}</h2><p>${g.detail}</p>${tackleSelectors()}${instrumentation()}<div class="rig-setting">${depthControl()}<p class="setting-label">Starting lane</p><div class="segmented" role="group" aria-label="Starting lane">${[-1,0,1].map(l=>`<button type="button" data-lane="${l}" aria-pressed="${s.lane===l}">${laneName(l)}</button>`).join('')}</div></div>${button('cast','Fish this drift →',true)}${button('chart','Choose another ground')}`;
  else if(s.phase==='drifting')panel.innerHTML=`<p class="eyebrow">04 / LINE DOWN</p><h2>Let it drift.</h2><p>Follow the echoes. You can change line depth while the boat moves.</p>${instrumentation()}<div class="rig-setting">${depthControl()}</div><div class="drift-status"><span id="drift-guidance"></span><progress id="drift-progress" max="1" value="${s.drift}" aria-label="Progress through this drift"></progress></div>${button('chart','Wind in & open chart')}<p class="small">Winding in uses this drift. Pausing stops the outing completely.</p>`;
  else if(s.phase==='bite')panel.innerHTML=`<p class="eyebrow">THERE IT IS</p><h2>${s.rig==='perch'?'Tap. Tap.':'A proper tug.'}</h2><p>The rod tip has an opinion. Lift into the bite.</p>${button('strike','Strike! Fish on →',true)}<p class="bite-note">${s.assisted?'Relaxed timing: the bite will wait for you.':'Strike within five seconds before the bite passes.'}</p>${button('chart','Wind in & open chart')}`;
  else if(s.phase==='fight')panel.innerHTML=`<p class="eyebrow">05 / FISH ON</p><h2>Easy does it.</h2><div id="fish-cue" class="fish-cue"></div><label class="meter-label" for="tension">Line tension <span id="tension-text"></span></label><meter id="tension" min="0" max="1" low=".15" high=".78" optimum=".45" value=".3"></meter><p class="small">Keep some pull. Ease before the line gets tight.</p><label class="meter-label" for="landing">Bringing it in <span id="landing-text"></span></label><progress id="landing" max="1" value=".05"></progress><div class="fight-actions"><button type="button" data-action="reel" data-primary class="primary" aria-pressed="false">Reel steadily</button><button type="button" data-action="ease" aria-pressed="true">Ease the line</button></div><p class="small">Click once to keep reeling or easing. Watch the fish cue. ${s.assisted?'Relaxed timing forgives over-tight or slack line.':'Too much tension or prolonged slack can lose the fish.'}</p>${button('chart','Wind in & open chart')}`;
  else if(s.phase==='landed'&&s.fish)panel.innerHTML=`<p class="eyebrow">06 / IN THE NET</p><h2>${speciesName(s.fish.species)}.</h2><p class="fish-size">${s.fish.length}<span> cm</span></p><p>${fishInfo[s.fish.species].note}</p><p class="catch-points">${s.fish.points} points · only your best of this species counts</p>${fishInfo[s.fish.species].invasive?button('release','Log encounter for dock review',true):button('keep',keptCount(s)>=BASKET?'The supper basket is full':'Keep for supper',true,keptCount(s)>=BASKET)+button('release','Release it back to the lake',keptCount(s)>=BASKET)}<p class="small">${keptCount(s)} of ${BASKET} supper places filled. Keeping and releasing earn the same points.</p>`;
  else if(s.phase==='result')panel.innerHTML=`<p class="eyebrow">A MOMENT BETWEEN DRIFTS</p><h2>${s.casts>=MAX_CASTS?'The day fills up.':'Stay or move?'}</h2><p>${s.casts>=MAX_CASTS?'Jo taps the empty sandwich wrapper. The landing is calling.':'A fish changes the mood of a boat. So does a near miss. There’s always another patch of water.'}</p>${s.casts<MAX_CASTS?button('again','Set up another drift',true)+button('chart','Try another fishing ground'):''}${button('home','Head home for supper',s.casts>=MAX_CASTS)}`;
  else if(s.phase==='home'){
    const e=ending(s);panel.innerHTML=`<p class="eyebrow">BACK AT THE LANDING</p><h2>${e.title}</h2><p>${e.text}</p><p class="ending-detail">${e.detail}</p><dl class="outing-summary"><div><dt>Catch score</dt><dd>${score(s)}</dd></div><div><dt>Charge at the dock</dt><dd>${Math.floor(s.charge)}%</dd></div><div><dt>Fish landed</dt><dd>${s.journal.length}</dd></div><div><dt>Grounds visited</dt><dd>${s.visited.length} / ${grounds.length}</dd></div><div><dt>Drifts taken</dt><dd>${s.casts} / 8</dd></div></dl>${button('restart','Another day on the lake →',true)}<p><a href="${base}atlas/lake-erie-energy-security-coast-2075/">Explore the working coast ↗</a></p>`;
  }
}
let audio:AudioContext|null=null;
function sound(kind:'tap'|'catch'|'click'){
  if(!el<HTMLInputElement>('sound').checked)return;
  try{audio??=new AudioContext();void audio.resume();const start=audio.currentTime;
    const notes=kind==='catch'?[392,494,587]:kind==='tap'?[620,770]:[260];
    notes.forEach((note,i)=>{const osc=audio!.createOscillator(),gain=audio!.createGain();osc.type='sine';osc.frequency.value=note;gain.gain.setValueAtTime(.0001,start+i*.13);gain.gain.exponentialRampToValueAtTime(.055,start+i*.13+.015);gain.gain.exponentialRampToValueAtTime(.0001,start+i*.13+.2);osc.connect(gain);gain.connect(audio!.destination);osc.start(start+i*.13);osc.stop(start+i*.13+.21);});
  }catch{el<HTMLInputElement>('sound').checked=false;}
}
function sync(focus=false){
  const changed=state.phase!==lastPhase;
  if(changed){lastPhase=state.phase;document.body.dataset.phase=state.phase;renderPanel();renderer.draw(state,animationTime,el<HTMLInputElement>('motion').checked);if(state.phase==='bite')sound('tap');if(state.phase==='landed')sound('catch');
    if(focus||!['dock','chart','rig'].includes(state.phase))queueMicrotask(()=>{
      const fishingOnPhone=matchMedia('(max-width:720px)').matches&&['drifting','bite','fight','landed'].includes(state.phase);
      (panel.querySelector<HTMLElement>('[data-primary]')??el('controls')).focus({preventScroll:fishingOnPhone});
      if(fishingOnPhone)document.querySelector('.stage-wrap')!.scrollIntoView({block:'start'});
    });
  }
  if(state.event!==lastEvent){lastEvent=state.event;el('message').textContent=state.message;}
  el('weather-name').textContent=weather[state.weather].name;el('energy').textContent=`${Math.floor(state.charge)}% / ${state.phase==='home'?0:returnReserve(state)}%`;el<HTMLMeterElement>('charge').value=state.charge;el('score').textContent=String(score(state));
  if(el('solar-note'))el('solar-note').textContent=`${seasons[state.season].name} · ${weather[state.weather].wind}. Solar: up to ${(solarRate(state)*60).toFixed(1)} charge points per minute of active drifting; capped at 4 per drift.`;
  if(el('marina-note'))el('marina-note').textContent=marinas[state.marina].note;
  el('casts').textContent=`${state.casts} / ${MAX_CASTS}`;el('basket').textContent=`${keptCount(state)} / ${BASKET}`;
  el<HTMLButtonElement>('pause').disabled=!active();el('pause').textContent=state.paused?'Resume':'Pause';
  el('panel-pause').hidden=!active();el('panel-pause').textContent=state.paused?'Resume fishing':'Pause fishing';
  el('view-label').textContent=['dock','chart','rig','home'].includes(state.phase)?'SCHEMATIC WESTERN LAKE ERIE · NOT FOR NAVIGATION':`${seasons[state.season].name.toUpperCase()} · ${weather[state.weather].name.toUpperCase()} · ${Math.floor(state.charge)}% BATTERY`;
  canvas.setAttribute('aria-label',['dock','chart','rig','home'].includes(state.phase)?`Schematic Western Lake Erie chart. ${getGround(state).name} selected. Use the fishing-ground buttons to travel.`:`Fishing at ${getGround(state).name}. ${state.message}`);
  if(el('depth-label'))el('depth-label').textContent=`${state.depth.toFixed(1)} m`;
  if(el('lane-text'))el('lane-text').textContent=`Echoes favor the ${laneName(targetLane(state)).toLowerCase()} lane. You start in the ${laneName(state.lane).toLowerCase()} lane.`;
  panel.querySelectorAll<HTMLElement>('[data-lane]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.lane)===state.lane)));
  if(el('drift-progress')){
    el<HTMLProgressElement>('drift-progress').value=state.drift;
    el('drift-guidance').textContent=Math.abs(state.depth-targetDepth(state))>=1.35?`Try the echoes at ${targetDepth(state).toFixed(1)} m.`:state.drift<.12?'Coming onto the echoes…':'Good depth. Watch for a bite.';
  }
  if(el('fish-cue')){
    el('fish-cue').textContent=state.pulling?'↗ Pulling — ease the line':'≈ Resting — reel steadily';el('fish-cue').classList.toggle('pulling',state.pulling);
    el<HTMLMeterElement>('tension').value=state.tension;el('tension-text').textContent=state.tension>.78?'Tight':state.tension<.15?'Slack':'Steady';
    el<HTMLProgressElement>('landing').value=state.progress;el('landing-text').textContent=`${Math.min(100,Math.round(state.progress*100))}%`;
    panel.querySelector('[data-action="reel"]')?.setAttribute('aria-pressed',String(state.reeling));panel.querySelector('[data-action="ease"]')?.setAttribute('aria-pressed',String(!state.reeling));
  }
  el('journal-count').textContent=String(state.journal.length);
  if(changed)el('journal').innerHTML=state.journal.length?`<ul>${state.journal.map(f=>`<li><strong>${speciesName(f.species)}</strong><span>${f.length} cm · ${grounds.find(g=>g.id===f.ground)!.name}</span><em>${f.logged?'Logged':f.kept?'For supper':'Released'} · ${f.points} pts</em></li>`).join('')}</ul>`:'<p>The first page is still dry.</p>';
  panel.querySelectorAll<HTMLButtonElement>('button').forEach(b=>{if(state.paused)b.disabled=true;else if(b.dataset.ground)b.disabled=!canVisit(state,b.dataset.ground as GroundId);else if(b.dataset.action!=='keep')b.disabled=false;});
  const slider=el<HTMLInputElement>('depth');if(slider)slider.disabled=state.paused;
}
function act(action:string){
  if(state.paused)return;
  switch(action){
    case 'launch':launch(state);break;case 'cast':cast(state);break;case 'strike':strike(state);break;
    case 'chart':openChart(state);break;case 'again':anotherDrift(state);break;case 'home':returnHome(state);break;
    case 'reel':state.reeling=true;break;case 'ease':state.reeling=false;break;
    case 'keep':decideCatch(state,true);break;case 'release':decideCatch(state,false);break;
    case 'restart':{const assisted=state.assisted;state=createState(Date.now());state.assisted=assisted;break;}
  }sync(true);
}
panel.addEventListener('click',e=>{
  const b=(e.target as Element).closest<HTMLButtonElement>('button');if(!b||b.disabled)return;
  if(b.dataset.action)act(b.dataset.action);
  if(b.dataset.ground){visit(state,b.dataset.ground as GroundId);sound('click');sync(true);}

  if(b.dataset.lane){state.lane=Number(b.dataset.lane);sync();}
});
panel.addEventListener('input',e=>{const input=e.target as HTMLInputElement;if(input.id==='depth'){setDepth(state,input.valueAsNumber);sync();}});
panel.addEventListener('change',e=>{
  const input=e.target as HTMLInputElement;
  if(state.phase==='dock'){
    if(input.name==='weather')state.weather=input.value as Weather;
    if(input.id==='marina')state.marina=input.value as MarinaId;
    if(input.id==='season')state.season=input.value as Season;
    if(input.id==='speculative')state.speculative=input.checked;
  }
  if(input.id==='rig'){setRig(state,input.value as Rig);renderPanel();el('rig').focus();}
  if(input.id==='bait')setBait(state,input.value as Bait);
  sync();
});
canvas.addEventListener('click',e=>{if(state.phase!=='chart'||state.paused)return;const id=renderer.hit(e.clientX,e.clientY);if(id){visit(state,id);sync(true);}});
function pause(){if(!active())return;state.paused=!state.paused;sync();}
el('pause').addEventListener('click',pause);
el('panel-pause').addEventListener('click',pause);
el('assist').addEventListener('change',()=>{state.assisted=el<HTMLInputElement>('assist').checked;renderPanel();sync();});
el('sound').addEventListener('change',()=>sound('click'));
canvas.addEventListener('keydown',e=>{
  if(e.key.toLowerCase()==='p'){e.preventDefault();pause();return;}
  if(state.paused||e.repeat)return;
  if(e.code==='Space'){e.preventDefault();if(state.phase==='rig')act('cast');else if(state.phase==='bite')act('strike');else if(state.phase==='fight')act(state.reeling?'ease':'reel');}
  if(state.phase==='rig'&&(e.key==='ArrowLeft'||e.key==='ArrowRight')){e.preventDefault();state.lane=Math.max(-1,Math.min(1,state.lane+(e.key==='ArrowLeft'?-1:1)));sync();}
});
document.addEventListener('visibilitychange',()=>{if(document.hidden&&active()){state.paused=true;sync();}});
function frame(now:number){
  const dt=Math.max(0,(now-lastFrame)/1000);lastFrame=now;tick(state,dt);
  if(!state.paused)animationTime+=Math.min(dt,.1);
  if((!state.paused&&now-lastPaint>=33)||state.paused!==paintedPause||state.phase!==lastPhase){
    renderer.draw(state,animationTime,el<HTMLInputElement>('motion').checked);lastPaint=now;paintedPause=state.paused;
  }
  if(now-lastUi>100||state.phase!==lastPhase){sync();lastUi=now;
    const sonar=el<HTMLCanvasElement>('sounder'),drift=el<HTMLCanvasElement>('drift');
    if(sonar)drawSounder(sonar,state,el<HTMLInputElement>('motion').checked?0:animationTime);
    if(drift)drawDrift(drift,state);
  }requestAnimationFrame(frame);
}
sync();requestAnimationFrame(frame);
