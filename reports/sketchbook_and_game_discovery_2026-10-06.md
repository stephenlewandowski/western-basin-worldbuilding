# Sketchbook integration and Erie Drift discovery

**6 October 2026 · published on both sites**

The user approved Erie Drift and requested stronger links on the personal site
and Atlas, plus reuse of the original concept-art sheets. Both repositories were
clean at inspection: Western Basin `95c80c3`; portfolio `c784301`.

## Delivered

- Personal-site homepage and Projects featured boxes have a direct **Play Erie
  Drift** button. The project overview gains a game shortcut and replaces retired
  bus/Return Visit promotion with **The Orange Band**. Four overview shortcuts
  form a responsive two-column grid.
- Atlas hero, navigation and footer offer a visible game route. The existing
  fishing teaser moves up, immediately after maps, ahead of the futurescapes.
- New `/sketchbook/` collection: nine curated drawings, subject filters, an
  accessible native inspection dialog, full-sheet view, zoom and original-file
  links. Homepage, navigation, footer and five developed places link into it.
- Three original sheets remain untouched. Nine crops and three full-sheet WebPs
  are recorded in [the derivative manifest](../assets/atlas/sketchbook/manifest.json).
  All served derivatives total about 1.85 MB; full sheets load lazily. Original
  PNGs total about 10.48 MB and are not served in the gallery.

## Curatorial decisions

The first selection favors the bridge, glass-and-brick city, working river,
repairable machine spread, four worker silhouettes, rural maker, wetland path,
field station and small biological archive. It preserves the ink-and-wash visual
language without creating new illustrations or changing handwritten annotations.

**Frontier Arc → Black Swamp Country:** the original six-region labels remain on
the full sheets. A short public history explains that the former agricultural,
cooperative-energy and maker themes now share Black Swamp Country with wetland
themes. Old map outlines are not reused as current navigation or a historical
swamp boundary. The current five-region register is unchanged.

**Characters:** sheet 02 assigns Dr. Li Wei to photonics, while sheet 03 assigns
that name to an ecologist; Maya labels also vary. The gallery presents occupations,
clothing and silhouettes, without establishing biographies or identifying these
figures with Renata, Hannah, Jo or other current story characters. Old dates and
water-level/technology annotations remain early concept notes. These historical
sheets are not newly accepted depictions of a particular 2075 summer condition.

Scientific baselines, Model Lab, game mechanics, empirical data, Hall orientation,
accepted artwork and the withdrawn comic remain unchanged.

## Next useful integrations

1. Give existing stories and games a few recurring props from the machine spread:
   a service case, small robot or working boat silhouette. Test recognition before
   adding an equipment catalog or new simulation systems.
2. Use a worker silhouette as visual reference for one established scene role.
   Choose a consistent design and season-appropriate clothing before fixing names
   or expanding a cast.
3. Develop a small river landing or wetland shelter as an Atlas-linked side place,
   with a human task at its center. Keep the former Frontier Arc’s practical maker
   character within Black Swamp Country.

## Validation and review state

Web tests: 64 across nine files. TypeScript/production build: 18 routes, including
Sketchbook. Browser checks at 1440, 390 and 320 px cover prominent game links,
filters and deep links, keyboard dialog opening, full-sheet zoom, Escape/focus
return, portfolio buttons, retired-link removal and horizontal overflow. All 18
Atlas routes return 200 locally and no runtime errors were found.

Portfolio source check: 21 HTML pages and 30 sitemap URLs pass, with valid local
assets, anchors and links. The featured map image also decodes at its expected
1536-pixel width. External gallery and game destinations now resolve on the published Atlas. All 670 repository-relative Markdown links,
`git diff --check`, LFS integrity, source/derivative hashes and 640 protected/source
files (645 freeze references) pass. Original sheets and game sources are unchanged.

Preview:

- Atlas: `http://127.0.0.1:4175/western-basin-worldbuilding/`
- Sketchbook: `http://127.0.0.1:4175/western-basin-worldbuilding/sketchbook/`
- Portfolio: `http://127.0.0.1:4180/#western-basin`
- Projects: `http://127.0.0.1:4180/projects/`

The user authorized commit, push and publication on 6 October 2026, with a new
homepage sketchbook heading: **People, places, and things worth knowing.**
The portfolio uses PR publication; the Atlas uses a manual Pages workflow.
Deployment and live-check evidence follow.

## Publication and live verification

- Atlas source: `36e1c7daf5cb2e160a344d73c78ce45fd0e4c339`.
  [Pages deployment 37409048862](https://github.com/stephenlewandowski/western-basin-worldbuilding/actions/runs/37409048862) succeeded.
- Personal-site changes: `ebe1df5f681405a95e2e30fcb0546fe131c85d1a`, merged through
  [PR #29](https://github.com/stephenlewandowski/stephenlewandowski.github.io/pull/29) as `16c1b9fb422bf77b06b1ac1173b55c5c882fed17`.
  [Pages deployment 37409205039](https://github.com/stephenlewandowski/stephenlewandowski.github.io/actions/runs/37409205039) succeeded.
- Live checks at 1440, 390 and 320 px pass: new heading, Sketchbook filters,
  keyboard inspection, full-sheet zoom, Escape/focus return, featured-project
  game buttons on homepage/Projects/overview and no horizontal overflow.
  All 18 Atlas routes return 200. No missing site assets or runtime errors were
  found, and retired bus/Return Visit links are absent from the updated pages.

Public routes:
[Atlas](https://stephenlewandowski.github.io/western-basin-worldbuilding/),
[Sketchbook](https://stephenlewandowski.github.io/western-basin-worldbuilding/sketchbook/),
[personal homepage](https://stephenlewandowski.github.io/#western-basin),
[Projects](https://stephenlewandowski.github.io/projects/).

The final documentation follow-up records publication without changing deployed
web code. Both source pushes were clean, and protected/scientific products remain
unchanged.

## Changed paths

Western Basin:

```text
README.md
PROJECT_STATUS.md
reports/README.md
reports/current_phase_handoff.md
reports/sketchbook_and_game_discovery_2026-10-06.md
src/atlas/main.ts
src/atlas/style.css
src/atlas/sketchbook.ts
vite.config.ts
sketchbook/index.html
assets/atlas/sketchbook/README.md
assets/atlas/sketchbook/manifest.json
assets/atlas/sketchbook/bridge.webp
assets/atlas/sketchbook/glass-and-brick.webp
assets/atlas/sketchbook/working-river.webp
assets/atlas/sketchbook/workshop-machines.webp
assets/atlas/sketchbook/river-workers.webp
assets/atlas/sketchbook/rural-maker.webp
assets/atlas/sketchbook/wetland-boardwalk.webp
assets/atlas/sketchbook/field-station.webp
assets/atlas/sketchbook/biological-archive.webp
assets/atlas/sketchbook/sheet-01.webp
assets/atlas/sketchbook/sheet-02.webp
assets/atlas/sketchbook/sheet-03.webp
```

Personal website:

```text
index.html
projects/index.html
projects/western-basin-worldbuilding/index.html
assets/styles.css
```

No deletions. Packaging helpers and browser screenshots remain ignored in
`temp/sketchbook-integration/` in the Western Basin workspace.
