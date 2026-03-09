<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0

Modified principles: none (initial ratification — all five principles newly defined)

Added sections:
  - Core Principles (5): I. Reproducibility-First, II. Stage Independence,
    III. Shared Artifact Contracts, IV. Experiment Observability, V. Service-Training Parity
  - Technology Stack & Conventions
  - Development Workflow & Quality Gates
  - Governance

Removed sections: none

Templates requiring updates:
  ✅ .specify/memory/constitution.md — filled and ratified (this file)
  ✅ .specify/templates/plan-template.md — Constitution Check placeholder is feature-scoped;
     gates will be populated at plan-generation time; no structural change required
  ✅ .specify/templates/spec-template.md — generic structure remains adequate; no new
     mandatory spec sections imposed by this constitution
  ✅ .specify/templates/tasks-template.md — generic phase structure covers DVC stage,
     MLflow observability, and BentoML task types; no structural change required
  ✅ .github/prompts/*.prompt.md — reviewed; no outdated agent-specific references found

Follow-up TODOs: none — all placeholders resolved
-->

# Projekt Penguins Constitution

## Core Principles

### I. Reproducibility-First

Every experiment and pipeline run MUST be fully reproducible from a clean checkout.
All pipeline stages are defined in `dvc.yaml` with explicit dependencies and outputs.
All tunable parameters MUST live in `params.yaml` and be tracked by DVC.
Random seeds MUST be fixed and logged in every MLflow run.
`dvc repro` on a clean environment MUST produce bit-identical outputs given the same
data version.

**Rationale**: Reproducibility is the foundation of trustworthy ML; without it every
result is anecdotal and every fix is a guess.

### II. Stage Independence

Each of the five DVC pipeline stages (`data_load`, `preprocess`, `train`, `evaluate`,
`register`) MUST be independently executable via `dvc repro <stage>`.
Stages MUST communicate exclusively through versioned file artifacts — no shared mutable
in-memory state, no hidden global side-effects between stages at runtime.
A stage's public interface is its declared `deps` and `outs`; changes to that interface
require a pipeline version bump in `dvc.yaml`.

**Rationale**: Independent stages enable parallel development, targeted reruns, and safe
refactoring without full-pipeline regression risk.

### III. Shared Artifact Contracts

The feature encoder is a shared artifact and MUST be implemented once, in
`src/features/encoder.py`.
Both the DVC training pipeline and the BentoML service MUST import from this single
module — no reimplementation, no copy-paste of encoding logic is permitted anywhere.
The serialised encoder artifact produced by the `preprocess` stage MUST be the exact
file loaded by the BentoML runner at inference time.
Any change to encoder logic MUST result in a new DVC-tracked artifact version; the
BentoML service MUST be re-packaged before the next deployment.

**Rationale**: Divergent encode paths are the primary source of training-serving skew —
a silent and costly failure mode that this principle eliminates by design.

### IV. Experiment Observability

Every MLflow run MUST log, at minimum:
- All parameters sourced from `params.yaml`
- All evaluation metrics produced by the `evaluate` stage
- The artifact URI of the serialised model and encoder
- A `dvc_commit` tag capturing the DVC data commit hash at run time

Every Optuna study MUST persist its trial database to a storage backend whose URI is
declared in `params.yaml` (no in-memory-only studies).
Silent experiments — runs that complete without logged metrics — are a constitution
violation and MUST be caught as a CI failure.

**Rationale**: Logged experiments are the project's institutional memory; unlogged runs
cannot be audited, compared, or rolled back.

### V. Service-Training Parity

The BentoML service MUST load its model and encoder exclusively from artifacts produced
by the DVC pipeline, referenced via the MLflow Model Registry or an explicit DVC path.
The service MUST NOT define its own preprocessing or encoding logic.
Pre-deployment integration tests MUST assert that the service produces the same
predictions as the pipeline's `evaluate` stage for a held-out golden dataset.

**Rationale**: Serving code that diverges from training code defeats the purpose of a
disciplined pipeline and undermines user trust in deployed predictions.

## Technology Stack & Conventions

**Language**: Python 3.11+
**Pipeline orchestration**: DVC (`dvc.yaml`, `params.yaml`)
**Experiment tracking**: MLflow Tracking Server
**Hyperparameter optimisation**: Optuna (studies persisted to SQLite or PostgreSQL)
**Model serving**: BentoML
**Shared package**: `src/` — importable by both pipeline stages and the BentoML service
**Testing**: pytest; unit tests in `tests/unit/`, integration tests in `tests/integration/`
**Linting / Formatting**: ruff + black (enforced in CI)

Naming conventions:
- DVC stage names: `snake_case` nouns (e.g., `data_load`, `preprocess`)
- MLflow experiment names: `<project>/<feature>` (e.g., `penguins/species-classifier`)
- BentoML service names: `<project>-svc` (e.g., `penguins-svc`)
- Shared module paths: `src/features/`, `src/models/`, `src/serving/`

## Development Workflow & Quality Gates

**Gate 1 — Before merging any stage change**:
- `dvc repro` completes without error on CI
- The MLflow run for that stage is logged with all required fields (Principle IV)
- Unit tests for changed modules pass

**Gate 2 — Before merging encoder changes**:
- Shared-artifact contract test passes (confirms pipeline and service load the same file)
- Service integration test against the golden dataset passes (Principle V)
- A new DVC encoder artifact version is committed and pushed

**Gate 3 — Before tagging a release**:
- `dvc repro --pull` on a clean environment reproduces final metrics within tolerance
- BentoML service smoke test passes against the registered Production artifact
- MLflow model is promoted to the `Production` alias in the Model Registry

All PRs MUST reference which principles are exercised or potentially violated.
Complexity added beyond the minimum required MUST be justified in the PR description.

## Governance

This constitution supersedes all other project-level practices and conventions.

Amendments require:
1. A written rationale referencing the specific principle(s) affected.
2. Review and approval by at least one project maintainer.
3. A version bump following the semantic versioning policy below.
4. Updates to all dependent templates and documents within the same commit.

**Versioning policy**:
- MAJOR: Removal or fundamental redefinition of a principle (backward-incompatible
  governance change).
- MINOR: Addition of a new principle or materially expanded guidance.
- PATCH: Clarifications, wording refinements, typo fixes, non-semantic changes.

**Compliance review**: Every sprint retrospective MUST include a check that the five
principles were not violated in that sprint's merged work. Violations MUST be logged
as issues before the retrospective closes.

**Version**: 1.0.0 | **Ratified**: 2026-03-09 | **Last Amended**: 2026-03-09
