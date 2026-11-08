# ADR-0001 — Use "agent-factory" as the code name until the brand is chosen

**Status:** Accepted · **Date:** 2026-11-08 · **Deciders:** product owner

## Context
Three brand identities are proposed (HANDOFF §3.1): A "Agent Factory", B "Masna3 / مصنع"
(recommended for Egypt), C "Agentory". No trademark or domain checks have been done. Package names,
repository name and design tokens depend on the name.

## Decision
Code, packages, containers and the repository use the neutral code name `agent-factory`. The
public brand is chosen, after trademark and domain checks, **before the first frontend feature
sprint**. The brand appears only in translation files, design tokens and static assets, so
changing it does not touch code.

## Consequences
- Sprint 1 is not blocked.
- Spec 001 FR-024 requires design tokens with neutral placeholder values.
- Renaming the GitHub repository later keeps redirects; package names stay `agent-factory`.
