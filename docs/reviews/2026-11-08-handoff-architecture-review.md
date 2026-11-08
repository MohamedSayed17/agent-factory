# Architecture review of HANDOFF.md

**Date:** 2026-11-08 · **Reviewer:** senior architect review (Claude) · **Input:** `docs/HANDOFF.md`

Each finding names where it is now handled. "Open" means no spec or ADR owns it yet.

## Contradictions
| # | Finding | Handled by |
|---|---|---|
| C1 | Free chat runs on a local model, but the server proposal says "GPU only if local models serve production". Free chat *is* local models in production. A 7B model on 16 CPU cores serves about 1–2 concurrent conversations at a few tokens per second. | ADR-0002 (decide after week-1 model test); **open**: free-tier capacity and caps |
| C2 | AGPL open source vs paid-plan features: plan gating in public code is removable by any self-hoster. No open-core boundary. | ADR-0005, constitution Art. IX.2; **open** ADR before R2 |
| C3 | R1 includes the widget, task engine (014) and hand-off inbox (036), but approvals/actions and billing/plans are R2: R1 actions have no approval flow and Business-plan features have no gating. | **Open**: product owner to re-cut R1/R2 |
| C4 | Gap capture is R1 but the gap inbox and approved answers are R2, so the week-12 pilot cannot close the gap loop, the core value. | **Open**: recommend a minimal gap inbox in R1 |
| C5 | "Mapping and agent generation use zero AI calls" vs the knowledge index needing embeddings. | Constitution Art. IV.3 ("zero LLM generation calls") |
| C6 | "Every row has company_id + workspace_id" cannot apply to companies, users or global packs. | Constitution Art. III.1, spec 002 FR-015/016 |
| C7 | "Each layer calls only the one below": the planner (layer 3) needs the LLM gateway (layer 6). | Constitution Art. V.1 ("any layer below") |
| C8 | PRD is HR-first and MongoDB; HANDOFF says PostgreSQL. | Constitution precedence rule |

## Gaps
| # | Finding | Handled by |
|---|---|---|
| G1 | No authentication design, MFA policy or visitor model. | ADR-0003, spec 002; visitors spec 035 |
| G2 | How tenant context is set (per transaction, pooler-safe), for workers too, and cross-company jobs. | Constitution Art. III.3–4, spec 001 FR-009, spec 002 FR-018/020 |
| G3 | Vector search under RLS: approximate indexes plus company filters lose recall. | **Open**: spec 034 must choose filtering/partitioning |
| G4 | Egypt PDPL (Law 151/2020): residency, transfer licence, consent, DPO. | Constitution Art. VI.4, ADR-0002; **open**: legal check |
| G5 | Backups/restore planned for R3, but customer data arrives week 12. | Spec 001 out-of-scope note → proposed spec 041 in R1 |
| G6 | Encryption of customer API keys/secrets; file storage location, size limits, malware scanning. | Constitution Art. VI.2; **open**: specs 003, 013 |
| G7 | Observability: logs, metrics, alerts. | Spec 001 FR-016–020 |
| G8 | Migrations, generated client, contract tests. | Spec 001 FR-007–015 |
| G9 | Arabic text normalisation, Egyptian dialect vs MSA, Arabizi, numerals. | **Open**: specs 005 and 034 |
| G10 | Spikes (§13) have no pass/fail thresholds. | **Open**: set before week 0 ends |
| G11 | Email provider for verification, invitations, notifications. | Spec 002 FR-026 (interface); provider in plan |

## Risks
| # | Risk | Likelihood / impact | Mitigation |
|---|---|---|---|
| R1 | Scope: ~25 specs in 12 weeks with 2 Angular developers; mapping UX (column map, relationship graph) is heavy. | High / High | Re-cut R1 around one pilot journey; defer relationship graph and learned-rules screen |
| R2 | Arabic answer quality on a 7B local model. | Medium / High | Week-1 test with thresholds; `LLMProvider` allows a hosted model |
| R3 | A cross-tenant leak. | Low / Critical | Forced RLS, leak tests in CI (spec 002 SC-001), external review before pilot |
| R4 | Single server: no redundancy; Ollama competes with PostgreSQL. | Medium / High | Resource limits in compose, tested restore (spec 041), separate model host if needed |
| R5 | Prompt injection through crawled pages, spreadsheets and API data. | High / Medium | Constitution Art. IV.4; red-team evals in `evals/` |
| R6 | Self-built authentication has security bugs. | Medium / High | Maintained libraries only, ADR-0003, spec 002 SC-007 external review |
