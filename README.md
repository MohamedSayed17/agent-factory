# Agent Factory

> Working name. The final product name is still open (see `specs/constitution.md`).

An open-source, hosted platform that turns a company's data — Excel/CSV uploads, REST APIs and its
public website — into an AI agent that answers in **Arabic and English with sources**, performs
approved actions, and reports what people asked that it could not answer (the **gap loop**).
First market: Egypt.

## Status
Pre-release. Release 1 is planned over 12 weeks; specs live in [`specs/`](specs/).

## Stack
| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic v2, Celery + Redis |
| Frontend | Angular (standalone components, signals), full RTL |
| Database | PostgreSQL + pgvector, row-level security per company |
| AI | Ollama (local model) behind an `LLMProvider` interface |
| Hosting | Docker Compose on a single server |

## Repository layout
```
.github/     CI workflows, issue/PR templates, CODEOWNERS
deploy/      docker-compose.yml, .env.example
specs/       constitution.md and one folder per spec (NNN-name/)
contracts/   openapi.yaml and JSON schemas (source of truth for the API)
backend/     FastAPI service
frontend/    Angular web app, admin console and website widget
packs/       domain packs (field dictionaries, synonyms, sample agents)
evals/       answer-quality, mapping-accuracy and crawler evaluations
docs/        architecture and operations docs
```

## Local development
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on Linux/macOS
pip install -e ".[dev]"
pytest
uvicorn app.main:app --reload
```
Full stack (database, Redis, API):
```bash
cp deploy/.env.example deploy/.env   # then edit values
docker compose -f deploy/docker-compose.yml up -d
```

## Contributing
Spec-driven: every feature starts as a spec in `specs/`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License
[AGPL-3.0](LICENSE).
