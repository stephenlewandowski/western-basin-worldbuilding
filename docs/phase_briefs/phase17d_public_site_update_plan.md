# Phase 17D — public site update plan

**Basis:** the checked-in Atlas Preview is a Vite multi-page site under `/western-basin-worldbuilding/`. It currently serves `/`, four `/atlas/.../` studies, `/methods/`, `/roadmap/`, and `/game/`. Page entries are in `vite.config.ts`; the shared layout and home/roadmap copy are in `src/atlas/main.ts`; study data are in `src/atlas/content.ts`. This plan extends those routes. The public Pages workflow is manually deployed; this document does not authorize a deployment.

## Proposed information architecture

| Route | Change |
| --- | --- |
| `/` | Lead with the accepted HF-01 wide image, a short Glass City premise and a direct hero-page link. Add a **2075 futurescapes** section for HF-01 and, once accepted, HF-04. Keep the existing `#essays` anchor and four Phase 17A studies under a clearly named **Studies / how the Atlas works** section. Update the current-work band, count-based CTA and footer version/status text when each milestone publishes. |
| `/atlas/glass-city-2075/` | New HF-01 page: wide → short place/question → maintenance view → canopy/old-wall inset → E/S/K boundary and source links → related Toledo crib study and next hero. Publish as a final hero only after human visual approval. |
| `/atlas/industrial-metabolism-2075/` | New HF-04 page with the same reading order, foregrounding qualification, rejection and external flows. Link to the existing Industrial Exchange study. Publish after HF-04 review. |
| `/updates/` | Add a compact dated project log with status labels and links to the relevant page or repository record. Entries: Phase 17D direction accepted; HF-01 prototype under visual review; HF-01 hero approved/published; HF-04 hero approved/published. Write only the milestone that has actually occurred, with its date; do not present a prototype as final. |
| `/methods/` and `/roadmap/` | Explain that new heroes are S/K composite concept art while the Phase 17A figures are supporting studies. Change the stale roadmap claim that Phase 17D has not begun; show Phase 17D as active development without changing older phase records or implying canon promotion. |

Navigation can keep **Atlas** pointed to a new `#futurescapes` home anchor once HF-01 publishes, while retaining `#essays` for existing deep links. Add **Updates** to the header/footer. Leave `/game/` available; no redesign is required. Implement the two new `/atlas/` HTML entries and `/updates/` in the current Vite page map. Reuse the shared layout, but give heroes their own content type/renderer so the three-image sequence and S/K boundary are explicit rather than forcing them into the four-panel Phase 17A essay template.

## Cross-links and publication rhythm

- **Both hero pages:** [Phase 17D brief](phase17d_futurist_atlas_synthesis.md), [HF concept record](../../reports/phase17d_hero_futurescape_concepts.md), [house style](phase17d_public_visual_style_guide.md), [production plan](phase17d_hf01_hf04_production_plan.md), and `/methods/` for E/S/K. Label links to the repository as development sources, not visual proof of a built project.
- **HF-01:** link `/atlas/toledo-crib/` as a related example of old/new persistence, plus [Phase 17A findings](../../reports/phase17a_prototype_findings_and_production_pattern.md). State that the composite Glass City street is not the intake crib site. Add the HF-01 prototype notes only when they are actually integrated into the public repository.
- **HF-04:** link `/atlas/industrial-exchange/`, the [Phase 17B lived-world packets](../../reports/phase17b_lived_world_condition_packets.md) (FT-03), and the Phase 17A findings. Distinguish the new hall concept from the existing district diagram.
- **Updates:** each entry links to its new hero page when available, its relevant source record, and `/roadmap/`; hero pages link back to the dated release entry. The home page links to the latest update. This gives the live site a visible record at each major development.

**Execution order:** publish an accurate text/status update for Phase 17D and the pending HF-01 review; after HF-01 approval, add its assets/page and promote it on home; after HF-04 approval, add its page/card and update the log. Before each manual Pages deployment, review captions, alt text, image rights, route links, mobile crops, visual hierarchy and file weight in a local preview. Hermes can handle routine page wiring and optimization; human review owns visual acceptance and final public wording. No site changes or deployment are performed by this plan.
