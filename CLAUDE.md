# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository.

## Read first
1. `specs/constitution.md`: binding rules.
2. `specs/README.md`: workflow and spec status.
3. The spec you are working on.
4. `docs/adr/`: decisions. `docs/HANDOFF.md` is background only.

## Delivery cycle and the skill for each step
| Step | Output | Skill |
|---|---|---|
| Epic / release scope | epic summary inside `specs/README.md` or an issue | `breakdown-epic-pm` (project) |
| Shape a feature | agreed intent | `superpowers:brainstorming` |
| Specify | `specs/NNN-name/spec.md` from `specs/_templates/spec.md` | `superpowers:brainstorming` |
| Decide | `docs/adr/NNNN-title.md` from `docs/adr/0000-template.md` | `architecture-decision-records` (project) |
| Plan | `specs/NNN-name/plan.md` | `superpowers:writing-plans` |
| Tasks → issues | `specs/NNN-name/tasks.md`, GitHub issues on the Project board | `gh` CLI |
| Build backend | code + tests, test-first | `superpowers:test-driven-development`, `fastapi` (project) |
| Database / RLS | migrations, policies, leak tests | `supabase-postgres-best-practices` (project) |
| Build frontend | Angular code | `angular-principles` |
| Design quality | audit, RTL, accessibility | `impeccable` |
| CI / workflows | `.github/workflows/*` | `github-actions-hardening` (project) |
| Review | PR | `code-review`, `security-review` (auth/data), `superpowers:requesting-code-review` |
| Finish | merged PR, spec status updated | `superpowers:verification-before-completion`, `superpowers:finishing-a-development-branch` |

### Overrides for project skills
- Skills that save documents elsewhere (for example `breakdown-epic-pm` → `docs/ways-of-work/`) must
  save into this repo's structure instead: specs in `specs/`, decisions in `docs/adr/`.
- `architecture-decision-records`: use our template `docs/adr/0000-template.md`, not the skill's.
- `supabase-postgres-best-practices`: ignore Supabase-only parts (`auth.uid()`, `auth.jwt()`,
  Supabase dashboard, PostgREST). Our RLS keys on the per-transaction tenant context (spec 002 FR-018).

### Keeping skills current
- Project skills live in `.claude/skills/`, pinned by `skills-lock.json` (committed).
- Restore after clone: `npx skills experimental_install`.
- Check for updates at the start of each sprint: `npx skills update -p`, review the diff of
  `.claude/skills/` like any other code, and commit it in its own PR.

## Gates
- Never write application code for a spec whose status is not **Approved**.
- Reference FR/SC ids in commits and PRs. Spec PRs and implementation PRs are separate.

## Hard rules
- Tenant tables: `company_id` (+ `workspace_id`), FORCE RLS, leak tests in the same PR.
- The AI never writes SQL or reads raw tables; everything goes through the tool gateway.
- Every user-facing string in Arabic and English; logical CSS properties only (RTL).
- Never commit secrets, `.env`, dumps or customer data.

## Commands
- Backend checks: `cd backend && ruff check . && ruff format --check . && pytest`
- Local stack: `cp deploy/.env.example deploy/.env && docker compose -f deploy/docker-compose.yml up -d`
