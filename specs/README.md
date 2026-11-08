# Specs

Specs are the source of truth for what we build. Rules: [constitution.md](constitution.md).

## Workflow
| Step | Artifact | Who approves | Tool |
|---|---|---|---|
| 1. Shape the idea | discussion, ADRs for decisions | product owner | Superpowers `brainstorming` |
| 2. Specify (what/why) | `NNN-name/spec.md` from `_templates/spec.md` | product owner | spec PR labelled `spec` |
| 3. Plan (how) | `NNN-name/plan.md` | tech lead | Superpowers `writing-plans` |
| 4. Break down | `NNN-name/tasks.md` → GitHub issues on the Project board | tech lead | |
| 5. Build | code PRs, test-first | 1 CODEOWNER + green CI | Superpowers `test-driven-development`, `subagent-driven-development` |
| 6. Review | PR review against spec FR/SC ids | reviewer | `code-review`, `security-review`, impeccable for UI |
| 7. Close | spec status → Done; drift fixed in spec, not only in code | tech lead | Superpowers `finishing-a-development-branch` |

A spec PR and its implementation PRs are separate. A spec with `[NEEDS CLARIFICATION]` cannot be approved.

## Status
| Spec | Title | Release | Status |
|---|---|---|---|
| — | constitution | — | **Approved** 1.0.0 (2026-11-08) |
| 001 | platform-foundation | R1 | **Approved** 2026-11-08 — next: plan.md |
| 002 | companies-identity-and-workspaces | R1 | Ready for approval (questions answered) |
| 041 | backup-and-restore (proposed, moved from R3) | R1 | Not written |

Full R1 backlog: `docs/HANDOFF.md` §10.
