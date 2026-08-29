# Glasspunk: Blackout at Vesper Station — slice design

## Tone and presentation

The first slice is a compact, readable mystery in a four-color CGA palette: black, cyan, magenta, and white. Canvas primitives suggest machinery, paper, pipes, and a lone station technician; no external art assets are required. The canvas always draws at 320×200, then CSS scales it with pixelated rendering.

## Player loop

1. Start in the control room and inspect the shift log.
2. Ask Mara for the maintenance key; her dialogue changes after the log is found.
3. Enter the maintenance corridor, inspect the map and breaker note, and unlock the red locker.
4. Select the ceramic fuse and use it on the control console. The repair requires both the item and the breaker clue.
5. Press `F` or double-click the repaired console to close the case. A missing clue or failed repair can lead to the failure ending in later expansions.

## Data-driven extension points

Rooms, hotspots, clues, and items are definitions in `src/game/data.ts`. State transitions are small named functions in `src/game/engine.ts`, while reusable rules live in `src/game/logic.ts`. Future rooms and case branches can add definitions and transitions without changing the renderer’s core loop.

## Accessibility and persistence

Every essential canvas action has keyboard support: arrows/WASD navigate hotspots, Enter/Space activates, Tab cycles inventory, and shortcuts cover the NPC, item use, ending, and restart. The HUD uses real buttons and live regions. Save/load stores the current state in `localStorage`; mute is a local state toggle ready for future audio.
