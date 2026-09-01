# Agent Workflow

This document governs durable handoffs among ChatGPT/Sol, Hermes, and Codex.
The repository is the canonical operational state; chat summaries are context,
not authority.

## Roles

### ChatGPT Project / Sol (high reasoning)

Sol owns scientific and worldbuilding architecture, phase design, evidence
standards, scenario design, major methodological decisions, interpretation,
acceptance/hold/rejection decisions, and publication or release decisions.
Sol defines what should be built and the scientific boundaries.

### Hermes / GPT-5.6-Luna

Hermes executes an approved brief: bounded source research, reproducible data
retrieval, scripts, spatial/data analysis, maps, figures, documentation, QA,
regression testing, branch/worktree management, commits, normal pushes and
fast-forward integration, and durable progress handoffs. Hermes determines how
to implement the approved scope.

### Codex

Codex provides focused maintenance, recovery, validation, Git/data hygiene,
targeted implementation, durable-state preparation, and independent review.
Codex should not redefine scientific scope while an approved brief exists.

## Start-of-run checklist

At the beginning of every run, inspect actual state in this order:

1. `git status`;
2. local and remote branch SHAs;
3. `PROJECT_STATUS.md`;
4. `docs/canon_status.md`;
5. `docs/agent_workflow.md`;
6. `reports/current_phase_handoff.md`, if present; and
7. existing outputs before rebuilding anything.

An interrupted action must not be assumed to have failed. Repository state
overrides stale chat history.

## One active writing agent

Only one agent may actively modify a given phase branch/worktree at a time.
Other agents may review, design future phases, analyze results, or prepare
prompts, but must not concurrently edit the active phase branch/worktree.

## Normal execution authority

Under an approved phase brief, the execution agent may perform routine public
source research, retrieve reproducible data, create or edit scripts and
analytical tables, produce maps/figures and reports, revise cartography after
visual QA, create a phase branch/worktree, run Python/R/application validation,
commit, push a feature branch, and fast-forward validated work to `main` and
push `main`.

This authority requires that the approved scope and acceptance criteria are
followed, frozen baselines are unchanged, and no destructive Git action is
needed.

## Mandatory human / Sol approval

Stop and obtain approval before altering an accepted/frozen factual baseline,
force-pushing or rewriting published history, deleting substantial content,
changing repository visibility, creating a release or tag, publishing outside
GitHub, materially expanding a phase, resolving a major scientific
contradiction by assumption, introducing sensitive or nonpublic infrastructure
detail, or converting scenario content into the factual baseline.

## Evidence and modeling discipline

Never silently convert inferred to verified, planned to operating, scenario to
factual, or historical to current. Accepted factual baselines remain immutable
during later scenario phases; corrections require a separately reviewed change.

Prefer sources in this order: authoritative government/scientific source,
primary institutional source, peer-reviewed literature, authoritative industry
or company primary source, then high-quality secondary source when necessary.
Record provenance, date, uncertainty, and status. Do not inflate source counts
for appearance.

Use the simplest model that answers the approved phase question. Do not add
detailed engineering models, synthetic precision, unsupported quantitative
estimates, unnecessary GIS layers, or speculative infrastructure unless the
phase brief requires them.

## Git, data, and artifact hygiene

- Keep one active phase branch/worktree.
- Inspect the final diff before integration.
- Validate frozen-baseline hashes and audit the largest tracked blobs.
- Verify Git LFS and keep reproducibly downloadable large raw datasets out of
  ordinary Git where appropriate.
- Never rewrite historical release history.
- Do not create releases or tags without explicit approval.

## Interruption and usage-limit protocol

Before stopping after substantial work, or when a usage limit is approaching,
update `reports/current_phase_handoff.md`. Chat history is not a sufficient
recovery mechanism.

On resumption:

1. read `reports/current_phase_handoff.md`;
2. inspect actual Git and worktree state;
3. compare actual state with the handoff;
4. continue from the latest valid checkpoint;
5. do not repeat expensive research, downloads, builds, or validation unless
   required; and
6. do not assume a push, merge, or commit failed merely because the prior
   session ended before reporting it.

The handoff is an operational continuity record, not a duplicate project
history. `PROJECT_STATUS.md` remains authoritative for detailed status.

## Current boundary

Phase 3C is accepted/validated. Phase 1 and Phase 3B factual baselines remain
accepted/frozen. Phase 4A is the expected next analytical phase, but this
workflow setup does not authorize beginning it. Future scenario content must
remain separate from factual baseline content.
