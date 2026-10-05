/** Authored fishing-game rules. Real place names; invented distances, depths, weather and catch odds. */
import {grounds,marinas,seasons,rigs,fishInfo,type Species,type GroundId,type MarinaId,type Season,type Rig,type Bait} from './content';
export * from './content';
export type Weather = 'morning'|'chop'|'haze';
export type Phase = 'dock'|'chart'|'rig'|'drifting'|'bite'|'fight'|'landed'|'result'|'home';
export const weather: Record<Weather,{name:string; wind:string; speed:number; depthShift:number; text:string;solar:number}> = {
  morning:{name:'Clear skies',wind:'SW → NE · light',speed:.020,depthShift:0,solar:1,text:'Warm light, little chop. A good first outing.'},
  chop:{name:'Broken cloud',wind:'W → E · steady',speed:.029,depthShift:.5,solar:.55,text:'A quicker drift. Leave room to pass over the fish.'},
  haze:{name:'Overcast',wind:'SW → NE · light',speed:.016,depthShift:1,solar:.15,text:'Slow drift, gray light. Very little solar top-up.'},
};
export interface Fish {species:Species; length:number; ground:GroundId; kept:boolean;points:number;logged:boolean;}
export interface State {
  phase:Phase; weather:Weather; ground:GroundId; rig:Rig; bait:Bait; marina:MarinaId; season:Season; speculative:boolean; charge:number; solarGained:number; lane:number; depth:number;
  seed:number; assisted:boolean; paused:boolean; casts:number; visited:GroundId[]; journal:Fish[];
  fish:Fish|null; elapsed:number; drift:number; interest:number; biteTime:number;
  tension:number; progress:number; fightTime:number; reeling:boolean; pulling:boolean;
  danger:number; slack:number; message:string; event:number;
}
export const MAX_CASTS=8;
export const BASKET=3;
export const speciesName=(s:Species)=>fishInfo[s].name;
export const getGround=(s:State)=>grounds.find(g=>g.id===s.ground)!;
export const keptCount=(s:State)=>s.journal.filter(f=>f.kept).length;
export function createState(seed=2718): State {
  return {phase:'dock',weather:'morning',ground:'reeds',rig:'perch',bait:'minnows',marina:'maumee',season:'summer',speculative:false,charge:100,solarGained:0,lane:0,depth:4.5,seed:seed>>>0,
    assisted:true,paused:false,casts:0,visited:[],journal:[],fish:null,elapsed:0,drift:0,interest:0,biteTime:0,
    tension:.3,progress:0,fightTime:0,reeling:false,pulling:false,danger:0,slack:0,
    message:'Eight drifts, a borrowed boat, and supper back at the landing.',event:0};
}
function say(s:State,message:string){s.message=message;s.event++;}
function random(s:State){s.seed=(Math.imul(s.seed,1664525)+1013904223)>>>0;return s.seed/4294967296;}
// Charge is a game budget, not a battery/range engineering model.
const travelCost=(a:{x:number;y:number},b:{x:number;y:number})=>Math.ceil(Math.hypot(a.x-b.x,a.y-b.y)*.085);
export const returnReserve=(s:State)=>s.visited.length?travelCost(getGround(s),marinas[s.marina]):0;
export function tripCost(s:State,id:GroundId){const to=grounds.find(g=>g.id===id)!;return travelCost(s.visited.length?getGround(s):marinas[s.marina],to);}
export function canVisit(s:State,id:GroundId){const to=grounds.find(g=>g.id===id);return !!to&&s.casts<MAX_CASTS&&tripCost(s,id)+travelCost(to,marinas[s.marina])<=s.charge;}
export const solarRate=(s:State)=>.1*seasons[s.season].solar*weather[s.weather].solar;
export function score(s:State){const best=new Map<Species,number>();for(const f of s.journal)best.set(f.species,Math.max(best.get(f.species)??0,f.points));return [...best.values()].reduce((a,b)=>a+b,0);}
export function setBait(s:State,bait:Bait){if(s.phase==='rig'&&rigs[s.rig].baits.includes(bait))s.bait=bait;}
export function catchWeights(s:State):Partial<Record<Species,number>>{
  const bay=getGround(s).habitat==='bay',rock=getGround(s).habitat==='rock';
  const weights:Partial<Record<Species,number>>={perch:s.rig==='perch'?50:12,walleye:bay?5:30,bass:rock?22:3,bluegill:bay?30:0,drum:12,whiteperch:10,goby:6};
  if(s.bait==='minnows')weights.perch!+=20;
  if(s.bait==='plastic')weights.bass!+=45;
  if(s.rig==='spinner'&&s.bait==='worms')weights.walleye!+=45;
  if(s.rig==='float'&&bay){weights.bluegill!+=60;weights.walleye=0;}
  if(s.speculative&&bay)weights.snakehead=12;
  return weights;
}
function drawCatch(s:State):Species{const entries=Object.entries(catchWeights(s)) as [Species,number][];let pick=random(s)*entries.reduce((n,[,w])=>n+w,0);for(const [id,w] of entries){pick-=w;if(pick<0)return id;}return 'perch';}
export function launch(s:State){if(s.phase!=='dock')return;s.phase='chart';say(s,'Choose a fishing ground. Jo has packed the sandwiches.');}
export function visit(s:State,id:GroundId){
  if(!['chart','rig','result'].includes(s.phase)||s.casts>=MAX_CASTS)return;
  if(!canVisit(s,id)){say(s,'That trip would use the charge reserved for home. Choose closer water.');return;}
  s.charge-=tripCost(s,id);
  s.ground=id;s.phase='rig';s.fish=null;s.elapsed=0;s.drift=0;
  if(!s.visited.includes(id))s.visited.push(id);
  s.depth=Math.min(getGround(s).depth-.5,s.depth);say(s,getGround(s).voice);
}
export function targetDepth(s:State){return s.rig==='float'?Math.min(1.5,getGround(s).depth-.5):s.rig==='perch'?getGround(s).depth-.5:Math.min(getGround(s).depth-1,getGround(s).walleyeDepth+weather[s.weather].depthShift);}
export function targetLane(s:State){return s.rig==='perch'?getGround(s).perchLane:getGround(s).walleyeLane;}
export function setRig(s:State,rig:Rig){if(s.phase!=='rig')return;s.rig=rig;if(!rigs[rig].baits.includes(s.bait))s.bait=rigs[rig].baits[0];s.depth=targetDepth(s);say(s,rigs[rig].note);}
export function setDepth(s:State,depth:number){if(!['rig','drifting'].includes(s.phase)||!Number.isFinite(depth))return;s.depth=Math.max(.5,Math.min(getGround(s).depth,depth));}
export function cast(s:State){
  if(s.phase!=='rig'||s.casts>=MAX_CASTS)return;
  s.phase='drifting';s.casts++;s.solarGained=0;s.elapsed=0;s.drift=0;s.interest=0;s.biteTime=0;s.fish=null;
  say(s,'Line down. Watch the rod tip and the depth of the echoes.');
}
export function strike(s:State){
  if(s.phase!=='bite')return;
  s.phase='fight';s.tension=.3;s.progress=.05;s.fightTime=0;s.danger=0;s.slack=0;s.reeling=false;s.pulling=false;
  const species=drawCatch(s),info=fishInfo[species],length=Math.round(info.min+random(s)*info.range);
  s.fish={species,length,points:50+length*info.factor,ground:s.ground,kept:false,logged:false};
  say(s,'Fish on! Reel when it rests. Ease the line when it pulls.');
}
function lose(s:State,message:string){s.phase='result';s.fish=null;s.reeling=false;s.pulling=false;say(s,message);}
export function decideCatch(s:State,keep:boolean){
  if(s.phase!=='landed'||!s.fish)return;
  if(keep&&(keptCount(s)>=BASKET||fishInfo[s.fish.species].invasive))return;
  const logged=!!fishInfo[s.fish.species].invasive;
  s.journal.push({...s.fish,kept:keep,logged});s.fish=null;s.phase='result';
  say(s,logged?'Encounter recorded for the dock team. Jo marks the place in the journal.':keep?'Into the ice box. Jo is already making plans for the lemon.':'Back into the lake. A quick flash, and it’s gone.');
}
export function anotherDrift(s:State){if(s.phase!=='result'||s.casts>=MAX_CASTS)return;s.phase='rig';s.drift=0;s.elapsed=0;say(s,'Move the starting lane or change depth for the next drift.');}
export function openChart(s:State){
  if(['dock','home','landed'].includes(s.phase))return;
  s.phase='chart';s.fish=null;s.reeling=false;s.paused=false;say(s,s.casts>=MAX_CASTS?'The afternoon has filled up. Time to head to the landing.':'Line wound in. Choose another ground, or return to the landing.');
}
export function returnHome(s:State){if(!['chart','rig','result'].includes(s.phase))return;s.charge=Math.max(0,s.charge-returnReserve(s));s.phase='home';s.paused=false;s.reeling=false;say(s,'The boat nudges the fenders. Someone has already set the table.');}
export function tick(s:State,delta:number){
  if(s.paused||!Number.isFinite(delta)||delta<=0)return;
  const dt=Math.min(delta,.1); // No catch-up jump when a background tab returns.
  if(s.phase==='drifting'){
    const gain=Math.min(dt*solarRate(s),4-s.solarGained,100-s.charge);s.charge+=gain;s.solarGained+=gain;
    s.elapsed+=dt;s.drift=Math.min(1,s.drift+weather[s.weather].speed*dt);
    const depthError=Math.abs(s.depth-targetDepth(s));
    const laneError=Math.abs(s.lane-targetLane(s));
    const inSchool=s.drift>.12&&s.drift<.86;
    if(depthError<1.35&&inSchool)s.interest+=dt*(1-depthError/1.35)*(1-laneError*.32)*(s.rig==='float'&&getGround(s).habitat!=='bay'?.55:1);
    else s.interest=Math.max(0,s.interest-dt*.12);
    if(s.interest>(s.rig==='perch'?3.2:4.6)){
      s.phase='bite';s.biteTime=0;say(s,s.rig==='perch'?'Tap. Tap. A bite — strike!':'A firm tug. Strike!');
    }else if(s.drift>=1)lose(s,depthError>=1.35?'The drift ends without a bite. The echoes were at a different depth. Adjust the line and try again.':'The boat passes the last echoes. Reposition for another drift.');
  }else if(s.phase==='bite'){
    s.biteTime+=dt;
    if(!s.assisted&&s.biteTime>5)lose(s,'A tap, a tug, then nothing. Jo says that one was definitely enormous.');
  }else if(s.phase==='fight'){
    s.fightTime+=dt;
    const walleye=['walleye','bass','drum','snakehead'].includes(s.fish?.species??'');
    const pulling=(s.fightTime%(walleye?6:5.2))>(walleye?2.8:3);
    if(pulling!==s.pulling){s.pulling=pulling;say(s,pulling?'It’s pulling — ease the line.':'It’s resting — reel steadily.');}
    s.tension=Math.max(0,Math.min(1,s.tension+dt*(s.reeling?(pulling?(walleye?.34:.27):.085):-.25)));
    if(s.assisted)s.tension=Math.min(.9,Math.max(.12,s.tension));
    s.progress=Math.max(0,s.progress+dt*(s.reeling?(pulling?.024:(walleye?.13:.17)):(s.tension<.1?-.035:-.002)));
    s.danger=s.tension>.96?s.danger+dt:0;s.slack=s.tension<.06?s.slack+dt:0;
    if(s.danger>1.1)lose(s,'Too much pull. The hook comes free. Ease sooner on the next fish.');
    else if(s.slack>5)lose(s,'The line goes slack and the fish slips off. Keep a little pull next time.');
    else if(s.progress>=1){s.phase='landed';s.reeling=false;say(s,`${speciesName(s.fish!.species)}, ${s.fish!.length} cm. Nicely done. A new entry for the catch journal.`);}
  }
}
export function ending(s:State){
  const kept=keptCount(s),released=s.journal.filter(f=>!f.kept&&!f.logged).length;
  if(kept===0)return {title:'Still a good day',text:`Jo opens the beans with unnecessary ceremony. “Locally sourced from my cupboard.” You tell the story of ${s.journal.length?'the fish you met':'the one that got away'}. Nobody asks for proof. The lake is still bright beyond the dock.`,detail:`${released} released. The supper happens anyway.`};
  if(kept<BASKET)return {title:'Plenty, with potatoes',text:'The fish go farther than you expected once Jo finds the potatoes. Someone pulls another chair into the shade. You describe the drift with your fork. By the second telling, the waves are a little bigger.',detail:`${kept} for supper · ${released} released.`};
  return {title:'Save a place at the table',text:'The pan starts talking before anyone else does. Jo borrows a lemon from the next boat and somehow invites its entire crew. You take the chair facing the water. Tomorrow, someone else can do the finding.',detail:`${kept} for supper · ${released} released. The little ice box did its job.`};
}
