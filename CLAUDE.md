# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## Read first
1. `specs/constitution.md`: binding rules.
2. `specs/README.md`: workflow and spec status.
3. The spec you are working on.
4. `docs/adr/`: decisions. `docs/HANDOFF.md` is background only.

## Workflow (spec-driven, Superpowers)
- New feature or change in behaviour: `superpowers:brainstorming` → spec in `specs/NNN-name/spec.md`
  (from `specs/_templates/`) → owner approval → `superpowers:writing-plans` → `plan.md` and `tasks.md`.
- Never write application code for a spec whose status is not **Approved**.
- Implement test-first (`superpowers:test-driven-development`); reference FR/SC ids in commits and PRs.
- Before a PR: `code-review`, `security-review` for auth or data code, impeccable `audit` for UI.
- Decisions with lasting effect → ADR in `docs/adr/` from `0000-template.md`.

## Hard rules
- Tenant tables: `company_id` (+ `workspace_id`), FORCE RLS, leak tests in the same PR.
- The AI never writes SQL or reads raw tables; everything goes through the tool gateway.
- Every user-facing string in Arabic and English; logical CSS properties only (RTL).
- Never commit secrets, `.env`, dumps or customer data.

## Commands
- Backend checks: `cd backend && ruff check . && ruff format --check . && pytest`
- Local stack: `cp deploy/.env.example deploy/.env && docker compose -f deploy/docker-compose.yml up -d`
