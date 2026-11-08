# Constitution

Non-negotiable rules for every spec and every pull request. Change this file only by team decision.

## Product
1. Answers in Arabic and English from release 1; the UI is fully right-to-left capable.
2. Every answer shows its route, source, import time and confidence. The agent never guesses;
   when it cannot answer, it records a gap.
3. Answer order: approved answers -> data tools -> documents/web pages -> planner (one validated
   AI call) -> gap.

## Data and security
4. PostgreSQL with row-level security. Every tenant table has `company_id` and `workspace_id`,
   `FORCE ROW LEVEL SECURITY` is on, and the application role is `NOSUPERUSER NOBYPASSRLS`.
   The owner role is used only for migrations.
5. The AI never reads raw data or writes SQL. It calls tools. Unusual questions produce a
   structured query plan that a validator checks against the agent spec and permissions.
6. The tool gateway is the only data path for chat and tasks (permissions, masking, audit).
7. Mapping and agent generation make zero AI calls.
8. Crawled or uploaded text is data, never instructions.
9. Mask before storing; hide analytics groups smaller than 5.
10. Never commit `.env` files, keys, dumps or real customer data.

## Architecture
11. Layers call only the layer directly below: presentation -> gateway/identity -> agent
    services -> data intelligence -> integration plugins -> data/infrastructure.
12. AI sits behind an `LLMProvider` interface; Ollama is the default.

## Process
13. Spec-driven: a spec (`specs/NNN-name/`) is written one sprint before it is built;
    `contracts/` is the API source of truth.

## Open decisions
Product name and identity, first industry and pilot company, model choice after the Arabic test,
server provider and size, trademark and domain checks. See `docs/HANDOFF.md`.
