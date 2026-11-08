# Spec 001 — Platform foundation

**Status:** Draft, awaiting owner approval · **Release:** R1, sprint 1 · **Owner:** tech lead
**Depends on:** constitution 1.0.0 · **Blocks:** every other spec

## Why
Ten people start building in parallel next sprint. Without one agreed project structure, API
conventions, database setup, local environment and CI gates, each person invents their own and the
first month is spent reconciling them. This spec defines the shared ground everything else
stands on. It contains no product features.

## Who it serves
- **Developers** (backend, Angular, AI, QA): one command to run everything locally, clear module
  boundaries, fast and trustworthy CI.
- **DevOps/security:** a portable deployment that works on whichever provider ADR-0002 picks.
- **Product owner:** confidence that "done" means the same thing for every spec.

## User stories

**US-1 — Run the platform locally (P1).** As a new developer, I clone the repo and start the full
stack (database, cache, API, worker, web app) with one documented command, so I can work on day one.
- *Given* a machine with Docker and git, *when* I follow the README, *then* the API health check
  and the web app both respond within 10 minutes of starting, without editing any file except
  copying `.env.example`.

**US-2 — Trust the merge gate (P1).** As a reviewer, I know a green pull request has passed the
same checks for every module, so I review design, not formatting.
- *Given* a PR that breaks lint, a test, the API contract or the secret scan, *when* CI runs,
  *then* the PR cannot merge into `main`.

**US-3 — Add a module without asking where things go (P1).** As a backend developer starting
spec 003, I create a module by following a written convention, and my code can only reach other
modules through their public interface.
- *Given* code in one module that imports another module's internals, *when* CI runs, *then* the
  import check fails.

**US-4 — Change the database safely (P1).** As a backend developer, I add a table through a
versioned migration that runs as the owner role, while the application keeps running as the
restricted role.
- *Given* a fresh database, *when* migrations run, *then* the schema is created and the
  application role cannot create, alter or drop tables, and cannot bypass row-level security.

**US-5 — Consistent API behavior (P2).** As an Angular developer, I rely on every endpoint using
the same URL versioning, error shape, pagination and language negotiation, and I use a client
generated from the contract instead of hand-written calls.
- *Given* any API error, *when* I read the response, *then* it has the same structure with a
  machine-readable code and a message in the language requested by the caller (Arabic or English).

**US-6 — See what happened (P2).** As the on-call engineer, I find every log line for one request
by its request id, and logs never show secrets or personal data.

**US-7 — Bilingual app shell (P2).** As a user, I switch the web app between Arabic and English,
and the whole layout mirrors correctly, before any feature screens exist.

**US-8 — Build a release image (P3).** As DevOps, I build versioned container images from CI so
any server can run a known version.

## Functional requirements

### Repository and modules
- **FR-001** The repository follows the layout in `docs/HANDOFF.md` §12. Every top-level folder
  has a README saying what belongs there.
- **FR-002** The backend is one Python package with one sub-package per module (constitution
  Article V.2). The initial modules are empty shells named after the architecture layers' main
  modules; their contents come from later specs.
- **FR-003** A module may import another module only through that module's public interface.
  CI enforces this, and enforces that no layer imports a layer above it.
- **FR-004** A written module convention (`docs/architecture/modules.md`) states folder structure,
  naming, where tests live and how a module exposes its interface.

### Configuration and secrets
- **FR-005** All configuration comes from environment variables, validated at startup. The service
  refuses to start with a clear message if a required value is missing or invalid.
- **FR-006** `deploy/.env.example` lists every variable with a safe placeholder and a one-line
  description. No real secret appears anywhere in the repository.

### Database
- **FR-007** PostgreSQL with the pgvector extension. Schema changes happen only through versioned,
  reviewable migrations that run as the owner role.
- **FR-008** Three database roles exist: *owner* (migrations only), *app* (`NOSUPERUSER
  NOBYPASSRLS`, data access only, no DDL), and *readonly* (for support queries; no access to
  tables marked sensitive). Their creation is automated.
- **FR-009** The mechanism for setting tenant context per transaction exists and is tested here,
  even though the first tenant tables arrive in spec 002 (constitution Article III.4).
- **FR-010** Migrations can be applied to an empty database and to the previous release's schema
  in CI.

### API conventions
- **FR-011** All product endpoints live under `/api/v1/`. Health endpoints stay unversioned.
- **FR-012** Errors use one documented structure (RFC 9457 problem details) with a stable
  machine-readable `code`, and a human message localised from the request's language preference.
- **FR-013** The caller's language is taken from an explicit user preference when present,
  otherwise from `Accept-Language`, defaulting to Arabic. Supported values: `ar`, `en`.
- **FR-014** List endpoints use one pagination style, documented in the contract.
- **FR-015** `contracts/openapi.yaml` is the source of truth. CI fails if the running API's schema
  differs from the contract. The Angular API client is generated from the contract.
- **FR-016** Every request gets a request id, returned in a response header and included in logs.

### Background work
- **FR-017** A worker process and a scheduler run from the same codebase, using Redis as broker.
  A sample no-op task proves the worker is wired up; it is removed once a real task exists.

### Observability
- **FR-018** Logs are structured JSON (constitution Article VIII.2). A redaction filter removes
  values of known secret fields and is covered by tests.
- **FR-019** Liveness (`/health`) and readiness (`/health/ready`: database and Redis reachable)
  endpoints exist for the API and worker.
- **FR-020** Basic metrics are exposed for scraping: request count, latency and error rate per
  route, and queue depth.

### Frontend shell
- **FR-021** An Angular workspace (standalone components, signals) with an empty app shell: header,
  language switch (Arabic/English) and a placeholder home page.
- **FR-022** Switching language changes the document direction (`dir`) and language (`lang`) and
  mirrors the layout. Layout uses logical CSS properties only (start/end, not left/right); CI
  flags physical left/right properties in styles.
- **FR-023** Translation files exist for both languages; CI fails if a key exists in one language
  but not the other.
- **FR-024** Design tokens (colours, type, spacing, radius) are defined in one place with neutral
  placeholder values, so the chosen brand (ADR-0001) can replace them without touching components.
  An Arabic-capable font is loaded for Arabic.

### Local environment, CI and images
- **FR-025** One documented command starts database, Redis, API, worker and web app locally.
  Ollama stays an optional profile.
- **FR-026** CI on every pull request runs: backend lint, format, type check, unit and integration
  tests against real PostgreSQL + pgvector and Redis; the module-boundary check; migrations
  check; the contract check; frontend lint, unit tests, build, translation-key check;
  compose validation; secret scan; dependency licence check (AGPL-compatible).
- **FR-027** `main` is protected: merges need a green CI and one CODEOWNER approval; no direct
  pushes; squash merges only.
- **FR-028** A release workflow builds versioned API, worker and web images on a git tag and
  publishes them to the GitHub container registry. Deploying to a server is out of scope until
  ADR-0002 is resolved.

### Team workflow
- **FR-029** Templates exist for spec, plan and tasks (`specs/_templates/`), ADRs
  (`docs/adr/0000-template.md`), issues and pull requests. The PR template asks which spec and
  which FR/US items the PR implements.
- **FR-030** A GitHub Project board tracks specs and tasks with the columns Backlog, Spec in
  review, Ready, In progress, In review, Done.

## Out of scope
- Any product feature (companies, users, files, mapping, agents, chat). Identity is spec 002.
- Deployment to a real server, TLS and domains (after ADR-0002).
- Production backup and restore: proposed as new spec **041 backup-and-restore**, moved from R3 to
  R1 and due before week 8, because pilot data arrives at week 12 (constitution Article VIII.3).
- The LLM provider interface (spec 010) and file storage (spec 003).
- Final brand and visual identity (ADR-0001).

## Success criteria
- **SC-001** A developer who has not seen the repo has the full stack running locally in under 10
  minutes from clone (measured with two team members on Windows and one on Linux/macOS).
- **SC-002** CI for a backend-only pull request finishes in under 8 minutes; full CI in under 12.
- **SC-003** Each deliberately broken sample (lint error, cross-module import, contract drift,
  missing translation key, committed fake secret, app role attempting DDL) is caught by CI:
  6 out of 6.
- **SC-004** The app role provably cannot run `CREATE`, `ALTER`, `DROP` or `SET row_security = off`
  (automated test).
- **SC-005** Switching the shell between Arabic and English mirrors the layout with no
  horizontally misplaced element at 360 px, 768 px and 1440 px widths (screenshot check).
- **SC-006** Every log line for a request carries the same request id; a test log containing a
  password and an API key shows neither.

## Key entities
None. This spec creates no product tables.

## Assumptions
- Release 1 runs on a single Docker Compose host (HANDOFF §2); the provider is unknown (ADR-0002).
- Python 3.12, FastAPI, Pydantic v2, Celery + Redis, Angular with standalone components and
  signals (HANDOFF §2).
- The minimal `/health` code already on `main` is replaced or confirmed by this spec's plan; it is
  not grandfathered.

## Open questions
None blocking. Library choices (migration tool, import-boundary checker, metrics library) belong in
`plan.md`.
