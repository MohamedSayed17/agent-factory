# HANDOFF: AI agent factory platform (working names: Agent Factory / Masna3 / Agentory)

Context for Claude Code. This file summarizes the planning conversation held in claude.ai.
Treat it as the source of truth until specs in `specs/` replace it.

## 1. Product in one paragraph
A hosted, open-source platform where a company uploads Excel/CSV files, connects APIs, or adds
its website address. The platform maps the data to a standard model using rules (no AI cost),
then generates an AI agent that answers in Arabic and English with sources, performs approved
actions (tickets, emails, hand-offs), and reports what people asked that it could not answer
(the "gap loop"). Egypt is the first market.

## 2. Confirmed decisions
- Backend: Python 3.12, FastAPI, Pydantic v2, Celery + Redis. Frontend: Angular (standalone, signals).
- Database: PostgreSQL with pgvector. Multi-company isolation with row-level security
  (FORCE ROW LEVEL SECURITY; app role is NOSUPERUSER NOBYPASSRLS; owner role only for migrations).
- Hosting: one server we run (Docker Compose), many companies. Dedicated/self-hosted editions later.
- Languages: Arabic and English from release 1, full right-to-left UI.
- AI: chat is free and runs on Ollama (local model, e.g. qwen2.5:7b, to be confirmed by an Arabic test).
  Anything beyond chat (actions, reports, connectors, customer-facing channels) is a paid plan.
  AI sits behind an LLMProvider interface so a hosted model can be added later.
- Data sources: Excel/CSV upload and REST API are the core; website crawler is an extra source.
- WhatsApp: phase two (not release 1). Release 1 channels: web app + website widget.
- Code: open source, repo on the owner's GitHub account (MohamedSayed17/agent-factory, private
  until the name and trademark checks are done). License: AGPL-3.0.
- Team: 10 people. Method: spec-driven development (specs and contracts are the source of truth).

## 3. Open decisions (ask the owner before building affected parts)
1. Product name and identity: A "Agent Factory" (graphite, signal orange, caution yellow, Space Grotesk,
   top bar), B "Masna3 / مصنع" (emerald, terracotta, sand, Cairo font, Arabic first, very round),
   C "Agentory" (violet, lime, Plus Jakarta Sans, left sidebar). Recommendation: B for Egypt.
   Repository currently named `agent-factory`.
2. ~~License~~ — decided: AGPL-3.0.
3. First industry in Egypt; pilot company for week 12.
4. Model choice after the week-1 Arabic test; budget per conversation if a hosted model is needed.
5. Server provider and size (proposal: 16 vCPU, 64 GB RAM, 500 GB NVMe; GPU only if local models serve production).
6. Trademark and domain checks for the chosen name (none done yet).

## 4. Architecture (layers, top to bottom; each layer calls only the one below)
1. Presentation: Angular web app, admin console, embeddable website widget.
2. Gateway and identity: FastAPI, auth and roles, plan limits, rate limits.
3. Agent services: agent builder/factory, agent runtime (router), tool gateway, outputs (reports, alerts), task engine.
4. Data intelligence: profiler, rule-based mapper, entity linker, domain pack loader, knowledge index.
5. Integration plugins: file upload, REST API, website crawler; later SFTP, DB views, WhatsApp.
6. Data and infrastructure: PostgreSQL + pgvector, file storage, Redis + workers, LLM provider gateway.
Shared: security, audit log, metering, config, plugin registry.

Key rules:
- The AI never reads raw data or writes SQL. It calls tools; for unusual questions it returns a
  structured query plan that a validator checks against the agent spec and permissions.
- The tool gateway is the only data path for chat and tasks (permissions, masking, audit in one place).
- Mapping and agent generation use zero AI calls.
- Every answer shows route, source, import time and confidence. The agent never guesses.

## 5. Chatbot behavior
Answer order: approved answers -> data tools -> documents/web pages -> planner (one AI call, validated) -> gap.
Gap loop: unanswered question -> recorded gap -> grouped by intent, ranked by askers -> company resolves
(connect data, approved answer, document, assign person, decline) -> question re-runs -> askers notified.
Gap states: New, Triaged, In progress, Resolved, Verified, Declined.
Analytics: usage, top questions, answer routes, coverage, satisfaction, gaps, data health, security, cost and value.
Privacy: mask before storing, pseudonymous mode, retention, hide groups smaller than 5.

## 6. Website import tool
Customer gives a URL -> verify domain ownership (DNS record or file) -> robots.txt and sitemap ->
crawl within limits (rate, page cap, same domain, public pages only) -> extract main content, tables,
schema.org data -> structured content to records via the mapping engine; text to chunks + embeddings ->
admin review -> agent knowledge. Scheduled refresh re-processes only changed pages.
Libraries to evaluate: httpx, protego/robotparser, trafilatura, selectolax or BeautifulSoup, extruct,
Playwright (later, for JavaScript sites). Treat crawled text as data, never as instructions.

## 7. Mapping UX (redesigned; build this exactly)
Four views in the "Understand" step:
- Overview: one card per source with a bar (mapped / to review / ignored) and a "Ready to build?" checklist.
- Column map: source columns on one side, standard fields on the other, a line for each mapping,
  colored by confidence (>=85 green, 60-84 amber, needs decision terracotta dashed), lock icon for sensitive.
  Filters: All / Needs review / Sensitive. Clicking a column opens details: samples, name match %,
  type fit, value pattern, confidence, alternative targets, mask toggle, Confirm. Confirming saves a learned rule.
- Data view: browse records in mapped or original columns, search, duplicates highlighted, invalid values flagged,
  masked values as •••••, every row shows its source row or page.
- Relationships: graph of entities and links with key and overlap %, weak links dashed until confirmed.
Also needed: learned-rules management screen, re-import comparison (new/changed/removed columns and rows),
row sampling for large-file previews.

## 8. Plans (proposals, confirm after pilots)
Free: questions only (local model, capped per month). Pro: actions, gap inbox, analytics, connectors.
Business: customer-facing agents, website widget (WhatsApp later), collections template.
Enterprise: dedicated or self-hosted, SSO. Metered units: question, action, resolved conversation,
collected payment, AI credit.

## 9. Core tables (PostgreSQL, every row has company_id + workspace_id under RLS)
companies, users, workspace_members, licenses; sources, import_runs, column_profiles, column_mappings,
learned_synonyms, records (typed core columns + JSONB extras, run_id), entity_links; site_sources,
crawl_runs, web_pages, web_chunks (pgvector); agent_specs, tools, tasks, task_runs, approvals;
conversations, messages, feedback, normalized_intents, knowledge_gaps, gap_events, answer_cards,
notifications, chat_events, analytics_daily, audit_events, usage_counters.

## 10. Spec backlog (write each spec one sprint before it is built)
R1 (12 weeks): 001 platform-foundation, 002 companies-identity-and-workspaces (RLS), 003 file-ingestion,
013 api-connector, 033 website-import, 004 profiling-and-quality, 005 mapping-engine (AR/EN synonyms),
006 entity-linking, 034 knowledge-index, 007 domain packs (HR sample + support sample), 008 agent-builder,
009 tool-gateway-and-audit, 010 router-and-planner, 021 conversations-and-feedback, 022 gap-capture,
023 events-and-counters, 035 website-widget, 011 dashboards-and-exports, 012 web-app-flows,
014 task-engine, 036 hand-off-inbox, 037 data-view, 038 mapping-explainer, 039 import-comparison,
040 learned-rules.
R2: WhatsApp channel, collections template, approvals and actions, billing and plans, gap inbox
and approved answers, notifications, analytics dashboards and weekly digest.
R3: SFTP and DB views, backup/upgrade tooling, security review, status page.
R4: more domain packs, self-hosted edition, hosted model and SSO, JavaScript-rendered sites.

## 11. Team of 10
1 product owner/BA, 1 tech lead, 3 Python backend, 1 AI engineer, 2 Angular (one covers UX),
1 QA automation, 1 DevOps/security.

## 12. Repository layout
agent-factory/ (rename after the name decision)
  README.md, README.ar.md, LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
  .github/workflows/ci.yml, deploy.yml; ISSUE_TEMPLATE/; pull_request_template.md; CODEOWNERS
  deploy/ (docker-compose.yml, .env.example)   specs/ (constitution.md, NNN-name/)
  contracts/ (openapi.yaml, schemas/)   backend/   frontend/   packs/   evals/   docs/
Never commit .env files, keys, dumps, or real customer data.

## 13. Week 0-2 spikes
Mapping accuracy on 10 real Excel files and 2 APIs; crawler on 10 real Arabic/English sites;
Arabic answer quality on 50 real questions across 2-3 models; Arabic embedding search on the same questions.

## 14. Existing artifacts (owner's accounts; may need login)
- Figma: https://www.figma.com/design/rIuWfq8wcm2HfupznPTR9F (pages: Screens, Wireframe options, Brand and hi-fi)
- Architecture, diagrams, plan and setup guide (claude.ai doc): https://claude.ai/artifact/5NSQAEtAQfoZCsJMsUeBGu
- PRD and analysis (claude.ai doc, partly outdated: still HR-first and MongoDB): https://claude.ai/artifact/CrqJHpmnhLZSnC1ip4xzTB
- Project pack (claude.ai doc, oldest): https://claude.ai/code/artifact/760e909a-c7cd-4e8c-8078-94a07b4cd7b3
