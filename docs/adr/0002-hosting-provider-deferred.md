# ADR-0002 — Hosting provider: decide by week 8, stay portable until then

**Status:** Accepted (decision deferred) · **Date:** 2026-11-08 · **Deciders:** product owner

## Context
HANDOFF §3.5 proposes one 16 vCPU / 64 GB / 500 GB NVMe server. Egypt's Personal Data Protection
Law (Law 151 of 2020) restricts transferring personal data outside Egypt without a licence from the
data protection authority. Free chat on a local model (HANDOFF §2) may need a GPU in production.

## Decision
Sprint 1 targets local Docker and CI only. The provider is chosen **by week 8**, after (1) a legal
check of the cross-border transfer rules for the pilot's data and (2) the week-1 Arabic model test,
which tells us whether a GPU is needed. Until then everything must run from Docker Compose with no
provider-specific services.

## Consequences
- Spec 001 builds images and publishes them; it does not deploy to a server.
- Spec 041 (backup and restore) must be portable.
- Options to compare at week 8: an Egyptian data centre, a Gulf cloud region (AWS Bahrain/UAE,
  Azure UAE), an EU host (Hetzner). Criteria: legal fit, GPU availability, monthly cost, support.
