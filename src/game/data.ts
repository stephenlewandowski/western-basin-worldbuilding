export type RoomId = 'control' | 'corridor' | 'furnace' | 'pump' | 'terrace';
export type ItemId = 'maintenance-key' | 'fuse' | 'heat-glove';
export type ClueId = 'shift-log' | 'breaker-note' | 'station-map' | 'furnace-tag' | 'maintenance-memo' | 'furnace-scar';
export type NpcId = 'mara' | 'niko';
export type HotspotAction = 'move' | 'clue' | 'npc' | 'locker' | 'console' | 'case-review' | 'plain' | 'service-note' | 'valve' | 'pump' | 'dispatch' | 'view';
export type ServiceNoteId = 'pump-card' | 'route-board' | 'dispatch-card';
export type TheoryId = 'industrial-accident' | 'worker-sabotage' | 'management-cover-up';
export type CaseEvidenceId = ClueId | 'mara-testimony' | 'niko-report' | 'niko-silence' | 'repair-outcome';
export type CaseDecision = 'report' | 'conceal' | 'postpone';

export interface Rect { x: number; y: number; width: number; height: number; }

export interface Hotspot {
  id: string;
  label: string;
  rect: Rect;
  action: HotspotAction;
  target?: RoomId;
  clueId?: ClueId;
  itemId?: ItemId;
  npcId?: NpcId;
  noteId?: ServiceNoteId;
}

export interface Room {
  id: RoomId;
  name: string;
  description: string;
  hotspots: Hotspot[];
}

export interface Clue {
  id: ClueId;
  title: string;
  text: string;
}

export interface Item {
  id: ItemId;
  label: string;
  description: string;
}

export const COLORS = {
  black: '#000000',
  cyan: '#55ffff',
  magenta: '#ff55ff',
  white: '#ffffff',
  dim: '#ffffff',
} as const;

export const rooms: Record<RoomId, Room> = {
  control: {
    id: 'control',
    name: 'CONTROL ROOM',
    description: 'Mara needs the lights back before the morning handoff. Start with the shift log.',
    hotspots: [
      { id: 'console', label: 'CONTROL CONSOLE', rect: { x: 28, y: 66, width: 93, height: 64 }, action: 'console' },
      { id: 'shift-log', label: 'SHIFT LOG', rect: { x: 146, y: 71, width: 38, height: 38 }, action: 'clue', clueId: 'shift-log' },
      { id: 'maintenance-memo', label: 'DEFERRED MAINTENANCE MEMO', rect: { x: 190, y: 42, width: 34, height: 19 }, action: 'clue', clueId: 'maintenance-memo' },
      { id: 'case-review', label: 'CASE REVIEW TERMINAL', rect: { x: 190, y: 67, width: 34, height: 49 }, action: 'case-review' },
      { id: 'mara', label: 'MARA, STATION TECH', rect: { x: 229, y: 49, width: 42, height: 86 }, action: 'npc', npcId: 'mara' },
      { id: 'to-corridor', label: 'MAINTENANCE DOOR', rect: { x: 4, y: 35, width: 25, height: 99 }, action: 'move', target: 'corridor' },
    ],
  },
  corridor: {
    id: 'corridor',
    name: 'MAINTENANCE CORRIDOR',
    description: 'Pipes tick in the dark. A red locker and a breaker panel line the wall.',
    hotspots: [
      { id: 'locker', label: 'RED LOCKER', rect: { x: 40, y: 45, width: 56, height: 78 }, action: 'locker' },
      { id: 'breaker', label: 'BREAKER NOTE', rect: { x: 125, y: 69, width: 43, height: 26 }, action: 'clue', clueId: 'breaker-note' },
      { id: 'map', label: 'MAINTENANCE MAP', rect: { x: 207, y: 60, width: 62, height: 51 }, action: 'clue', clueId: 'station-map' },
      { id: 'to-furnace-gallery', label: 'FURNACE GALLERY', rect: { x: 278, y: 35, width: 31, height: 99 }, action: 'move', target: 'furnace' },
      { id: 'to-control', label: 'CONTROL ROOM', rect: { x: 4, y: 35, width: 25, height: 99 }, action: 'move', target: 'control' },
      { id: 'to-pump', label: 'PUMP HOUSE', rect: { x: 120, y: 104, width: 59, height: 28 }, action: 'move', target: 'pump' },
    ],
  },
  furnace: {
    id: 'furnace',
    name: 'FURNACE GALLERY',
    description: 'The furnace has cooled, but soot still clings to the gallery walls.',
    hotspots: [
      { id: 'furnace-tag', label: 'SOOT-STAINED SERVICE TAG', rect: { x: 31, y: 53, width: 70, height: 65 }, action: 'clue', clueId: 'furnace-tag', itemId: 'heat-glove' },
      { id: 'furnace-scar', label: 'BYPASS SCORCH MARK', rect: { x: 103, y: 70, width: 28, height: 42 }, action: 'clue', clueId: 'furnace-scar' },
      { id: 'niko', label: 'NIKO, FURNACE WORKER', rect: { x: 137, y: 47, width: 48, height: 87 }, action: 'npc', npcId: 'niko' },
      { id: 'to-corridor', label: 'MAINTENANCE CORRIDOR', rect: { x: 278, y: 35, width: 31, height: 99 }, action: 'move', target: 'corridor' },
    ],
  },
  pump: {
    id: 'pump', name: 'PUMP HOUSE',
    description: 'The lights work. The return pump does not. A tagged wheel sits above a silent heat exchanger.',
    hotspots: [
      { id: 'pump-card', label: 'LOOP CARD', rect: { x: 41, y: 32, width: 59, height: 32 }, action: 'service-note', noteId: 'pump-card' },
      { id: 'return-wheel', label: 'RETURN WHEEL', rect: { x: 114, y: 47, width: 39, height: 35 }, action: 'valve' },
      { id: 'pump-starter', label: 'PUMP STARTER', rect: { x: 202, y: 56, width: 51, height: 57 }, action: 'pump' },
      { id: 'to-corridor', label: 'CORRIDOR', rect: { x: 4, y: 35, width: 25, height: 99 }, action: 'move', target: 'corridor' },
      { id: 'to-terrace', label: 'RIVER TERRACE', rect: { x: 278, y: 35, width: 31, height: 99 }, action: 'move', target: 'terrace' },
    ],
  },
  terrace: {
    id: 'terrace', name: 'RIVER TERRACE',
    description: 'Maumee water catches the first light. A dispatch terminal waits beside the route board.',
    hotspots: [
      { id: 'route-board', label: 'BASIN ROUTES', rect: { x: 40, y: 63, width: 76, height: 62 }, action: 'service-note', noteId: 'route-board' },
      { id: 'dispatch-card', label: 'DISPATCH SLIP', rect: { x: 170, y: 102, width: 39, height: 28 }, action: 'service-note', noteId: 'dispatch-card' },
      { id: 'dispatch', label: 'DISPATCH TERMINAL', rect: { x: 214, y: 75, width: 57, height: 56 }, action: 'dispatch' },
      { id: 'river-view', label: 'WATCH THE RIVER', rect: { x: 120, y: 28, width: 92, height: 42 }, action: 'view' },
      { id: 'to-pump', label: 'PUMP HOUSE', rect: { x: 4, y: 35, width: 25, height: 99 }, action: 'move', target: 'pump' },
    ],
  },
};

// Operational notes stay separate from the ten-item blackout case file.
export const serviceNotes: Record<ServiceNoteId, { title: string; text: string }> = {
  'pump-card': { title: 'LOOP CARD', text: 'Heat goes somewhere: process hall → exchanger → district loop → return. The standby loop needs the RETURN wheel open before the pump starts. The wheel is warm; use Niko’s glove. The river is not the drain.' },
  'route-board': { title: 'BASIN ROUTES', text: 'Glass City: roofs and repair yards. River Commons: ferry, reeds and public steps. Industrial Belt: furnaces and borrowed heat. Lake Coast: fish, birds and bright rides. Someone has drawn a tiny roller coaster beside their next day off.' },
  'dispatch-card': { title: 'DISPATCH SLIP', text: 'One local link, two waiting jobs: a flexible glass-roof render and a maintenance record for the Basin Reading Hall. Send the record now and delay the render, or finish the render and queue the record for morning. Cooling has its own protected supply.' },
};

export const clues: Record<ClueId, Clue> = {
  'shift-log': {
    id: 'shift-log', title: 'SHIFT LOG',
    text: 'Last note, marked in newer ink: “Blue-tape bypass. LEFT socket takes the ceramic fuse.”',
  },
  'breaker-note': {
    id: 'breaker-note', title: 'BREAKER NOTE',
    text: 'A grease pencil arrow marks the LEFT socket. Leave the damaged right socket alone.',
  },
  'station-map': {
    id: 'station-map', title: 'MAINTENANCE MAP',
    text: 'The red locker is tagged: SPARE CERAMIC FUSE. Keep the key with the tech.',
  },
  'furnace-tag': {
    id: 'furnace-tag', title: 'FURNACE SERVICE TAG',
    text: 'A soot-stained tag says the final line of the shift log was rewritten after the furnace tripped.',
  },
  'maintenance-memo': {
    id: 'maintenance-memo', title: 'DEFERRED MAINTENANCE MEMO',
    text: 'An unsigned memo records arcing at the left socket and a deferred inspection: “Run it until the next shutdown.”',
  },
  'furnace-scar': {
    id: 'furnace-scar', title: 'BYPASS SCORCH MARK',
    text: 'The scorch trail begins at the blue-tape bypass. The panel face has no tool marks or signs of forced entry.',
  },
};

export const items: Record<ItemId, Item> = {
  'maintenance-key': { id: 'maintenance-key', label: 'MAINTENANCE KEY', description: 'A square brass key stamped V-13.' },
  fuse: { id: 'fuse', label: 'CERAMIC FUSE', description: 'A good fuse, wrapped in blue tape.' },
  'heat-glove': { id: 'heat-glove', label: 'HEAT GLOVE', description: 'A heat-scarred glove for handling warm furnace parts.' },
};

export interface TheoryDefinition {
  id: TheoryId;
  label: string;
  shortLabel: string;
}

export const theories: Record<TheoryId, TheoryDefinition> = {
  'industrial-accident': {
    id: 'industrial-accident',
    label: 'Industrial accident caused by neglected maintenance',
    shortLabel: 'INDUSTRIAL ACCIDENT',
  },
  'worker-sabotage': {
    id: 'worker-sabotage',
    label: 'Deliberate worker sabotage',
    shortLabel: 'WORKER SABOTAGE',
  },
  'management-cover-up': {
    id: 'management-cover-up',
    label: 'Management cover-up of a known design defect',
    shortLabel: 'MANAGEMENT COVER-UP',
  },
};

export interface CaseEvidenceEffect {
  score: number;
  explanation: string;
}

export type CaseEvidenceRequirement =
  | { kind: 'clue'; clueId: ClueId }
  | { kind: 'mara-testimony' }
  | { kind: 'niko-report' }
  | { kind: 'niko-silence' }
  | { kind: 'repair-outcome' };

export interface CaseEvidenceDefinition {
  id: CaseEvidenceId;
  title: string;
  text: string;
  requirement: CaseEvidenceRequirement;
  effects: Partial<Record<TheoryId, CaseEvidenceEffect>>;
}

export const caseEvidenceOrder: CaseEvidenceId[] = [
  'shift-log', 'breaker-note', 'station-map', 'furnace-tag', 'maintenance-memo', 'furnace-scar',
  'mara-testimony', 'niko-report', 'niko-silence', 'repair-outcome',
];

// These relationships are the case-review rules. A positive score supports a theory;
// a negative score is deliberately contradictory evidence.
export const caseEvidenceDefinitions: Record<CaseEvidenceId, CaseEvidenceDefinition> = {
  'shift-log': {
    id: 'shift-log', title: 'ALTERED SHIFT LOG', text: clues['shift-log'].text,
    requirement: { kind: 'clue', clueId: 'shift-log' },
    effects: {
      'industrial-accident': { score: -1, explanation: 'The newer ink makes a simple maintenance accident less certain.' },
      'worker-sabotage': { score: 1, explanation: 'A bypass could have been used to trigger a failure deliberately.' },
      'management-cover-up': { score: 3, explanation: 'A changed line points to records being managed after the event.' },
    },
  },
  'breaker-note': {
    id: 'breaker-note', title: 'BREAKER NOTE', text: clues['breaker-note'].text,
    requirement: { kind: 'clue', clueId: 'breaker-note' },
    effects: {
      'industrial-accident': { score: 2, explanation: 'A documented left-socket hazard fits neglected maintenance.' },
      'worker-sabotage': { score: 2, explanation: 'The marked trap gives a worker a known route to damage the panel.' },
      'management-cover-up': { score: 1, explanation: 'The known risk was documented without being repaired.' },
    },
  },
  'station-map': {
    id: 'station-map', title: 'MAINTENANCE MAP', text: clues['station-map'].text,
    requirement: { kind: 'clue', clueId: 'station-map' },
    effects: {
      'industrial-accident': { score: 1, explanation: 'The spare-fuse plan shows this was expected to be routine maintenance.' },
      'management-cover-up': { score: 1, explanation: 'Maintenance inventory was documented, but the hazard remained.' },
    },
  },
  'furnace-tag': {
    id: 'furnace-tag', title: 'ALTERED FURNACE TAG', text: clues['furnace-tag'].text,
    requirement: { kind: 'clue', clueId: 'furnace-tag' },
    effects: {
      'industrial-accident': { score: 2, explanation: 'The furnace tripped before the blackout, matching a cascading equipment failure.' },
      'worker-sabotage': { score: -2, explanation: 'The timing contradicts a worker starting the failure at the panel.' },
      'management-cover-up': { score: 2, explanation: 'The shift log was rewritten after the trip.' },
    },
  },
  'maintenance-memo': {
    id: 'maintenance-memo', title: 'DEFERRED MAINTENANCE MEMO', text: clues['maintenance-memo'].text,
    requirement: { kind: 'clue', clueId: 'maintenance-memo' },
    effects: {
      'industrial-accident': { score: 3, explanation: 'Recorded arcing and a deferred inspection directly support maintenance failure.' },
      'worker-sabotage': { score: -1, explanation: 'Existing wear is a better fit than deliberate damage.' },
      'management-cover-up': { score: 3, explanation: 'Management knew about the design defect and deferred the fix.' },
    },
  },
  'furnace-scar': {
    id: 'furnace-scar', title: 'BYPASS SCORCH MARK', text: clues['furnace-scar'].text,
    requirement: { kind: 'clue', clueId: 'furnace-scar' },
    effects: {
      'industrial-accident': { score: 3, explanation: 'The scorch trail follows the bypass, with no sign of forced entry.' },
      'worker-sabotage': { score: -3, explanation: 'The absence of tool marks undermines deliberate sabotage.' },
      'management-cover-up': { score: 1, explanation: 'The defect left a trace someone could have hidden.' },
    },
  },
  'mara-testimony': {
    id: 'mara-testimony', title: 'MARA\'S MAINTENANCE TESTIMONY',
    text: 'Mara gave you her key and repeated the blue-tape, left-socket procedure after the shift log was read.',
    requirement: { kind: 'mara-testimony' },
    effects: {
      'industrial-accident': { score: 1, explanation: 'Mara describes a maintenance procedure, not a forced failure.' },
      'worker-sabotage': { score: 1, explanation: 'Her warning confirms that someone familiar with the panel could exploit it.' },
      'management-cover-up': { score: -1, explanation: 'Mara openly gives the key and the safe procedure.' },
    },
  },
  'niko-report': {
    id: 'niko-report', title: 'NIKO\'S REPORTED TESTIMONY',
    text: 'Niko agreed to report that the furnace tripped first and that the final shift-log line was altered.',
    requirement: { kind: 'niko-report' },
    effects: {
      'industrial-accident': { score: 2, explanation: 'The worker testimony confirms the failure began in the furnace.' },
      'worker-sabotage': { score: -2, explanation: 'Niko\'s report contradicts a worker starting the panel failure.' },
      'management-cover-up': { score: -3, explanation: 'A filed report exposes the altered line instead of concealing it.' },
    },
  },
  'niko-silence': {
    id: 'niko-silence', title: 'NIKO\'S SILENCE',
    text: 'Niko agreed to keep the altered shift-log line between the two of you.',
    requirement: { kind: 'niko-silence' },
    effects: {
      'industrial-accident': { score: -1, explanation: 'Withholding the alteration leaves the maintenance theory less secure.' },
      'worker-sabotage': { score: 1, explanation: 'Silence allows a deliberate act to remain a plausible accusation.' },
      'management-cover-up': { score: 3, explanation: 'Keeping the altered line quiet helps preserve a cover-up.' },
    },
  },
  'repair-outcome': {
    id: 'repair-outcome', title: 'REPAIR OUTCOME',
    text: 'The ceramic fuse in the marked left socket restored the station; the right socket was never used.',
    requirement: { kind: 'repair-outcome' },
    effects: {
      'industrial-accident': { score: 3, explanation: 'A correct routine repair restored the system, consistent with a preventable failure.' },
      'worker-sabotage': { score: -1, explanation: 'The panel recovered without evidence of deliberate damage.' },
      'management-cover-up': { score: 1, explanation: 'The design defect was known and fixable, yet it was left in service.' },
    },
  },
};

export const initialMessage = 'The station went dark at 02:13. Find out why.';
