# ADR-0004 — Workspaces are isolated areas inside a company

**Status:** Accepted · **Date:** 2026-11-08 · **Deciders:** product owner

## Context
HANDOFF §9 puts `company_id` and `workspace_id` on every row but does not define a workspace.

## Decision
A workspace is an isolated area inside a company (for example *HR*, *Support*). Sources, records,
agents, conversations and gaps belong to exactly one workspace. A person has one login and can be a
member of several companies and of several workspaces in each, with a role in each. Company owners
and admins can manage every workspace in their company.

## Consequences
- Row-level security checks both company and the set of workspaces the user may access.
- Identity tables (`users`, sessions) are global; membership tables carry the tenant ids.
- Sharing data between workspaces is not possible in R1; if needed later it requires a spec.
