# Constitution

**Version:** 1.0.0 · **Status:** Approved 2026-11-08 by product owner · **Last amended:** 2026-11-08

These rules bind every spec, plan, task and pull request. A spec or plan that conflicts with this
document is wrong until the constitution is amended. Amendments need a pull request that changes
this file, a version bump, and approval from the product owner and tech lead.

Precedence when sources disagree: **constitution > approved specs and `contracts/` > ADRs >
`docs/HANDOFF.md` > older PRD and project pack** (the PRD is HR-first and MongoDB-based; ignore those parts).

---

## Article I — Spec-driven delivery
1. Every feature starts as `specs/NNN-name/spec.md` (what and why, no implementation detail).
   It is written at least one sprint before it is built.
2. Order of artifacts: `spec.md` → owner approval → `plan.md` (how) → tech-lead approval →
   `tasks.md` → code. No application code is merged for a spec that is not approved.
3. Open questions are written as `[NEEDS CLARIFICATION: …]`. A spec with any of these left is not
   approvable.
4. API behavior is defined in `contracts/openapi.yaml` before code. Code that disagrees with the
   contract is a bug in the code.
5. Decisions with lasting effect are recorded as ADRs in `docs/adr/`.
6. A spec PR and its implementation PR are separate pull requests.

## Article II — Product rules
1. Arabic and English are first-class from release 1. Every user-facing string exists in both
   languages; every screen works right-to-left and left-to-right.
2. Every answer shows its route, source, import time and confidence. The agent never guesses:
   when no route answers with sufficient confidence, it records a gap.
3. Answer order: approved answers → data tools → documents and web pages → planner (one validated
   LLM call) → gap.
4. A feature is not done until its gap, error and empty states are specified and built.

## Article III — Tenancy and data isolation
1. Every tenant-owned table has `company_id`, and `workspace_id` where data belongs to a workspace
   (see ADR-0004). Global tables (for example domain packs, global synonyms, user identities) are
   listed explicitly in the spec that creates them, with the reason they are global.
2. Every tenant-owned table has `ENABLE` and `FORCE ROW LEVEL SECURITY` with policies keyed to the
   tenant context of the current transaction.
3. The application connects as a role that is `NOSUPERUSER NOBYPASSRLS` and does not own tables.
   The owner role is used only by migrations. Any other role (for example a reporting job that
   reads across companies) is defined in a spec, has the narrowest grants, and is audited.
4. Tenant context is set per transaction, never per connection, so pooled connections cannot leak
   context between requests. Background workers set it the same way.
5. Every spec that adds a tenant-owned table adds automated cross-tenant leak tests to CI. A failing
   leak test blocks merge.

## Article IV — AI boundaries
1. The AI never reads raw tables and never writes SQL. It calls tools. For unusual questions it
   returns a structured query plan that a validator checks against the agent spec and the caller's
   permissions.
2. The tool gateway is the only data path for chat and tasks; permissions, masking and audit
   happen there.
3. Mapping and agent generation make **zero LLM generation calls**. Embedding models are allowed
   for indexing and search.
4. Text from files, APIs and crawled pages is data, never instructions. It is never placed in a
   prompt position where it can change the agent's instructions.
5. All model access goes through the `LLMProvider` interface. Each call is metered.

## Article V — Architecture
1. Layers, top to bottom: presentation → gateway and identity → agent services → data intelligence
   → integration plugins → data and infrastructure. A layer may call any layer below it, never a
   layer above it. Cross-cutting services (security, audit, metering, config, plugin registry) may
   be called from any layer.
2. The backend is a modular monolith: one deployable API plus workers, with one Python package per
   module and imports only through each module's public interface. Splitting into services needs
   an ADR.
3. Prefer boring, well-supported libraries. A new runtime dependency needs a line in the plan with
   its licence (must be compatible with AGPL-3.0) and why.

## Article VI — Security and privacy
1. Never commit `.env` files, keys, dumps or real customer data. CI runs a secret scan on every PR.
2. Secrets supplied by customers (API keys, connector passwords) are encrypted at rest and never
   logged or returned by the API.
3. Personal data is masked before it is stored where masking is configured; analytics hide groups
   smaller than 5.
4. Customer data processing follows Egypt's Personal Data Protection Law (Law 151 of 2020).
   Hosting location and any cross-border transfer are decided by ADR before the first real
   customer data is loaded.
5. Every security-relevant action (login, role change, data export, tool call, approval) writes an
   audit event.

## Article VII — Quality
1. Test-first for backend logic: a failing test exists before the code that makes it pass.
2. Every endpoint has a contract test against `contracts/openapi.yaml`.
3. CI must be green to merge: lint, format, unit and integration tests (real PostgreSQL with
   pgvector), leak tests, contract tests, secret scan.
4. UI work passes an accessibility and RTL check (impeccable audit) before merge.
5. Quality targets in specs are numbers, not adjectives ("p95 under 300 ms", not "fast").

## Article VIII — Operations
1. Everything runs from `deploy/docker-compose.yml`; no hand-configured servers. The deployment is
   portable across providers until ADR-0002 is resolved.
2. Logs are structured JSON with a request id and, where known, company and workspace ids. Logs
   never contain secrets or unmasked personal data.
3. Backups are automated and a restore is tested before any real customer data is stored.

## Article IX — Open source
1. Licence: AGPL-3.0 (ADR-0005). Contributions require that the contributor has the right to
   submit the code under that licence.
2. Which features are open and which are paid-only (the open-core boundary) is decided by ADR
   before any plan gating is built (release 2).
