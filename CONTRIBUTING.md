# Contributing

## Workflow (spec-driven)
1. A feature starts as a spec in `specs/NNN-name/` (written one sprint before it is built).
2. API changes go into `contracts/openapi.yaml` first; code follows the contract.
3. Branch from `main`: `feat/NNN-short-name`, `fix/short-name`, `chore/short-name`.
4. Open a pull request using the template. CI must be green and one CODEOWNER must approve.

## Rules
- Never commit `.env` files, keys, database dumps or real customer data.
- Every table carries `company_id` and `workspace_id` and is covered by row-level security.
- The AI never reads raw data or writes SQL; it calls tools through the tool gateway.
- Mapping and agent generation use zero AI calls.
- User-facing text must exist in Arabic and English; UI must work right-to-left.

## Backend checks (same as CI)
```bash
cd backend
ruff check . && ruff format --check . && pytest
```
