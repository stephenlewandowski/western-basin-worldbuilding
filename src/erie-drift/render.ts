import { grounds, marinas, rigs, baits, speciesName, canVisit, getGround, targetDepth, targetLane, type State, type Species } from './logic';

const W=960,H=600;
function path(c:CanvasRenderingContext2D,points:number[][],fill:string,stroke?:string){
  c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=fill;c.fill();
  if(stroke){c.strokeStyle=stroke;c.lineWidth=2;c.stroke();}
}
function ellipse(c:CanvasRenderingContext2D,x:number,y:number,rx:number,ry:number,color:string|CanvasGradient){c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fillStyle=color;c.fill();}
function text(c:CanvasRenderingContext2D,value:string,x:number,y:number,size=16,color='#f0e5ca',font='sans-serif'){c.font=`${size}px ${font}`;c.fillStyle=color;c.fillText(value,x,y);}
function boat(c:CanvasRenderingContext2D,x:number,y:number,angle:number,scale=1){
  c.save();c.translate(x,y);c.rotate(angle);c.scale(scale,scale);
  ellipse(c,6,8,20,41,'#071f294a');
  path(c,[[0,-43],[18,-16],[18,26],[12,36],[-12,36],[-18,26],[-18,-16]],'#eee4c9','#253b3f');
  path(c,[[0,-35],[12,-13],[12,24],[-12,24],[-12,-13]],'#a06e42');
  for(let y=-8;y<26;y+=7){c.strokeStyle='#684a35';c.beginPath();c.moveTo(-11,y);c.lineTo(11,y);c.stroke();}
  c.fillStyle='#234d55';c.fillRect(-9,4,18,6);c.fillStyle='#dea44d';c.fillRect(-14,-17,28,20);
  c.fillStyle='#204863';c.fillRect(-12,-15,24,15);c.strokeStyle='#7ca5b8';c.lineWidth=.5;for(let i=0;i<4;i++)c.strokeRect(-12+i*6,-15,6,15);c.fillStyle='#f1d488';c.fillRect(-14,-17,28,2);c.strokeStyle='#6f643e';c.strokeRect(-14,-17,28,20);
  c.fillStyle='#36565b';c.fillRect(-5,31,10,12);ellipse(c,-9,20,4,6,'#efe4c7');ellipse(c,9,20,4,6,'#efe4c7');
  c.restore();
}
export function drawFish(c:CanvasRenderingContext2D,species:Species,x:number,y:number,scale=1){
  if(species!=='perch'&&species!=='walleye'){
    c.save();c.translate(x,y);c.scale(scale,scale);
    const long=species==='snakehead',deep=species==='bluegill'||species==='drum'||species==='whiteperch';
    const color=({bass:'#9b955b',bluegill:'#889666',drum:'#a7b8b0',whiteperch:'#c0cdc2',goby:'#9a9279',snakehead:'#768566'})[species];
    const ry=long?24:deep?50:34;
    path(c,[[-84,0],[-135,-33],[-123,0],[-135,32],[-84,13]],color,'#3c5751');
    path(c,[[-75,-ry+6],[-62,-ry-22],[-42,-ry-12],[-25,-ry-25],[0,-ry-18],[62,-ry+7]],color,'#3c5751');
    const grad=c.createLinearGradient(0,-ry,0,ry);grad.addColorStop(0,'#3f5d56');grad.addColorStop(.45,color);grad.addColorStop(1,'#eee1b5');
    ellipse(c,0,0,long?125:105,ry,grad);
    if(species==='bass'||species==='snakehead'||species==='goby')for(let i=0;i<30;i++)ellipse(c,-84+(i*37)%170,-15+(i*17)%30,5,3,'#324c3d88');
    if(species==='bluegill'){ellipse(c,52,-5,12,17,'#264d57');ellipse(c,33,18,24,12,'#cba05e');}
    if(species==='goby')ellipse(c,-28,-ry-8,6,6,'#253e34');
    path(c,[[-12,16],[8,ry+24],[27,20]],color,'#3c5751');
    ellipse(c,82,-12,8,8,'#e2d89e');ellipse(c,84,-12,4,5,'#1c3030');
    c.beginPath();c.moveTo(90,9);c.lineTo(long?123:104,5);c.strokeStyle='#2a4942';c.lineWidth=2;c.stroke();c.restore();return;
  }
  const perch=species==='perch';c.save();c.translate(x,y);c.scale(scale,scale);
  const body=c.createLinearGradient(0,-40,0,40);body.addColorStop(0,perch?'#37695a':'#536149');body.addColorStop(.5,perch?'#d6bd54':'#c5b776');body.addColorStop(1,'#efe2af');
  path(c,[[-102,0],[-146,-40],[-134,-5],[-148,33],[-103,14]],perch?'#c38c36':'#978751','#454f3e');
  path(c,[[-56,-20],[-47,-65],[-33,-45],[-20,-70],[-10,-44],[2,-62],[17,-39],[28,-50],[41,-21]],perch?'#788952':'#787e51','#354d3d');
  for(let i=0;i<6;i++){c.beginPath();c.moveTo(-46+i*15,-24);c.lineTo(-46+i*15,-48-(i%2)*9);c.strokeStyle='#e4d68788';c.stroke();}
  ellipse(c,0,0,112,38,body);path(c,[[98,-19],[125,-5],[120,5],[97,20]],perch?'#bcb25c':'#b1b280');
  if(perch){for(let i=0;i<6;i++){c.save();c.globalAlpha=.75;path(c,[[-77+i*28,-26],[-68+i*28,-32],[-61+i*28,23],[-71+i*28,27]],'#304d40');c.restore();}}
  else for(let i=0;i<55;i++)ellipse(c,-88+(i*29)%170,-22+(i*17)%40,2.5,1.6,'#4c604677');
  path(c,[[-9,16],[11,58],[32,28]],perch?'#d39738':'#aa9a66','#6e7750');
  path(c,[[-70,24],[-62,51],[-35,28]],perch?'#d79e45':'#a29865');
  c.beginPath();c.ellipse(67,-1,14,29,.2,-1.35,1.3);c.strokeStyle='#647047';c.lineWidth=2;c.stroke();
  ellipse(c,93,-13,8,8,'#d9d492');ellipse(c,95,-13,4,5,'#182c2d');ellipse(c,96,-15,1.5,1.5,'#fff4d1');
  c.beginPath();c.moveTo(109,2);c.lineTo(124,0);c.strokeStyle='#415744';c.stroke();c.restore();
}
export class Renderer {
  private c:CanvasRenderingContext2D;
  private boatX=135;private boatY=453;
  constructor(private canvas:HTMLCanvasElement,private art:HTMLImageElement){
    canvas.width=W*2;canvas.height=H*2;this.c=canvas.getContext('2d')!;this.c.scale(2,2);
  }
  hit(clientX:number,clientY:number){const r=this.canvas.getBoundingClientRect();const x=(clientX-r.left)/r.width*W,y=(clientY-r.top)/r.height*H;return grounds.find(g=>Math.hypot(x-g.x,y-g.y)<72)?.id;}
  draw(s:State,time:number,reduced=false){
    const c=this.c,t=reduced?0:time;
    c.clearRect(0,0,W,H);
    if(['chart','rig','dock','home'].includes(s.phase))this.chart(s,t);else this.water(s,t);
    if(s.paused){c.fillStyle='#102d35bc';c.fillRect(0,0,W,H);c.textAlign='center';text(c,'Taking a breather',480,285,38,'#f6e6bd','Georgia');text(c,'Resume whenever you’re ready.',480,325,19);c.textAlign='left';}
  }
  private chart(s:State,t:number){
    const c=this.c,gr=c.createLinearGradient(0,0,960,600);gr.addColorStop(0,'#1c6470');gr.addColorStop(.6,'#277c86');gr.addColorStop(1,'#173f55');c.fillStyle=gr;c.fillRect(0,0,W,H);
    // Hand-drawn bathymetric contours belong to this composite game map.
    for(let j=0;j<9;j++){c.beginPath();c.moveTo(20+j*35,620);c.bezierCurveTo(170+j*18,370-j*12,230+j*70,130+j*27,1020,40+j*60);c.strokeStyle=j%2?'#bcd1b015':'#b9d8c525';c.lineWidth=2;c.stroke();}
    for(let i=0;i<85;i++){const x=(i*127)%970,y=(i*73)%610;const shift=Math.sin(t*.25+i)*4;c.strokeStyle='#c9e2cb20';c.lineWidth=1.3;c.beginPath();c.moveTo(x+shift,y);c.quadraticCurveTo(x+12,y-3,x+25+shift,y);c.stroke();}
    // Compressed west-to-east geography. No plotted routes or real bathymetry.
    path(c,[[0,320],[85,355],[112,400],[190,448],[300,461],[378,425],[485,453],[568,432],[624,456],[652,419],[671,441],[703,445],[742,424],[780,454],[832,431],[887,400],[960,403],[960,600],[0,600]],'#a4ac7a','#decea0');
    path(c,[[0,367],[95,415],[165,477],[293,491],[379,458],[475,484],[566,473],[640,492],[740,482],[836,476],[960,451],[960,600],[0,600]],'#728d6e');
    for(let i=0;i<35;i++){const x=20+(i*37)%370,y=483+(i*17)%63;c.strokeStyle='#3c5a45';c.beginPath();c.moveTo(x,y);c.lineTo(x+3,y-10);c.moveTo(x,y);c.lineTo(x-4,y-7);c.stroke();}
    for(const [x,y,rx,ry] of [[628,117,35,48],[570,60,24,15],[826,162,55,27]]){ellipse(c,x,y,rx+7,ry+7,'#d7cc9a77');ellipse(c,x,y,rx,ry,'#aab586');}
    // Intake landmark, shore town, and the inherited working waterfront.
    ellipse(c,353,177,17,7,'#d3d3ba');c.fillStyle='#a7b9ae';c.fillRect(337,166,32,12);ellipse(c,353,166,16,5,'#e7dbc0');
    for(let i=0;i<6;i++){const x=54+i*19,y=548+(i%2)*7;c.fillStyle='#385a53';c.fillRect(x,y,14,20);path(c,[[x-1,y],[x+7,y-6],[x+15,y]],'#ddd0a4');}
    text(c,'TOLEDO / GLASS CITY',26,537,14,'#f0e6c5','Georgia');text(c,'MAUMEE BAY STATE PARK',245,523,13,'#203f3d');text(c,'MARSH COAST',383,552,13,'#dce0be');text(c,'MARBLEHEAD',790,487,13,'#233f3d');
    c.textAlign='center';text(c,'W E S T E R N   L A K E   E R I E',505,75,18,'#d3e3ccaa','Georgia');c.textAlign='left';
    text(c,'N ↑',884,43,20,'#f2e5b6','Georgia');
    const selected=getGround(s),home=marinas[s.marina];
    if(s.phase!=='dock'&&s.phase!=='home'){
      c.setLineDash([5,8]);c.lineWidth=2;c.strokeStyle='#e2c17b66';c.beginPath();c.moveTo(home.x,home.y);c.lineTo(selected.x,selected.y);c.stroke();c.setLineDash([]);
    }
    for(const [id,m] of Object.entries(marinas)){
      c.fillStyle=id===s.marina?'#edc77c':'#c0cbb5';c.fillRect(m.x-9,m.y-9,18,18);text(c,'M',m.x-6,m.y+5,14,'#193c42');
      c.textAlign='center';text(c,id==='maumee'?'Maumee Bay Marina':'East Harbor Marina',m.x,m.y+33,17,'#fff0c9','Georgia');
      if(id==='eastharbor')text(c,'on West Harbor',m.x,m.y+52,12,'#dde2ca');c.textAlign='left';
    }
    for(const [i,g] of grounds.entries()){
      const chosen=g.id===s.ground&&s.visited.length>0&&s.phase!=='home';
      const reachable=canVisit(s,g.id);
      ellipse(c,g.x,g.y,chosen?51:39,chosen?25:21,chosen?'#d6d19e50':'#b6d4b126');
      c.beginPath();c.ellipse(g.x,g.y,47,25,-.2,0,Math.PI*2);c.strokeStyle=chosen?'#f4d68f':reachable?'#bed9c49c':'#b8c8c255';c.lineWidth=chosen?2:1;c.setLineDash([5,6]);c.stroke();c.setLineDash([]);
      ellipse(c,g.x,g.y,10,10,reachable?'#f3d48e':'#b1bcb5');c.textAlign='center';text(c,String(i+1),g.x,g.y+4,12,'#183d45');
      text(c,g.name,g.x,g.y+48,23,'#fff0ca','Georgia');text(c,`${g.depth} m${!reachable?' · outside budget':''}`,g.x,g.y+67,12,'#d3e0cd');c.textAlign='left';
    }
    const dest=['dock','home'].includes(s.phase)||!s.visited.length?home:{x:selected.x-35,y:selected.y-16};
    this.boatX+=(dest.x-this.boatX)*.06;this.boatY+=(dest.y-this.boatY)*.06;
    boat(c,this.boatX,this.boatY+Math.sin(t*1.4)*1.2,.5,.65);
    text(c,'ERIE DRIFT',26,44,27,'#f5e6b9','Georgia');text(c,'Familiar places. A borrowed boat.',26,69,13,'#d2e3d0');
    c.fillStyle='#112e3ec9';c.fillRect(468,562,476,25);text(c,'SCHEMATIC · DISTANCES & DEPTHS ARE GAME RULES',480,579,12,'#e4e4ce');
  }
  private water(s:State,t:number){
    const c=this.c;
    if(this.art.complete&&this.art.naturalWidth){const ratio=Math.max(W/this.art.width,H/this.art.height);c.drawImage(this.art,(W-this.art.width*ratio)/2,(H-this.art.height*ratio)/2,this.art.width*ratio,this.art.height*ratio);}
    else {const gr=c.createLinearGradient(0,0,0,H);gr.addColorStop(0,'#a4cbd0');gr.addColorStop(.39,'#ede0bd');gr.addColorStop(.4,'#448a90');gr.addColorStop(1,'#194b62');c.fillStyle=gr;c.fillRect(0,0,W,H);}
    if(s.weather!=='morning'){c.fillStyle=s.weather==='haze'?'#49637665':'#7c939a26';c.fillRect(0,0,W,H);}
    if(s.season==='autumn'){c.fillStyle='#b9985520';c.fillRect(0,0,W,H);}
    for(let i=0;i<24;i++){const y=310+i*9,x=((i*137+t*(5+i%3))%1100)-80;c.strokeStyle='#e6eee42b';c.lineWidth=1.5;c.beginPath();c.moveTo(x,y);c.quadraticCurveTo(x+40,y+3,x+90,y);c.stroke();}
    // Boat gunwale and wooden deck, close enough to give the player a body/place.
    path(c,[[0,532],[960,552],[960,600],[0,600]],'#bcb6a2','#3a5559');
    path(c,[[0,553],[960,572],[960,600],[0,600]],'#9c774d');
    for(let i=0;i<12;i++){c.strokeStyle='#4c544755';c.beginPath();c.moveTo(i*95,557);c.lineTo(i*95-30,600);c.stroke();}
    c.strokeStyle='#eadabd';c.lineWidth=7;c.beginPath();c.moveTo(0,530);c.lineTo(960,550);c.stroke();
    const bob=s.phase==='bite'?Math.sin(t*14)*13:Math.sin(t*2)*3;
    const bend=s.phase==='fight'?s.tension*76:s.phase==='bite'?18:0;
    c.beginPath();c.moveTo(790,587);c.quadraticCurveTo(650,280,510+bend,300+bob);c.strokeStyle='#102f37';c.lineWidth=8;c.stroke();
    c.beginPath();c.moveTo(790,587);c.quadraticCurveTo(650,280,510+bend,300+bob);c.strokeStyle='#cfad69';c.lineWidth=3;c.stroke();
    c.beginPath();c.moveTo(510+bend,300+bob);c.quadraticCurveTo(496+bend,356,470+bend,435+bob);c.strokeStyle='#fff4c6b0';c.lineWidth=1.5;c.stroke();
    ellipse(c,470+bend,437+bob,18+Math.sin(t*3)*3,4,'#f3eee254');
    c.fillStyle='#d68b4a';c.fillRect(752,523,12,49);ellipse(c,749,555,18,18,'#1d464f');ellipse(c,749,555,11,11,'#b3c1b1');
    c.strokeStyle='#28464a';c.lineWidth=4;c.beginPath();c.moveTo(740,558);c.lineTo(724,568);c.lineTo(719,561);c.stroke();
    c.fillStyle='#153a45c9';c.fillRect(26,25,340,64);text(c,getGround(s).name,42,54,25,'#f3e9c9','Georgia');text(c,`${rigs[s.rig].name.toUpperCase()} · ${baits[s.bait].toUpperCase()}`,43,75,12,'#d4dcbf');
    if(s.phase==='landed'&&s.fish){
      c.fillStyle='#102d3ac4';c.fillRect(0,0,W,H);
      c.fillStyle='#ebe0be';c.fillRect(228,135,504,305);c.strokeStyle='#c2a16b';c.lineWidth=2;c.strokeRect(240,147,480,281);
      drawFish(c,s.fish.species,480,290,1.15);
      c.textAlign='center';text(c,speciesName(s.fish.species),480,191,s.fish.species==='drum'?22:28,'#244947','Georgia');text(c,`${s.fish.length} cm · a good moment on the water`,480,401,18,'#4e6555');c.textAlign='left';
    }
  }
}
export function drawSounder(canvas:HTMLCanvasElement,s:State,t:number){
  const c=canvas.getContext('2d')!;const w=320,h=146;canvas.width=w*2;canvas.height=h*2;c.scale(2,2);
  c.fillStyle='#112f3b';c.fillRect(0,0,w,h);
  const ground=getGround(s),waterHeight=111,depthY=(d:number)=>15+d/ground.depth*waterHeight;
  for(let i=0;i<=ground.depth;i+=2){c.strokeStyle='#7caca72a';c.beginPath();c.moveTo(32,depthY(i));c.lineTo(w,depthY(i));c.stroke();text(c,`${i}m`,4,depthY(i)+4,10,'#b3d3c3');}
  const bottom=depthY(ground.depth);c.fillStyle='#887759';c.beginPath();c.moveTo(32,bottom);for(let x=32;x<=w;x+=5)c.lineTo(x,bottom-3*Math.sin(x*.06));c.lineTo(w,h);c.lineTo(32,h);c.fill();
  const y=depthY(targetDepth(s));
  for(let i=0;i<6;i++){const x=53+(i*41+(s.phase==='drifting'?t*4:0))%255;c.strokeStyle='#d7b86b';c.lineWidth=2;c.beginPath();c.moveTo(x-5,y+4);c.quadraticCurveTo(x,y-5,x+5,y+4);c.stroke();}
  c.setLineDash([3,3]);c.strokeStyle='#a4e4d9';c.beginPath();c.moveTo(145,15);c.lineTo(145,depthY(s.depth));c.stroke();c.setLineDash([]);ellipse(c,145,depthY(s.depth),4,4,'#d3fff0');
  text(c,'LINE',153,Math.max(25,depthY(s.depth)-3),10,'#c8eee3');
}
export function drawDrift(canvas:HTMLCanvasElement,s:State){
  const c=canvas.getContext('2d')!;canvas.width=640;canvas.height=220;c.scale(2,2);
  c.fillStyle='#1b505e';c.fillRect(0,0,320,110);
  for(let lane=-1;lane<=1;lane++){
    const y=55+lane*26;c.setLineDash([4,5]);c.strokeStyle=lane===s.lane?'#f1d58d':'#b5d4c444';c.lineWidth=lane===s.lane?2:1;c.beginPath();c.moveTo(24,y);c.lineTo(294,y);c.stroke();c.setLineDash([]);
  }
  ellipse(c,167,55+targetLane(s)*26,69,18,'#bcd0a138');
  for(let i=0;i<5;i++)ellipse(c,121+i*22,55+targetLane(s)*26+(i%2)*5,3,1.5,'#e3c579');
  boat(c,30+s.drift*245,55+s.lane*26,Math.PI/2,.25);
  text(c,'START',8,105,9,'#ceddcc');text(c,'DRIFT →',259,105,9,'#ceddcc');
}
