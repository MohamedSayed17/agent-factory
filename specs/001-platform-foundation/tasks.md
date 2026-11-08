# Tasks 001 — Platform foundation

**Plan:** `specs/001-platform-foundation/plan.md` (details, interfaces and tests for each task).
Each task is one pull request. `[P]` = can run in parallel with the other `[P]` tasks of the same wave.
"After" lists the tasks whose interfaces it consumes.

## Wave 1 — start immediately
- [ ] **T1** Backend tooling baseline (uv, mypy, markers) · FR-026 · after: —
- [ ] **T13** [P] Angular workspace and bilingual shell · FR-021, FR-022, FR-024 · after: —
- [ ] **T19** [P] Repository governance: READMEs, Project board, merge settings · FR-001, FR-029, FR-030 (FR-027 blocked, see plan *Open items*) · after: —

## Wave 2 — after T1
- [ ] **T2** Validated settings and `.env.example` · FR-005, FR-006 · after: T1
- [ ] **T3** [P] Layer packages, module shells, import boundaries, `docs/architecture/modules.md` · FR-002, FR-003, FR-004 · after: T1
- [ ] **T4** [P] Request id, JSON logs, redaction · FR-016, FR-018, SC-006 · after: T1
- [ ] **T5** [P] Language negotiation and message catalogs · FR-013 · after: T1

## Wave 3
- [ ] **T6** App factory, `/api/v1`, problem details · FR-011, FR-012 · after: T2, T3, T4, T5
- [ ] **T7** [P] Cursor pagination · FR-014 · after: T6
- [ ] **T8** [P] DB roles, baseline migration, grants · FR-007, FR-008, FR-010, SC-004 · after: T2, T3
- [ ] **T9** Tenant context per transaction · FR-009 · after: T8
- [ ] **T10** [P] Health, readiness, metrics · FR-019, FR-020 · after: T6, T8
- [ ] **T11** [P] Worker, beat, worker health · FR-017, FR-019 · after: T2, T4
- [ ] **T12** Contract test · FR-015 · after: T6, T7, T10

## Wave 4
- [ ] **T14** Logical-CSS lint, translation-key check, generated API client · FR-015, FR-022, FR-023 · after: T12, T13
- [ ] **T15** [P] RTL/LTR layout check at 360/768/1440 px · SC-005 · after: T13
- [ ] **T16** One-command local stack · FR-025, SC-001 · after: T9, T10, T11, T14
- [ ] **T17** Complete CI gate · FR-026, SC-002 · after: T12, T14, T15, T16
- [ ] **T18** [P] Release images to GHCR · FR-028 · after: T16

## Wave 5
- [ ] **T20** Prove SC-001…SC-006 and close the spec · after: all

## Coverage check
| Requirement | Task | Requirement | Task |
|---|---|---|---|
| FR-001 | T19 | FR-016 | T4 |
| FR-002 | T3 | FR-017 | T11 |
| FR-003 | T3 | FR-018 | T4 |
| FR-004 | T3 | FR-019 | T10, T11 |
| FR-005 | T2 | FR-020 | T10 |
| FR-006 | T2, T16 | FR-021 | T13 |
| FR-007 | T8 | FR-022 | T13, T14, T15 |
| FR-008 | T8 | FR-023 | T14 |
| FR-009 | T9 | FR-024 | T13 |
| FR-010 | T8, T17 | FR-025 | T16 |
| FR-011 | T6 | FR-026 | T1, T3, T17 |
| FR-012 | T6 | FR-027 | T19 (blocked) |
| FR-013 | T5 | FR-028 | T18 |
| FR-014 | T7 | FR-029 | T19 |
| FR-015 | T12, T14 | FR-030 | T19 |
| SC-001 | T16, T20 | SC-004 | T8 |
| SC-002 | T17 | SC-005 | T15 |
| SC-003 | T20 | SC-006 | T4 |
