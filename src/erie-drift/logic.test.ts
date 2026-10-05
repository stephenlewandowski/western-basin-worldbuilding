import {describe,it,expect} from 'vitest';
import {createState,launch,visit,setRig,setDepth,targetDepth,targetLane,cast,tick,strike,decideCatch,
  anotherDrift,returnHome,openChart,keptCount,ending,MAX_CASTS,grounds,rigs,canVisit,returnReserve,score,setBait,catchWeights,type State,type Rig,type GroundId} from './logic';
const step=(s:State,seconds:number)=>{for(let i=0;i<seconds*20;i++)tick(s,.05);};
function ready(species:Rig='perch',ground:GroundId='reeds'){
  const s=createState(7);if(['islands','kelleys','harbor'].includes(ground))s.marina='eastharbor';launch(s);visit(s,ground);setRig(s,species);s.lane=targetLane(s);return s;
}
function catchFish(s:State){cast(s);step(s,40);expect(s.phase).toBe('bite');strike(s);s.reeling=true;step(s,50);expect(s.phase).toBe('landed');}
describe('Erie Drift: a complete, bounded outing',()=>{
  it('lets all tackle reach a mixed catch through its depth/lane on every ground',()=>{
    for(const ground of grounds)for(const rig of Object.keys(rigs) as Rig[]){
      const s=ready(rig,ground.id);catchFish(s);expect(s.fish?.species).not.toBe('snakehead');
      decideCatch(s,false);expect(s.journal).toHaveLength(1);expect(s.journal[0].ground).toBe(ground.id);
    }
  });
  it('makes depth and starting lane affect bites, with a recoverable empty drift',()=>{
    const good=ready('walleye'),offLane=ready('walleye'),wrong=ready('walleye');
    offLane.lane=-1;setDepth(wrong,5);cast(good);cast(offLane);cast(wrong);step(good,12);step(offLane,12);step(wrong,60);
    expect(good.phase).toBe('bite');expect(offLane.phase).toBe('drifting');expect(wrong.phase).toBe('result');
    anotherDrift(wrong);setDepth(wrong,targetDepth(wrong));catchFish(wrong);
  });
  it('waits on a bite in relaxed mode and allows a missed bite in standard mode',()=>{
    const relaxed=ready(),standard=ready();standard.assisted=false;cast(relaxed);cast(standard);step(relaxed,30);step(standard,30);
    expect(relaxed.phase).toBe('bite');expect(standard.phase).toBe('result');expect(standard.fish).toBeNull();
  });
  it('rewards reel/ease handling and loses a fish under sustained standard-mode tension',()=>{
    const s=ready();cast(s);step(s,12);strike(s);s.assisted=false;s.reeling=true;step(s,30);
    expect(s.phase).toBe('result');expect(s.message).toContain('Too much pull');
    const handled=ready('walleye');cast(handled);step(handled,14);strike(handled);handled.assisted=false;
    for(let i=0;i<1200&&handled.phase==='fight';i++){handled.reeling=!handled.pulling&&handled.tension<.72;tick(handled,.05);}
    expect(handled.phase).toBe('landed');
  });
  it('pauses all simulation and rejects background time jumps',()=>{
    const s=ready();cast(s);s.paused=true;const before=JSON.stringify(s);tick(s,100);expect(JSON.stringify(s)).toBe(before);
    s.paused=false;tick(s,100);expect(s.elapsed).toBe(.1);expect(s.phase).toBe('drifting');
  });
  it('keeps a three-fish household basket, records releases and never duplicates a catch',()=>{
    const s=ready();for(let i=0;i<3;i++){catchFish(s);s.fish!.species='perch';decideCatch(s,true);decideCatch(s,true);anotherDrift(s);}
    catchFish(s);s.fish!.species='perch';decideCatch(s,true);expect(s.phase).toBe('landed');expect(keptCount(s)).toBe(3);
    decideCatch(s,false);expect(s.journal).toHaveLength(4);expect(s.journal[3].kept).toBe(false);
    returnHome(s);expect(ending(s).title).toBe('Save a place at the table');
  });
  it('ends after eight used drifts and permits returning with an empty basket',()=>{
    const s=ready();for(let i=0;i<MAX_CASTS;i++){cast(s);openChart(s);visit(s,'reeds');}
    expect(s.casts).toBe(MAX_CASTS);expect(s.phase).toBe('chart');cast(s);expect(s.casts).toBe(MAX_CASTS);
    returnHome(s);expect(s.phase).toBe('home');expect(ending(s).title).toBe('Still a good day');
  });
  it('clamps depth and prevents catch/strike/travel actions from invalid phases',()=>{
    const s=createState();cast(s);strike(s);visit(s,'reef');decideCatch(s,true);expect(s.phase).toBe('dock');expect(s.casts).toBe(0);
    launch(s);visit(s,'reeds');setDepth(s,999);expect(s.depth).toBe(5);setDepth(s,-10);expect(s.depth).toBe(.5);
    cast(s);visit(s,'islands');expect(s.ground).toBe('reeds');strike(s);expect(s.phase).toBe('drifting');
  });
  it('changes range with marina and protects home charge through repeated travel',()=>{
    const west=createState();launch(west);expect(canVisit(west,'kelleys')).toBe(false);
    visit(west,'kelleys');expect(west.charge).toBe(100);expect(west.phase).toBe('chart');
    const east=createState();east.marina='eastharbor';launch(east);expect(canVisit(east,'kelleys')).toBe(true);
    for(let i=0;i<20;i++)for(const g of grounds){visit(east,g.id);expect(east.charge).toBeGreaterThanOrEqual(returnReserve(east));}
    const remaining=east.charge-returnReserve(east);returnHome(east);expect(east.charge).toBe(remaining);returnHome(east);expect(east.charge).toBe(remaining);
  });
  it('makes season/cloud matter without farming charge through menus or bite waiting',()=>{
    const sunny=ready(),cloudy=ready();cloudy.weather='haze';cloudy.season='autumn';
    cast(sunny);cast(cloudy);step(sunny,5);step(cloudy,5);expect(sunny.solarGained).toBeGreaterThan(cloudy.solarGained*10);
    step(sunny,35);expect(sunny.phase).toBe('bite');const charge=sunny.charge;step(sunny,500);expect(sunny.charge).toBe(charge);
    openChart(sunny);for(let i=0;i<10;i++){visit(sunny,'reeds');openChart(sunny);}step(sunny,500);expect(sunny.charge).toBe(charge);
    const long=ready();setDepth(long,.5);cast(long);step(long,100);expect(long.solarGained).toBeCloseTo(4);expect(long.charge).toBeLessThanOrEqual(100);
  });
  it('changes the catch mix with tackle and bait and repairs incompatible bait selections',()=>{
    const s=ready();const bottom=catchWeights(s);setRig(s,'float');setBait(s,'worms');expect(catchWeights(s).bluegill).toBeGreaterThan(bottom.bluegill!);
    setBait(s,'plastic');expect(s.bait).toBe('worms');setRig(s,'walleye');setBait(s,'plastic');expect(catchWeights(s).bass).toBeGreaterThan(bottom.bass!);
    setRig(s,'perch');expect(s.bait).toBe('minnows');
    const seen=new Set();for(let seed=1;seed<180;seed++){const outing=ready();outing.seed=seed*137;outing.phase='bite';strike(outing);seen.add(outing.fish!.species);}
    expect(seen.size).toBeGreaterThanOrEqual(6);expect(seen.has('snakehead')).toBe(false);
  });
  it('scores only the best fish per species, equally for kept and released fish',()=>{
    const s=ready();for(const [length,kept] of [[25,true],[26,false],[24,true]] as const){s.phase='landed';s.fish={species:'perch',length,points:50+length*5,ground:'reeds',kept:false,logged:false};decideCatch(s,kept);}
    expect(score(s)).toBe(180);expect(s.journal).toHaveLength(3);decideCatch(s,false);expect(score(s)).toBe(180);
  });
  it('gates snakehead behind explicit fiction and records invasive encounters',()=>{
    const s=ready();expect(catchWeights(s).snakehead).toBeUndefined();s.speculative=true;expect(catchWeights(s).snakehead).toBeGreaterThan(0);
    s.phase='landed';s.fish={species:'snakehead',length:50,points:200,ground:'reeds',kept:false,logged:false};
    decideCatch(s,true);expect(s.phase).toBe('landed');decideCatch(s,false);expect(s.journal[0].logged).toBe(true);expect(keptCount(s)).toBe(0);expect(score(s)).toBe(200);
    const reset=createState();expect(reset.speculative).toBe(false);expect(reset.charge).toBe(100);expect(score(reset)).toBe(0);
  });
});
