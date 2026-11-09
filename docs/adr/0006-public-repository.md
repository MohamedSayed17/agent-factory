# ADR-0006 — Make the repository public now

**Status:** Accepted · **Date:** 2026-11-09 · **Deciders:** product owner
**Amends:** ADR-0005 ("private until the brand, trademark and domain checks are done")

## Context
Branch protection (spec 001 FR-027) is not available for private repositories on the GitHub Free
plan. The project is open source under AGPL-3.0 by design.

## Decision
The repository `MohamedSayed17/agent-factory` is public from 2026-11-09. The code name
`agent-factory` stays until the brand is chosen (ADR-0001).

## Consequences
- Branch protection on `main` becomes available (FR-027 unblocked).
- The name `agent-factory` and all history, specs and ADRs are public. Trademark and domain checks
  for the final brand (HANDOFF §3.6) are still required before the brand is announced.
- Links in `docs/HANDOFF.md` to Figma and claude.ai documents are visible; access to them is still
  controlled by their own sharing settings.
- Security reports must go through private vulnerability reporting (`SECURITY.md`); enable it in
  repository settings.
