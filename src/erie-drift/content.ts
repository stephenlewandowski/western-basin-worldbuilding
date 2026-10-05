/** Real place names; schematic positions and all numerical fishing rules are authored. */
export type Species = 'perch'|'walleye'|'bass'|'bluegill'|'drum'|'whiteperch'|'goby'|'snakehead';
export type Rig = 'perch'|'walleye'|'spinner'|'float';
export type Bait = 'minnows'|'worms'|'plastic';
export type GroundId = 'reeds'|'intake'|'reef'|'islands'|'kelleys'|'harbor';
export type MarinaId = 'maumee'|'eastharbor';
export type Season = 'spring'|'summer'|'autumn';
export interface Ground {id:GroundId;name:string;subtitle:string;depth:number;walleyeDepth:number;x:number;y:number;perchLane:number;walleyeLane:number;detail:string;voice:string;habitat:'bay'|'open'|'rock';}
export const grounds:Ground[] = [
  {id:'reeds',name:'Maumee Bay',subtitle:'Marsh edge · mixed panfish',depth:5,walleyeDepth:2.5,x:230,y:358,perchLane:0,walleyeLane:1,habitat:'bay',detail:'Off Maumee Bay State Park, marsh birds work the shoreline. Try a light float and worms for small fish, or work the bottom with minnows.',voice:'Jo: “I promised fish. I also brought beans. That’s called experience.”'},
  {id:'intake',name:'Toledo Intake',subtitle:'Open water · perch country',depth:6,walleyeDepth:3,x:380,y:220,perchLane:0,walleyeLane:1,habitat:'open',detail:'The low intake is a familiar landmark, well away from our drift. Old fishing reports talk about perch and minnows here. The fish have not read them.',voice:'Jo: “Everyone knows this spot. The fish are the only ones who won’t give directions.”'},
  {id:'reef',name:'Niagara Reef',subtitle:'Western reef country · walleye',depth:7,walleyeDepth:3.5,x:490,y:348,perchLane:-1,walleyeLane:0,habitat:'rock',detail:'Stone changes the sounder trace. A jig or spinner can find walleye; a soft-plastic jig also interests bass. Sheepshead have their own plans.',voice:'Jo: “Your grandfather had a secret spot here. So did everyone else’s grandfather.”'},
  {id:'islands',name:'South Bass',subtitle:'Island water · bass and walleye',depth:8,walleyeDepth:4.5,x:620,y:182,perchLane:1,walleyeLane:-1,habitat:'rock',detail:'South Bass rises behind the drift. The island docks are stirring. Work a jig past the rock or suspend minnows for a different sort of bite.',voice:'Jo: “One more drift is how every fishing trip gets its name.”'},
  {id:'kelleys',name:'Kelleys Island',subtitle:'Island shoals · smallmouth water',depth:8,walleyeDepth:4,x:825,y:235,perchLane:1,walleyeLane:0,habitat:'rock',detail:'The shoals around Kelleys have generations of smallmouth stories. Soft plastic on a jig is a good place to start. No one promises the next fish.',voice:'Jo: “A bass this far from home owes us a photograph.”'},
  {id:'harbor',name:'East Harbor',subtitle:'Sheltered edge · bluegill and perch',depth:3,walleyeDepth:1.5,x:735,y:370,perchLane:0,walleyeLane:-1,habitat:'bay',detail:'A sheltered East Harbor edge: a float, a piece of worm, and a very serious little bluegill. The marina of the same name sits on West Harbor.',voice:'Jo: “Small water. Large opinions about bait.”'},
];
export const marinas = {
  maumee:{name:'Maumee Bay Marina',x:175,y:465,note:'Depart a lodge slip beside Maumee Bay State Park. Good for the intake and western grounds.'},
  eastharbor:{name:'East Harbor State Park Marina',x:652,y:474,note:'Depart from West Harbor, nearer South Bass and Kelleys Island.'},
};
export const seasons:Record<Season,{name:string;solar:number}>={spring:{name:'Late spring',solar:.72},summer:{name:'Summer',solar:1},autumn:{name:'Early autumn',solar:.48}};
export const rigs:Record<Rig,{name:string;note:string;baits:Bait[]}>={
  perch:{name:'Bottom spreader',note:'Near-bottom taps; minnows favor perch, worms invite more mixed catches.',baits:['minnows','worms']},
  walleye:{name:'Drift jig',note:'Work suspended fish with minnows, or rocky water with soft plastic for bass.',baits:['minnows','plastic','worms']},
  spinner:{name:'Spinner harness',note:'A moving presentation through the drift; nightcrawlers favor walleye.',baits:['worms','minnows']},
  float:{name:'Light float',note:'Shallow presentation; worms favor bluegill in the bays. Less effective offshore.',baits:['worms','minnows']},
};
export const baits:Record<Bait,string>={minnows:'Minnows',worms:'Nightcrawlers',plastic:'Soft-plastic tube'};
export const fishInfo:Record<Species,{name:string;min:number;range:number;factor:number;note:string;invasive?:boolean}>={
  perch:{name:'Yellow perch',min:19,range:15,factor:5,note:'Gold stripes and an indignant eye. Jo approves.'},
  walleye:{name:'Walleye',min:38,range:33,factor:3,note:'A pale eye, a flash of olive gold. Jo puts the sandwich down.'},
  bass:{name:'Smallmouth bass',min:24,range:24,factor:4,note:'Bronze shoulders. It has objections to the entire afternoon.'},
  bluegill:{name:'Bluegill',min:12,range:13,factor:6,note:'Small fish, enormous confidence. “That one thinks it owns the boat.”'},
  drum:{name:'Freshwater drum / sheepshead',min:28,range:36,factor:3,note:'Silver, stubborn, and nobody’s consolation prize. That was a proper pull.'},
  whiteperch:{name:'White perch',min:15,range:16,factor:5,note:'An established nonnative fish. A silver surprise among the yellow perch.',invasive:true},
  goby:{name:'Round goby',min:7,range:11,factor:8,note:'Small, bottom-hugging and invasive. This encounter goes into the dock record.',invasive:true},
  snakehead:{name:'Northern snakehead',min:35,range:40,factor:3,note:'Speculative 2075 encounter, enabled for this outing. This is not a record of an established Lake Erie population.',invasive:true},
};
