# Repository cleanup and current-state review — 3 October 2026

**Scope:** conservative organization, current-state verification and reader-facing
clarity. No scientific/model change, new futurescape production or publication.
Changes remain local and uncommitted; this report includes the pre-existing HF-05 work.

## Verified state and review coverage

- `main`, `origin/main` and live GitHub main matched **`ededbb5eee7f9cad70517a6e1a1e3449a4eac928`** at inspection. Starting changes were three HF-05-related status/index files plus its untracked brief and spatial-study SVG.
- Inventoried **1,284 tracked files**: 401 report files, 245 data files, 285 output files, 229 source files, and the remaining site/docs/assets/configuration. Tracked working-file content totals about **697 MB**, including the hydrated 88 MB LFS GeoPackage. This is not the Git history or download size.
- Reviewed current/status/canon/workflow/handoff records, root and report documentation, briefs, publication/source notes, Model Lab guides, tracked/ignored artifact classes, duplicate content, local links, site content/routes and registered worktrees. Bulk scientific records were checked by inventory, references and protected hashes; this was not a new scientific review of every result.
- The live Atlas homepage and content bundle contain the four futurescapes and the established Futurescapes / Studies / Methods / Updates navigation. They do **not** yet contain the new local Model Lab or Basin Reading Hall copy. Pages deploys through a manual workflow; source publication and site deployment are distinct.
- Current development is the Basin Reading Hall selected direction / production brief, with final imagery pending. Model Lab's committed saved cases are synthetic diagnostics, and its explorer is a local R/Shiny application. The game is a separate experiment.

## Decisions: keep, consolidate, archive/de-emphasize, delete

| Class | Material | Decision and reason |
| --- | --- | --- |
| **KEEP** | Frozen scientific products, accepted outputs, sources, manifests, validators, failed/successful reviews, old briefs and generated analytical figures | These establish reproducibility and decision lineage. Generated does not mean disposable. No scientific path was moved, rewritten or deleted. |
| **KEEP** | Both active HF-05 files and its useful local proof/helpers | Byte-for-byte preservation; current records link to the brief and study. No new scene or device development. |
| **KEEP** | Two exact duplicate pairs above 1 KiB | `vector_system_dependency_register.csv` / `vector_system_dependency_edges.csv` serve separate accepted register/network roles. Animation keyframe A5 / reduced-motion endpoint preserve a documented rejected-medium review lineage. No deduplication by hash alone. |
| **KEEP** | Registered worktrees, approved reference-image folders, review screenshots, local Shiny library | Three older worktrees contain untracked drafts/source studies. Reference/proof material can have value outside Git. No branch or worktree pruning. |
| **CONSOLIDATE** | Root README and technical context | A short front door explains Atlas, Studies, Model Lab, Methods and game. Detailed research/directory context moved to `docs/README.md`, with relative links adapted. |
| **CONSOLIDATE** | Report navigation | Subject-based entries lead to findings and current work; the entire previous package index remains in a collapsible historical section with existing headings/anchors. |
| **ARCHIVE / DE-EMPHASIZE** | Accumulated current-status and handoff bodies | Full snapshots retain all prior decisions, HF-05 notes and integration QA. Current pages are concise. Snapshot body SHA-256 records and reconstruction checks preserve provenance; only status-snapshot Markdown link prefixes changed for its location. |
| **ARCHIVE / DE-EMPHASIZE** | Old site/production plans and workflow phase summaries | Added explicit historical/completed-plan notices and current pointers. Original plan bodies and workflow permission rules remain. Canon-register status clarification creates no new setting decision. |
| **DELETE** | Four ignored one-off scratch scripts listed below | Probe/launch/hash diagnostics and a non-idempotent completed editorial helper have no required source/output dependency. Durable launch instructions, tests, commits and review records remain. No tracked file was deleted. |

The pre-pass Markdown scan found **no dead relative links** across 263 actual link
references. Many technical paths are plain code text rather than Markdown links.
The 258 Markdown files without a direct inbound Markdown link are **not proven
orphans**: package manifests, scripts, registries and historical records also refer
to them. They were not deleted on that basis.

## Removed files

These pre-existing individual files directly under ignored `temp/` were removed, after
checking their resolved location and references. Total **33,076 bytes**:

- `temp/model_lab_probe.R` — 213 bytes; package/hash-export diagnostic.
- `temp/model_lab_preview.R` — 149 bytes; disposable preview launcher, duplicated by durable launch instructions.
- `temp/model_lab_source_hash_probe.py` — 1,032 bytes; one-off newline/hash investigation, covered by durable tests and review.
- `temp/implement_public_editorial.py` — 31,682 bytes; completed, non-idempotent September editorial editing helper.

Three one-off editing helpers created for this pass were also discarded after
use: `temp/repository_cleanup_edit.py`, `temp/repository_cleanup_frontdoor.py`,
and `temp/repository_cleanup_site.py`. Current audit tools, JSON snapshots and
review screenshots are grouped under ignored `temp/repository-cleanup-review/`,
keeping new review scaffolding out of the temp root and public delivery.

Ignored build/dependency directories were not wholesale deleted. Current `dist/`
was rebuilt for validation and remains ignored. No tracked cache, `node_modules`,
`dist`, temporary directory or compiled Python junk was found in the Git inventory.

## Public-facing changes

- Home and footer now offer Model Lab as a separate reader path, explaining synthetic cases and local R/Shiny setup without implying a hosted web application.
- Studies distinguish qualitative watershed explanation from quantitative diagnostic accounting. No study figure or scientific claim was changed.
- Methods explain saved cases, routing-policy limits, non-forwarding, source identity checks and independent validation; source/rights and image-provenance transparency remain.
- Roadmap identifies the Reading Hall brief and pending imagery, available local Model Lab, and provisional narrative work. Updates distinguish the available research tool from a developing futurescape.
- Root README/report index use subjects before phase machinery. Internal IDs remain in stable paths, provenance and historical records. The Pages workflow's display/step names now say Atlas rather than Preview; deployment logic is unchanged.

## Validation

| Check | Result |
| --- | --- |
| `git diff --check` | PASS |
| Durable Markdown links | PASS: 370 relative links across root/docs/reports/data/outputs/assets/skills/src; validator coverage expanded beyond the old docs/reports-only selection, including the explorer guide |
| `npm test` | PASS: 22 tests in three files |
| `npm run build` | PASS: TypeScript and Vite; all 13 page entries built |
| Python Model Lab regressions | PASS: 30 tests; saved cases and model code unchanged |
| R/Shiny explorer checks | PASS: three runs, 252 HUCs, schema/balance/error checks and displays; R emitted existing locale startup warnings, with no test failure |
| Local route/layout smoke review | PASS: all 13 routes at 1440 and 390 px (26 observations); no horizontal overflow, unnamed links, missing alt text, failed local requests or JavaScript exceptions |
| Assets and references | PASS: all 27 unique page images decode; local link/asset URLs return HTTP 200; all 20 repository source-link targets exist; internal anchors and all five relative Markdown heading links resolve |
| Built text and new-record hygiene | PASS: 22 built HTML/JS/CSS/SVG files contain no Windows/localhost paths; untracked document/asset whitespace checks pass |
| Visual inspection | Home Model Lab section, Methods, Roadmap and Updates reviewed in rendered desktop/mobile proofs; accepted figures and crops unchanged |
| `git lfs fsck` | PASS |
| Freeze/protected audit | PASS: 37 manifests, 665 hash references / 654 unique protected paths; zero changed-path overlap and zero byte drift against the starting checkout |
| Historical newline representations | 190 raw hash-reference comparisons differ under Git's CRLF checkout; all match after LF normalization. No frozen bytes or newline policy changed |
| HF-05 and archival preservation | Both active HF-05 source hashes unchanged; prior status/handoff bodies reconstruct to their recorded LF-normalized SHA-256 hashes |

Commands: `python src/python/qa/validate_markdown_links.py`, `npm test`,
`npm run build`, `python -m unittest discover -s tests -p 'test_model_lab*.py'`,
and `Rscript` sourcing `tests/test_model_lab_explorer.R` with the existing local
Shiny library. Route review used the production Vite preview, with local browser
smoke/visual checks. Current proof images, audit tools and snapshots are ignored under
`temp/repository-cleanup-review/`; they are not public assets. No source-linked image or empirical model
output was rebuilt by this cleanup.

## Remaining clutter and technical debt

1. **Large analytical SVGs:** several existing system maps are about 17.5–17.9 MB each. They are accepted/native scientific products with freeze/source references. A later task could create lean reader derivatives while retaining protected originals; do not optimize them in place or rewrite history.
2. **Older worktrees:** `phase17c-ordinary-day-tests` has untracked `drafts/`; `phase17d-hf01-art-direction` has two untracked reports; `phase17d-hf01-glass-city` has untracked prototype assets/notes/builders. Preserve them until a separate source/draft inventory determines what merits durable retention. Three other non-primary registered worktrees are clean but can still hold ignored references.
3. **Historical index and plain paths:** the collapsible package index and historical reports still contain old milestone language and many unlinked code paths. Their context is now explicit. Incremental subject/package navigation is safer than bulk rewriting accepted records.
4. **Older inset lettering:** accepted study/inset assets retain some historical/internal wording inside the graphics. This pass preserves their content; a separate derivative/inset migration task needs visual/claim review.
5. **Experimental work:** HF-05 finished imagery, independent invention reuse tests, narrative drafts and empirical Model Lab readiness remain unfinished. They were not presented as published or scientifically validated.
6. **Local-only candidate:** README/site links and new records form one uncommitted cleanup candidate. Neither source nor Pages publication happened in this pass. Network/browser QA is bounded, not a complete accessibility or external-link audit.

## Recommended next priorities

1. Review and integrate this reader/navigation cleanup while preserving the HF-05 sources; separately deploy the validated Atlas candidate if publication is authorized.
2. Produce the three HF-05 camera/silhouette studies from the existing brief, then review recommended composition A before finished imagery. This is the next creative development priority; this pass improved its discoverability and continuity without beginning production.
3. Inventory the untracked narrative/visual source material in old worktrees and retain useful source/reference lineage before retiring any checkout.
4. Migrate older public insets as reviewed derivatives with readable narrow-screen explanations; retain accepted/native versions and provenance.
5. Assess empirical Model Lab inputs and validation requirements before extending mathematics or claiming environmental predictions.

## Exact path accounting and Git disposition

**Modified tracked paths (13):**

```text
.github/workflows/deploy-pages.yml
DESIGN.md
PROJECT_STATUS.md
README.md
docs/agent_workflow.md
docs/canon_status.md
docs/phase_briefs/phase17d_hf01_hf04_production_plan.md
docs/phase_briefs/phase17d_public_site_update_plan.md
reports/README.md
reports/current_phase_handoff.md
src/atlas/content.ts
src/atlas/main.ts
src/python/qa/validate_markdown_links.py
```

**New cleanup records (four untracked paths):**

```text
docs/README.md
reports/handoff_history_2026-10-03.md
reports/project_status_history_2026-10-03.md
reports/repository_cleanup_2026-10-03.md
```

**Pre-existing active work (two untracked paths, unchanged):**

```text
assets/phase17d/hf05/hf05_basin_reading_hall_spatial_study.svg
docs/phase_briefs/phase17d_hf05_basin_reading_hall_production_brief.md
```

Final status is `main...origin/main`, with **13 modified tracked files and six
untracked files** (Git displays the HF-05 asset file as its untracked directory).
HEAD remains `ededbb5eee7f9cad70517a6e1a1e3449a4eac928`; no commit, push, branch
change or deployment was made. The full history snapshots and both HF-05 sources
must accompany any later integration of these current/index changes. Deletion of
the ignored scratch/editing scripts does not appear in Git status.

## Integration checkpoint

The state and path accounting above describe the completed cleanup review before
integration. The user subsequently authorized integration and creative development.
The cleanup, both history snapshots and the existing HF-05 brief/spatial study are
included together in `docs: integrate repository cleanup and Reading Hall brief`.
Later work is recorded separately so this inventory remains a record of the cleanup.
