import bridge from '../../assets/atlas/sketchbook/bridge.webp';
import glass from '../../assets/atlas/sketchbook/glass-and-brick.webp';
import river from '../../assets/atlas/sketchbook/working-river.webp';
import machines from '../../assets/atlas/sketchbook/workshop-machines.webp';
import workers from '../../assets/atlas/sketchbook/river-workers.webp';
import maker from '../../assets/atlas/sketchbook/rural-maker.webp';
import wetland from '../../assets/atlas/sketchbook/wetland-boardwalk.webp';
import station from '../../assets/atlas/sketchbook/field-station.webp';
import archive from '../../assets/atlas/sketchbook/biological-archive.webp';
import sheet1 from '../../assets/atlas/sketchbook/sheet-01.webp';
import sheet2 from '../../assets/atlas/sketchbook/sheet-02.webp';
import sheet3 from '../../assets/atlas/sketchbook/sheet-03.webp';

const base=import.meta.env.BASE_URL;
const path=(suffix:string)=>`${base}${suffix}`;
const original=(sheet:number)=>`https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/assets/concept_art/glasspunk_toledo_sketchbook_sheet_0${sheet}.png`;
type Topic='all'|'places'|'equipment'|'people';
interface Sketch {id:string;topic:Exclude<Topic,'all'>;title:string;image:string;alt:string;sheet:number;region:string;text:string;link:string;label:string;}
const sketches:Sketch[]=[
 {id:'bridge',topic:'places',title:'The bridge as a civic room',image:bridge,alt:'Ink-and-wash concept of a Toledo-inspired bridge with illuminated towers and a city beyond',sheet:2,region:'Glass City Core',text:'An inherited river crossing becomes a place for light, movement and public life. The old structure stays recognizable beneath the future additions.',link:'atlas/glass-city-2075/',label:'Explore Glass City'},
 {id:'glass-and-brick',topic:'places',title:'New glass, old brick',image:glass,alt:'Early skyline study combines glass towers, reused brick workshops and a riverside promenade',sheet:3,region:'Glass City Core',text:'Glass towers share the waterfront with reused workshops and a riverwalk. Material contrast gives the city a past as well as a future.',link:'atlas/glass-city-2075/',label:'Walk into Glass City'},
 {id:'working-river',topic:'places',title:'The river is a main street',image:river,alt:'Sketchbook river scene with small freight boats, bank paths and waterside shelters',sheet:3,region:'Maumee River Commons',text:'Freight boats, market landings and everyday river life occupy the same water. A small dock could become a meeting place or the start of a journey.',link:'maps/?region=river',label:'Follow the Maumee'},
 {id:'workshop-machines',topic:'equipment',title:'Machines with somewhere to be repaired',image:machines,alt:'Sketchbook equipment spread with underwater vehicle, shallow freight boat, expedition vehicle, field drones and a wheeled workshop robot',sheet:1,region:'River, coast & industrial belt',text:'Small craft and work machines look assembled, reachable and repairable. Their cases, wheels and attachment points are useful starting shapes for games and stories.',link:'atlas/industrial-metabolism-2075/',label:'Enter the working hall'},
 {id:'river-workers',topic:'people',title:'The people who keep it running',image:workers,alt:'Four early character silhouettes: river technician with tablet, workshop apprentice, ecologist and systems officer',sheet:3,region:'Across the basin',text:'A field notebook, work jacket, goggles and a net make occupations readable before anyone speaks. These are early role and clothing studies, with no fixed cast or biographies.',link:'atlas/basin-reading-hall/#story',label:'Meet someone at the Reading Hall'},
 {id:'rural-maker',topic:'people',title:'The rural maker',image:maker,alt:'Early rural maker portrait in a cap, goggles, work vest and rolled sleeves',sheet:2,region:'Black Swamp Country',text:'A practical silhouette from the former Frontier Arc: somebody who can mend equipment, improvise a part and keep a workshop going. That maker tradition now sits within Black Swamp Country.',link:'atlas/maumee-bio-ag-2075/',label:'Visit the working fields'},
 {id:'wetland-boardwalk',topic:'places',title:'A path into the wetland',image:wetland,alt:'Wetland concept with a boardwalk, small observation shelters and wooded water edges',sheet:1,region:'Black Swamp Country',text:'Low paths and small shelters bring human activity close to a wetland without making it a blank wilderness. This is an imagined landscape, without a mapped historical boundary.',link:'maps/?region=swamp',label:'Explore Black Swamp Country'},
 {id:'field-station',topic:'equipment',title:'An instrument with a place in the landscape',image:station,alt:'Sketch of a raised field sensor tower with small instrument boxes and antennas at a wetland edge',sheet:1,region:'Black Swamp Country',text:'An exposed mast and reachable instrument boxes suggest a place someone must visit, inspect and maintain. The equipment is a design idea, without demonstrated sensing coverage.',link:'atlas/climate-thermal-regime/',label:'Explore real climate records'},
 {id:'biological-archive',topic:'equipment',title:'A small archive, a long obligation',image:archive,alt:'Early imagined cylindrical biological-material archive under a protective cap',sheet:1,region:'Black Swamp Country',text:'A compact archive proposes a tangible object for long stewardship. What goes inside, who looks after it and whether it preserves anything remain open design questions.',link:'atlas/maumee-bio-ag-2075/',label:'Explore the agricultural futurescape'},
];
const sheets=[sheet1,sheet2,sheet3];
const topicLabels:Record<Topic,string>={all:'All sketches',places:'Places & buildings',equipment:'Equipment',people:'People'};
function topicFromUrl():Topic {const topic=new URLSearchParams(location.search).get('topic');return topic&&Object.hasOwn(topicLabels,topic)?topic as Topic:'all';}

export function sketchbookPage():string {
 const topic=topicFromUrl();
 return `<section class="plain-hero section-shell sketchbook-intro"><p class="eyebrow accent">FROM THE ORIGINAL SKETCHBOOKS</p><h1>A world in<br><em>working drawings.</em></h1><p>People, small machines, river crossings and wetland paths from the project’s first three sketchbook sheets. Explore the shapes that helped the basin become a place for stories and games.</p><p class="sketchbook-note">Early generated concept art. The handwritten notes are part of the original images; names, dates, technology claims and old regional maps may differ from the current Atlas.</p></section>
 <section class="section-shell sketchbook-collection" aria-labelledby="collection-title"><div class="section-head"><div><h2 id="collection-title">Find a shape<br>worth following.</h2></div><p>Inspect a drawing, see the sheet it came from, or follow it into a place developed in the Atlas.</p></div><div class="sketchbook-filters" role="group" aria-label="Sketchbook subjects">${(Object.keys(topicLabels) as Topic[]).map(id=>`<button type="button" data-sketch-topic="${id}" aria-pressed="${id===topic}">${topicLabels[id]}</button>`).join('')}</div><p class="sketchbook-count" id="sketch-count" role="status"></p><div class="sketchbook-grid">${sketches.map(item=>`<article class="sketchbook-card" id="${item.id}" data-sketch-card="${item.topic}" ${topic!=='all'&&topic!==item.topic?'hidden':''}><button type="button" class="sketchbook-image" data-sketch-open="${item.id}" aria-label="Inspect ${item.title}"><img src="${item.image}" alt="${item.alt}" loading="lazy"/><span>Inspect sketch ↗</span></button><div class="sketchbook-copy"><p class="eyebrow">${item.region}</p><h3>${item.title}</h3><p>${item.text}</p><a class="text-link" href="${path(item.link)}">${item.label} ↗</a></div></article>`).join('')}</div></section>
 <section class="section-shell sketchbook-history"><p class="eyebrow">REGIONAL IDEAS THAT GREW TOGETHER</p><h2>From Frontier Arc<br>to <em>Black Swamp Country.</em></h2><p>The earliest sheets divided the world into six regions. Frontier Arc held farms, workshops, cooperative energy and rural maker culture; Black Swamp Preserve emphasized wetlands and ecological memory. Those themes now share <a href="${path('maps/?region=swamp')}">Black Swamp Country</a> in the five-region Atlas.</p><p>The original labels stay on the sheets so you can see how the idea changed. Their map outlines are exploratory drawings, rather than the geography used by the current map.</p></section>
 <section class="section-shell sketchbook-sheets" aria-labelledby="sheets-title"><div class="section-head"><div><p class="eyebrow">THE PAGES THEY CAME FROM</p><h2 id="sheets-title">Open the full sheets.</h2></div><p>Dense notes, alternative people and superseded maps are preserved together. Character names and roles vary between sheets; these drawings do not establish identities for the current stories.</p></div><div class="sheet-grid">${sheets.map((image,i)=>`<figure><button type="button" class="sketchbook-image" data-sketch-open="sheet-${i+1}" aria-label="Inspect full sketchbook sheet ${i+1}"><img src="${image}" alt="Original exploratory sketchbook sheet ${i+1}, combining early regions, architectural ideas, people and equipment" loading="lazy"/><span>Open sheet ${i+1} ↗</span></button><figcaption>Original sheet ${i+1} · early concept art. <a href="${original(i+1)}">Source PNG and history ↗</a></figcaption></figure>`).join('')}</div><p class="sketchbook-note">The sheets supply visual ideas, rather than scientific evidence, engineering specifications or current navigation. Explore <a href="${path('maps/')}">the basin map</a> and <a href="${path('methods/')}">Methods</a> for those distinctions. <a href="https://github.com/stephenlewandowski/western-basin-worldbuilding/blob/main/assets/atlas/sketchbook/README.md">Crop and source record ↗</a>.</p></section>
 <dialog id="sketch-viewer" class="sketch-viewer" aria-labelledby="sketch-viewer-title"><div class="sketch-viewer-head"><h2 id="sketch-viewer-title"></h2><button type="button" id="sketch-close">Close</button></div><div class="sketch-viewer-scroll"><img id="sketch-viewer-image" alt=""/></div><p id="sketch-viewer-note"></p><div class="sketch-viewer-links"><button type="button" id="sketch-full-sheet">See the full sheet</button><button type="button" id="sketch-zoom" aria-pressed="false" hidden>Zoom full sheet</button><a id="sketch-original" target="_blank" rel="noopener">Original PNG and history ↗</a></div></dialog>`;
}

export function mountSketchbook(){
 const dialog=document.getElementById('sketch-viewer') as HTMLDialogElement;
 let opener:HTMLElement|null=null,currentSheet=1;
 const show=(id:string)=>{
  const item=sketches.find(s=>s.id===id),full=!item;
  currentSheet=item?.sheet??Number(id.split('-')[1]);
  document.getElementById('sketch-viewer-title')!.textContent=item?.title??`Original sheet ${currentSheet}`;
  const image=document.getElementById('sketch-viewer-image') as HTMLImageElement;
  image.src=item?.image??sheets[currentSheet-1];image.alt=item?.alt??`Full exploratory sketchbook sheet ${currentSheet}`;
  document.getElementById('sketch-viewer-note')!.textContent=full?'Early concept art. The original six-region maps and handwritten claims are preserved as history. Frontier Arc and Black Swamp Preserve now sit within Black Swamp Country.':`${item!.text} Source: original sheet ${currentSheet}.`;
  document.getElementById('sketch-full-sheet')!.hidden=full;
  const zoom=document.getElementById('sketch-zoom')!;zoom.hidden=!full;zoom.textContent='Zoom full sheet';zoom.setAttribute('aria-pressed','false');
  dialog.classList.remove('is-zoomed');const scroll=dialog.querySelector('.sketch-viewer-scroll')!;scroll.scrollTop=0;scroll.scrollLeft=0;
  (document.getElementById('sketch-original') as HTMLAnchorElement).href=original(currentSheet);
  if(!dialog.open)dialog.showModal();
  document.getElementById('sketch-close')!.focus();
 };
 const update=(topic:Topic)=>{
  let count=0;document.querySelectorAll<HTMLElement>('[data-sketch-card]').forEach(card=>{card.hidden=topic!=='all'&&card.dataset.sketchCard!==topic;if(!card.hidden)count++;});
  document.querySelectorAll<HTMLElement>('[data-sketch-topic]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.sketchTopic===topic)));
  document.getElementById('sketch-count')!.textContent=`${count} ${count===1?'drawing':'drawings'} · ${topicLabels[topic]}`;
 };
 document.querySelectorAll<HTMLButtonElement>('[data-sketch-topic]').forEach(button=>button.addEventListener('click',()=>{const topic=button.dataset.sketchTopic as Topic;update(topic);const url=new URL(location.href);if(topic==='all')url.searchParams.delete('topic');else url.searchParams.set('topic',topic);history.replaceState(null,'',url);}));
 document.querySelectorAll<HTMLButtonElement>('[data-sketch-open]').forEach(button=>button.addEventListener('click',()=>{opener=button;show(button.dataset.sketchOpen!);}));
 document.getElementById('sketch-close')!.addEventListener('click',()=>dialog.close());
 document.getElementById('sketch-full-sheet')!.addEventListener('click',()=>show(`sheet-${currentSheet}`));
 document.getElementById('sketch-zoom')!.addEventListener('click',()=>{const zoomed=dialog.classList.toggle('is-zoomed'),button=document.getElementById('sketch-zoom')!;button.setAttribute('aria-pressed',String(zoomed));button.textContent=zoomed?'Fit full sheet':'Zoom full sheet';});
 dialog.addEventListener('close',()=>opener?.focus({preventScroll:true}));
 update(topicFromUrl());
}
