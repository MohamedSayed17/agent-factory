# ADR-0005 — Licence: AGPL-3.0

**Status:** Accepted · **Date:** 2026-11-08 · **Deciders:** product owner

## Decision
The repository is licensed under AGPL-3.0, so anyone who offers a modified version as a network
service must publish their changes.

## Consequences
- Dependencies must have AGPL-compatible licences; CI checks this (spec 001 FR-026).
- Plan gating in public code can be removed by anyone who self-hosts. The open-core boundary
  (which features stay open, which are paid-only or hosted-only) needs its own ADR before the R2
  billing spec.
- The repository stays private until the brand, trademark and domain checks are done.
