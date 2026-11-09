# Platform Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `specs/001-platform-foundation/spec.md` (approved 2026-11-08) · **Status:** Approved 2026-11-09 by owner · execution: subagent-driven
**Task index:** `specs/001-platform-foundation/tasks.md`

**Goal:** Give the team one runnable, tested skeleton (backend, database roles, tenant context, API
conventions, worker, Angular bilingual shell, local stack, CI and release images) that every later
spec builds on, with no product features.

**Architecture:** A FastAPI modular monolith (`backend/app`) split into layer packages whose
import direction is enforced in CI, a cross-cutting `shared` package, PostgreSQL accessed through
SQLAlchemy as a restricted role with per-transaction tenant context, Celery workers from the same
codebase, and an Angular shell that switches Arabic/English at runtime. Everything runs from
`deploy/docker-compose.yml`.

**Tech stack:** Python 3.12 · uv · FastAPI · Pydantic v2 + pydantic-settings · SQLAlchemy 2 (sync) ·
psycopg 3 · Alembic · Celery 5 + Redis · structlog · prometheus-client · import-linter · mypy · ruff ·
pytest · Angular (latest stable major, ≥ 21) · Transloco · ng-openapi-gen · Stylelint +
stylelint-use-logical · Playwright · Docker Compose · GitHub Actions · GHCR.

## Constitution check
| Article | How this plan complies |
|---|---|
| I.4 contract-first | Task 12 makes CI fail when `app.openapi()` differs from `contracts/openapi.yaml`; Task 14 generates the client from the contract |
| III.3 restricted app role | Task 8 creates `af_owner`, `af_app` (`NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE`), `af_readonly` |
| III.4 per-transaction context | Task 9 uses `set_config(..., true)` (transaction-local) only |
| V.1 layer direction | Task 3 enforces it with import-linter |
| V.3 dependency licences | Every new dependency is listed below; Task 17 adds a licence check to CI |
| VI.1 no secrets | `.env.example` placeholders only; gitleaks already in CI |
| VII.1 test-first | Every task starts with a failing test |
| VIII.2 structured, redacted logs | Task 4 |

## Decisions the implementer must not change
1. **Sync SQLAlchemy, not async.** FastAPI runs `def` endpoints in its thread pool; Celery is sync. One
   data-access path for API and workers is worth more than async throughput on a single server.
2. **uv** manages Python dependencies (`backend/uv.lock` committed; CI runs `uv sync --frozen`).
3. **Package layout** under `backend/app/`:
   `shared` (cross-cutting) and five layer packages, top to bottom:
   `gateway` → `agents` → `intelligence` → `integrations` → `infra`. (Presentation is the Angular app.)
4. **Public interface rule:** a module is `app/<layer>/<module>/`. Its public interface is what its
   `__init__.py` exports. Any other submodule is private. Code outside the module imports only
   `app.<layer>.<module>` (never `app.<layer>.<module>.<anything>`). `app.shared.*` submodules are public.
5. **Database roles:** `af_owner` owns schema `app` and all tables; `af_app` gets DML through
   default privileges; `af_readonly` gets nothing by default and is granted `SELECT` per table by the
   migration helper `grant_readonly(table)` only for tables not marked sensitive.
6. **Tenant context settings:** `app.user_id`, `app.company_id`, `app.workspace_ids` (comma-separated
   UUIDs), always set with `set_config(name, value, true)`. SQL helpers `app.current_company_id()`
   and `app.current_workspace_ids()` are created in the baseline migration for spec 002's policies.
7. **Error format:** RFC 9457 `application/problem+json` with fields
   `type, title, status, detail, code, instance, request_id` and optional `errors` (validation).
8. **Pagination:** cursor style. Query `limit` (1–100, default 25) and `cursor` (opaque string).
   Response `{"items": [...], "next_cursor": string | null}`.
9. **Request id header:** `X-Request-ID`. An incoming value is kept only if it matches
   `^[A-Za-z0-9-]{8,64}$`; otherwise a new UUID4 is generated.
10. **Language:** `ar` default; `Content-Language` header on every API response.
11. **Worker image:** API, worker and beat share one backend image (`agent-factory-backend`) with
    different commands. The web app has its own image (`agent-factory-web`). This satisfies FR-028's
    "API, worker and web images" with two built images.
12. **Worker health (deviation for tech-lead sign-off):** FR-019 asks for worker health endpoints.
    Celery workers have no HTTP server; the plan uses a CLI health command
    (`python -m app.infra.workers.health`) wired to the compose `healthcheck`, which checks Redis
    and a `ping` round-trip. Adding an HTTP server to the worker would be extra code for no
    consumer. If the tech lead requires HTTP, add a sidecar in a later task.

## New dependencies (licence → why)
Backend runtime: `fastapi` (MIT), `uvicorn[standard]` (BSD-3), `pydantic` / `pydantic-settings` (MIT),
`sqlalchemy` (MIT), `psycopg[binary]` (LGPL-3.0, AGPL-compatible), `alembic` (MIT), `celery[redis]`
(BSD-3), `redis` (MIT), `structlog` (MIT/Apache-2.0), `prometheus-client` (Apache-2.0),
`pyyaml` (MIT, contract loading).
Backend dev: `pytest`, `httpx`, `ruff`, `mypy`, `import-linter` (BSD-2), `pip-licenses` (MIT),
`types-PyYAML`.
Frontend: Angular (MIT), `@jsverse/transloco` (MIT), `ng-openapi-gen` (MIT), `@fontsource/noto-sans`
and `@fontsource/noto-sans-arabic` (OFL-1.1, self-hosted, no external font CDN), `stylelint` +
`stylelint-config-standard-scss` (MIT), `stylelint-use-logical` (CC0-1.0), `@playwright/test`
(Apache-2.0), `license-checker-rseidelsohn` (BSD-3).

## Global constraints
- Python `>=3.12,<3.13`; Docker base `python:3.12-slim`; Node 24 LTS in CI and the web image.
- Product endpoints only under `/api/v1/`; `/health`, `/health/ready`, `/metrics` unversioned.
- Supported languages exactly `ar`, `en`; default `ar`.
- Every environment variable appears in `deploy/.env.example` with a placeholder and a one-line comment.
- No physical `left`/`right` CSS properties or values in `frontend/src/**/*.scss`.
- Licence allow-list (both stacks): MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, MPL-2.0,
  LGPL-2.1, LGPL-3.0, AGPL-3.0, GPL-3.0, Python-2.0, PSF-2.0, CC0-1.0, OFL-1.1, 0BSD, Unlicense.
- `/docs` and `/openapi.json` are served only when `APP_ENV` is `local` or `test`.

## Review focus
1. **Forged or oversized `X-Request-ID`** (log injection, 10 KB header, newline) → replaced by a
   fresh UUID; the forged value never reaches logs. Test in Task 4.
2. **Unusual `Accept-Language`** (`ar-EG`, `EN-us;q=0.9`, `*`, `fr`, `;;;q=abc`, empty) → `ar-EG`→`ar`,
   `EN-us`→`en`, `fr`/`*`/garbage/empty → `ar`; never a 500. Test in Task 5.
3. **Secrets inside strings**, e.g. a startup error printing `DATABASE_URL` with its password, or
   `postgresql://u:p@h` inside an exception message → password replaced by `***`. Tests in Tasks 2 and 4.
4. **A request that fails mid-transaction on a pooled connection** → the next request on that
   connection sees no tenant context. Test in Task 9.
5. **Operational endpoints reachable in production** (`/docs`, `/openapi.json`, `/metrics` without a
   token) → 404. Tests in Tasks 6 and 10.

---

## Part A — Backend and database

### Task 1: Backend tooling baseline

**Files:**
- Modify: `backend/pyproject.toml` (deps above, `[tool.mypy]` strict for `app`, pytest markers `unit`, `integration`)
- Create: `backend/uv.lock` (generated), `backend/.python-version` (`3.12`)
- Modify: `.github/workflows/ci.yml` (backend job: `astral-sh/setup-uv`, `uv sync --frozen`, add `uv run mypy app`)
- Modify: `.github/dependabot.yml` (`pip` ecosystem → `uv`)

**Interfaces:** Produces the commands every later task uses: `uv run pytest -m unit`,
`uv run pytest -m integration`, `uv run mypy app`, `uv run ruff check .`, `uv run ruff format --check .`.

- [ ] **Step 1:** Mark the two existing tests: `test_health_returns_ok` as `unit`, `test_pgvector_extension_available` as `integration`. Configure pytest `--strict-markers` so an unknown marker fails.
- [ ] **Step 2:** Run `uv run pytest` — expected: 1 passed, 1 skipped locally (no DB).
- [ ] **Step 3:** Run `uv run mypy app` and `uv run ruff check .` — expected: both clean.
- [ ] **Step 4:** Commit `chore(backend): uv, mypy and pytest markers (spec 001 FR-026)`.

### Task 2: Validated settings

**Files:**
- Modify: `backend/app/config.py` → move to `backend/app/shared/config.py`; update the import in the current `backend/app/main.py` so the app keeps starting until Task 6 replaces it
- Modify: `deploy/.env.example`
- Test: `backend/tests/shared/test_config.py`

**Interfaces:**
- Produces: `class Settings(BaseSettings)` with fields
  `app_env: Literal["local","test","staging","production"]`, `log_level: Literal["DEBUG","INFO","WARNING","ERROR"] = "INFO"`,
  `database_url: PostgresDsn` (app role), `database_owner_url: PostgresDsn | None` (migrations only),
  `redis_url: RedisDsn`, `default_language: Literal["ar","en"] = "ar"`, `metrics_token: SecretStr | None = None`,
  `cors_origins: list[str] = []`; and `get_settings() -> Settings` (cached).
- Produces: `format_settings_error(exc: ValidationError) -> str` — one line per invalid field, no values.

- [ ] **Step 1: Failing tests**
```python
def test_missing_database_url_is_reported_by_name(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(ValidationError) as e: Settings(_env_file=None)
    assert "database_url" in format_settings_error(e.value)

def test_settings_error_never_prints_secret_values(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "not-a-url-with-s3cret")
    with pytest.raises(ValidationError) as e: Settings(_env_file=None)
    assert "s3cret" not in format_settings_error(e.value)

def test_language_must_be_ar_or_en(monkeypatch): ...  # DEFAULT_LANGUAGE=fr → error naming default_language
```
- [ ] **Step 2:** Run `uv run pytest tests/shared/test_config.py` — expected: FAIL (import error).
- [ ] **Step 3:** Implement. The API entry point (`app/main.py`, Task 6) catches `ValidationError` from `get_settings()`, prints `format_settings_error(...)` to stderr and exits with code 2.
- [ ] **Step 4:** Rewrite `deploy/.env.example`: every Settings field plus `POSTGRES_*`, `AF_OWNER_PASSWORD`, `AF_APP_PASSWORD`, `AF_READONLY_PASSWORD`, `API_PORT`, `WEB_PORT`, `OLLAMA_MODEL`, each with a `# one-line description` and a placeholder like `change-me-local-only`.
- [ ] **Step 5:** Tests pass; commit `feat(shared): validated settings (FR-005, FR-006)`.

### Task 3: Module skeleton and boundary enforcement

**Files:**
- Create: `backend/app/{shared,gateway,agents,intelligence,integrations,infra}/__init__.py`
- Create empty module shells (only `__init__.py` with a one-line docstring naming the future spec):
  `gateway/{identity,api}`, `agents/{builder,runtime,tools,tasks,outputs}`,
  `intelligence/{profiling,mapping,linking,packs,knowledge}`, `integrations/{files,rest_api,web}`,
  `infra/{db,workers,storage,llm}`
- Create: `backend/.importlinter` (layers contract: `app.gateway`, `app.agents`, `app.intelligence`, `app.integrations`, `app.infra`; forbidden contract: `app.shared` may not import any layer package)
- Create: `backend/tests/architecture/test_module_boundaries.py`, `backend/tests/architecture/fixtures/` (a tiny fake package used by the test)
- Create: `docs/architecture/modules.md` (FR-004: the rules in Decisions 3–4, folder layout, tests live in `backend/tests/<layer>/<module>/`, how to add a module, example)
- Modify: CI backend job: `uv run lint-imports`

**Interfaces:**
- Produces: `find_boundary_violations(root: Path, package: str = "app") -> list[Violation]`,
  `Violation(file: Path, line: int, imported: str)`; rule from Decision 4.

- [ ] **Step 1: Failing tests**
```python
def test_importing_another_modules_private_submodule_is_a_violation(tmp_path):
    # fixture: app/agents/builder/__init__.py and app/gateway/api/_routes.py containing
    # "from app.agents.builder.service import X"
    assert [v.imported for v in find_boundary_violations(fixture_root)] == ["app.agents.builder.service"]

def test_importing_a_module_package_itself_is_allowed(...)      # "from app.agents.builder import X" → []
def test_importing_own_private_submodule_is_allowed(...)         # inside app/agents/builder → []
def test_shared_submodules_are_public(...)                       # "from app.shared.config import Settings" → []
def test_real_codebase_has_no_violations():
    assert find_boundary_violations(Path("app")) == []
```
- [ ] **Step 2:** Run — FAIL. **Step 3:** Implement with `ast` (handle `import x.y` and `from x.y import z`, ignore relative imports inside the same module).
- [ ] **Step 4:** Add a temporary file in `app/gateway` that imports `app.agents` and confirm `uv run lint-imports` fails; remove it.
- [ ] **Step 5:** Tests and `lint-imports` pass; commit `feat(arch): layer packages and import boundaries (FR-002, FR-003, FR-004)`.

### Task 4: Request id, structured logging, redaction

**Files:**
- Create: `backend/app/shared/request_id.py`, `backend/app/shared/logging.py`
- Test: `backend/tests/shared/test_request_id.py`, `backend/tests/shared/test_logging.py`

**Interfaces:**
- Produces: `REQUEST_ID_HEADER = "X-Request-ID"`; `RequestIdMiddleware` (pure ASGI) that sets
  `request_id_var: ContextVar[str]` and the response header; `accept_or_generate(value: str | None) -> str`.
- Produces: `configure_logging(level: str) -> None` (structlog JSON to stdout, fields `timestamp, level, event, request_id`, plus `company_id`/`workspace_id` when bound); `redact(event_dict) -> event_dict` processor.
- Redacted keys (case-insensitive, substring match): `password, passwd, secret, token, api_key, apikey, authorization, cookie, set-cookie, private_key, dsn`. Values become `"***"`, recursively in dicts and lists. String values are also scanned for `scheme://user:password@` and the password part replaced with `***`.

- [ ] **Step 1: Failing tests**
```python
@pytest.mark.parametrize("bad", ["", "short", "x"*65, "abc\ninjected", "a b c d e f g h"])
def test_invalid_incoming_request_id_is_replaced(bad):
    rid = accept_or_generate(bad); assert rid != bad and uuid.UUID(rid)

def test_valid_incoming_request_id_is_kept(): assert accept_or_generate("abcd-1234-efgh") == "abcd-1234-efgh"

def test_all_log_lines_of_one_request_share_its_id(client, capsys):  # SC-006
    r = client.get("/health", headers={"X-Request-ID": "req-12345678"})
    lines = [json.loads(l) for l in capsys.readouterr().out.splitlines() if l]
    assert r.headers["X-Request-ID"] == "req-12345678" and lines
    assert {l["request_id"] for l in lines} == {"req-12345678"}

def test_secrets_are_redacted(capsys):                               # SC-006
    log.info("connect", password="hunter2", api_key="sk-live-123",
             nested={"Authorization": "Bearer abc"}, url="postgresql://u:pa55@db/x")
    out = capsys.readouterr().out
    for s in ("hunter2", "sk-live-123", "Bearer abc", "pa55"): assert s not in out
```
- [ ] **Step 2:** Run — FAIL. **Step 3:** Implement. Uvicorn access logs go through the same structlog pipeline.
- [ ] **Step 4:** Pass; commit `feat(shared): request id and redacted JSON logs (FR-016, FR-018, SC-006)`.

### Task 5: Language negotiation and message catalogs

**Files:**
- Create: `backend/app/shared/i18n.py`, `backend/app/shared/messages/ar.json`, `backend/app/shared/messages/en.json`
- Test: `backend/tests/shared/test_i18n.py`

**Interfaces:**
- Produces: `Language = Literal["ar", "en"]`;
  `negotiate_language(accept_language: str | None, user_preference: str | None, default: Language = "ar") -> Language`;
  `translate(key: str, lang: Language, **params: str) -> str` (raises `KeyError` for unknown keys in tests, falls back to the key in production);
  `language_var: ContextVar[Language]` set by `LanguageMiddleware`, which also sets `Content-Language`.
  `user_preference` is always `None` until spec 002 supplies it.

- [ ] **Step 1: Failing tests**
```python
@pytest.mark.parametrize("header,expected", [
    ("ar-EG,ar;q=0.9", "ar"), ("EN-us;q=0.9", "en"), ("fr-FR, en;q=0.5", "en"),
    ("fr", "ar"), ("*", "ar"), (";;;q=abc", "ar"), ("", "ar"), (None, "ar"),
    ("en;q=0.2, ar;q=0.8", "ar")])
def test_negotiate_language(header, expected): assert negotiate_language(header, None) == expected

def test_user_preference_wins(): assert negotiate_language("ar", "en") == "en"
def test_catalogs_have_identical_keys(): assert keys(ar) == keys(en)
def test_content_language_header_is_set(client): assert client.get("/health", headers={"Accept-Language": "en"}).headers["Content-Language"] == "en"
```
- [ ] **Step 2:** FAIL → **Step 3:** implement (parse q-values; invalid q counts as 0; primary subtag match, case-insensitive) → **Step 4:** PASS → **Step 5:** commit `feat(shared): language negotiation (FR-013)`.

### Task 6: App factory, `/api/v1`, problem-details errors

**Files:**
- Create: `backend/app/main.py` (replace current), `backend/app/shared/errors.py`, `backend/app/gateway/api/__init__.py` (exports `api_router`), `backend/app/gateway/api/_meta.py`
- Test: `backend/tests/gateway/api/test_errors.py`, `backend/tests/gateway/api/test_meta.py`

**Interfaces:**
- Produces: `create_app(settings: Settings) -> FastAPI` and module-level `app = create_app(get_settings())` guarded by the startup error handling from Task 2.
- Produces: `class AppError(Exception)` with `code: str`, `status: int`, `message_key: str`, `params: dict[str, str]`; subclasses `NotFoundError` (`not_found`, 404), `ConflictError` (`conflict`, 409), `PermissionDeniedError` (`permission_denied`, 403). Handlers for `AppError`, `RequestValidationError` (`validation_error`, 422, `errors=[{"field","message"}]`), `StarletteHTTPException`, and `Exception` (`internal_error`, 500, never exposes the exception text).
- Produces: `GET /api/v1/meta` → `{"version": str, "languages": ["ar","en"], "default_language": "ar"}`.
- Message keys in both catalogs: `error.not_found`, `error.conflict`, `error.permission_denied`, `error.validation`, `error.internal`, `error.method_not_allowed`.

- [ ] **Step 1: Failing tests**
```python
def test_unknown_route_is_problem_json_in_requested_language(client):
    r = client.get("/api/v1/nope", headers={"Accept-Language": "en"})
    assert r.status_code == 404 and r.headers["content-type"].startswith("application/problem+json")
    body = r.json(); assert body["code"] == "not_found" and body["request_id"] == r.headers["X-Request-ID"]
    assert body["title"] == translate("error.not_found", "en")

def test_same_error_in_arabic(client): ...  # title == translate("error.not_found", "ar")
def test_unhandled_exception_hides_details(client_with_boom_route):
    r = client_with_boom_route.get("/boom"); assert r.status_code == 500 and "secret detail" not in r.text
def test_validation_error_lists_fields(client_with_typed_route): ...
def test_docs_hidden_in_production(): assert TestClient(create_app(settings(app_env="production"))).get("/docs").status_code == 404
def test_meta(client): assert client.get("/api/v1/meta").json()["default_language"] == "ar"
```
- [ ] **Step 2:** FAIL → **Step 3:** implement; middleware order (outermost first): RequestId → Language → (metrics, inserted here by Task 10) → routes → **Step 4:** PASS
- [ ] **Step 5:** Commit `feat(api): app factory, /api/v1 and problem details (FR-011, FR-012)`.

### Task 7: Pagination model

**Files:** Create `backend/app/shared/pagination.py`; Test `backend/tests/shared/test_pagination.py`

**Interfaces:**
- Produces: `class Page(BaseModel, Generic[T])`: `items: list[T]`, `next_cursor: str | None`;
  `class PageParams` dependency: `limit: int = Query(25, ge=1, le=100)`, `cursor: str | None = Query(None, max_length=512)`;
  `encode_cursor(values: dict[str, str]) -> str` / `decode_cursor(cursor: str) -> dict[str, str]` (URL-safe base64 JSON; `decode_cursor` raises `AppError(code="invalid_cursor", status=400, message_key="error.invalid_cursor")` on bad input).

- [ ] **Step 1: Failing tests:** round-trip; `decode_cursor("%%%")` → `invalid_cursor` 400 problem; `limit=0` and `limit=101` → 422 `validation_error`.
- [ ] **Step 2–4:** FAIL → implement → PASS (add `error.invalid_cursor` to both catalogs).
- [ ] **Step 5:** Commit `feat(shared): cursor pagination (FR-014)`.

### Task 8: Database roles, Alembic baseline, grants

**Files:**
- Create: `backend/app/infra/db/__init__.py` (exports `get_engine`, `grant_readonly`; Task 9 adds its exports)
- Create: `backend/app/infra/db/_engine.py`, `backend/app/infra/db/_grants.py`
- Create: `backend/scripts/db_bootstrap.py`, `backend/alembic.ini`, `backend/migrations/env.py`, `backend/migrations/versions/0001_baseline.py`
- Test: `backend/tests/infra/db/test_roles.py` (integration)

**Interfaces:**
- `db_bootstrap.py` (run with an admin URL, idempotent): creates roles `af_owner` (LOGIN, NOSUPERUSER, NOCREATEROLE), `af_app` and `af_readonly` (LOGIN, `NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE`), passwords from `AF_*_PASSWORD`; creates extension `vector`; creates schema `app` owned by `af_owner`; `REVOKE CREATE ON SCHEMA public FROM PUBLIC`.
- `0001_baseline` (runs as `af_owner`): `GRANT USAGE ON SCHEMA app TO af_app, af_readonly`; `ALTER DEFAULT PRIVILEGES FOR ROLE af_owner IN SCHEMA app GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO af_app` and `GRANT USAGE, SELECT ON SEQUENCES TO af_app`; creates `app.current_company_id() RETURNS uuid`, `app.current_user_id() RETURNS uuid`, `app.current_workspace_ids() RETURNS uuid[]` (each `STABLE`, returning NULL / empty array when the setting is unset or empty).
- `grant_readonly(table: str) -> None` for use inside migrations.
- `get_engine(url: str) -> Engine` (pool_pre_ping, `search_path=app`).

- [ ] **Step 1: Failing integration tests** (fixture: fresh database, bootstrap, `alembic upgrade head`, connect as `af_app`)
```python
@pytest.mark.parametrize("ddl", ["CREATE TABLE app.x (id int)", "ALTER TABLE app.probe ADD COLUMN y int",
                                 "DROP TABLE app.probe", "CREATE SCHEMA evil", "CREATE TABLE public.x (id int)"])
def test_app_role_cannot_run_ddl(app_conn, ddl):                         # SC-004
    with pytest.raises(psycopg.errors.InsufficientPrivilege): app_conn.execute(ddl)

def test_row_security_off_does_not_bypass_rls(app_conn, rls_probe):     # SC-004
    app_conn.execute("SET row_security = off")
    with pytest.raises(psycopg.errors.InsufficientPrivilege): app_conn.execute("SELECT * FROM app.rls_probe")

def test_app_role_attributes(admin_conn):
    r = admin_conn.execute("select rolsuper, rolbypassrls, rolcreatedb, rolcreaterole from pg_roles where rolname='af_app'").one()
    assert r == (False, False, False, False)

def test_readonly_sees_nothing_by_default(readonly_conn, probe_table): ...  # InsufficientPrivilege
def test_bootstrap_is_idempotent(admin_url): run_bootstrap(admin_url); run_bootstrap(admin_url)
def test_migrations_downgrade_and_upgrade(owner_url): ...  # base → head → base → head
```
`rls_probe`/`probe_table` are created by the test fixture as `af_owner` (FORCE RLS, policy on `app.current_company_id()`), never by a migration.
- [ ] **Step 2:** Run `uv run pytest -m integration tests/infra/db` against the CI-style database — FAIL.
- [ ] **Step 3:** Implement; replace `tests/test_database.py` with these tests.
- [ ] **Step 4:** PASS. **Step 5:** Commit `feat(db): roles, baseline migration, grants (FR-007, FR-008, FR-010, SC-004)`.

### Task 9: Tenant context per transaction

**Files:** Create `backend/app/infra/db/_tenant.py`; Modify `backend/app/infra/db/__init__.py` (add exports `TenantContext`, `session_scope`, `tenant_session`); Test `backend/tests/infra/db/test_tenant_context.py` (integration)

**Interfaces:**
- Produces: `@dataclass(frozen=True) class TenantContext: user_id: UUID; company_id: UUID; workspace_ids: frozenset[UUID]`.
- Produces: `session_scope(engine: Engine) -> Iterator[Session]` (commit on success, rollback on error) and
  `tenant_session(engine: Engine, ctx: TenantContext) -> Iterator[Session]`, which calls
  `set_config('app.user_id'|'app.company_id'|'app.workspace_ids', value, true)` as the first statement of the transaction.

- [ ] **Step 1: Failing tests** (using `rls_probe` with rows for companies A and B)
```python
def test_no_context_sees_no_rows(engine): with session_scope(engine) as s: assert count(s) == 0
def test_context_sees_only_own_company(engine): with tenant_session(engine, ctx_a) as s: assert companies(s) == {A}
def test_context_does_not_survive_commit(engine_pool_size_1):
    with tenant_session(engine_pool_size_1, ctx_a): pass
    with session_scope(engine_pool_size_1) as s: assert count(s) == 0
def test_context_does_not_survive_failed_transaction(engine_pool_size_1):     # Review focus 4
    with pytest.raises(RuntimeError):
        with tenant_session(engine_pool_size_1, ctx_a): raise RuntimeError
    with session_scope(engine_pool_size_1) as s: assert count(s) == 0
def test_insert_for_other_company_is_refused(engine): ...  # WITH CHECK → InsufficientPrivilege/CheckViolation
def test_workspace_ids_round_trip(engine): ...             # app.current_workspace_ids() = sorted ctx ids
```
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** Commit `feat(db): per-transaction tenant context (FR-009)`.

### Task 10: Health, readiness, metrics

**Files:** Create `backend/app/gateway/api/_health.py`, `backend/app/shared/metrics.py`; Test `backend/tests/gateway/api/test_health.py`, `backend/tests/shared/test_metrics.py`

**Interfaces:**
- `GET /health` → 200 `{"status":"ok"}` (no dependencies touched).
- `GET /health/ready` → 200 `{"status":"ok","database":"ok","redis":"ok"}` or 503 with the failing part set to `"unreachable"`; each check has a 2-second timeout.
- `GET /metrics` → Prometheus text; requires `Authorization: Bearer <METRICS_TOKEN>`; 404 when `METRICS_TOKEN` is unset, 401 on a wrong token.
- Metrics: `http_requests_total{method,route,status}`, `http_request_duration_seconds{method,route}` (histogram), `celery_queue_length{queue}` (gauge, read from Redis `LLEN` at scrape time). `route` is the route template (`/api/v1/meta`), never the raw path; unmatched paths are labelled `unmatched`.

- [ ] **Step 1: Failing tests:** ready returns 503 with `"database":"unreachable"` when the DB URL points nowhere (unit, fake checker); ready 200 (integration); metrics 404 without token config, 401 wrong token, 200 right token and contains `http_requests_total`; requesting `/api/v1/meta/<random>` 100 times creates no new `route` label values.
- [ ] **Step 2–4:** FAIL → implement → PASS; delete the old `tests/test_health.py`.
- [ ] **Step 5:** Commit `feat(ops): health, readiness and metrics (FR-019, FR-020)`.

### Task 11: Worker and scheduler

**Files:** Create `backend/app/infra/workers/__init__.py` (exports `celery_app`, `ping`), `_celery.py`, `_tasks.py`, `health.py`; Test `backend/tests/infra/workers/test_worker.py`

**Interfaces:**
- `celery_app = Celery("agent_factory", broker=settings.redis_url, backend=settings.redis_url)`; JSON serializer only; `task_acks_late=True`; logging via `configure_logging`.
- Task `app.infra.workers.ping() -> str` returns `"pong"` (sample; delete when spec 003 adds a real task).
- Beat schedule: `ping` every 5 minutes (proves beat runs; removed with the sample task).
- `python -m app.infra.workers.health` exits 0 if Redis answers and a `ping` round-trip completes within 10 s, else 1.

- [ ] **Step 1: Failing tests:** `ping.apply().get() == "pong"` (eager, unit); integration: a worker started in a subprocess processes `ping.delay()` within 10 s; health command exits 0 with worker running and 1 with Redis URL pointing nowhere.
- [ ] **Step 2–4:** FAIL → implement → PASS. **Step 5:** Commit `feat(workers): celery worker, beat and health (FR-017, FR-019)`.

### Task 12: Contract as source of truth

**Files:** Modify `contracts/openapi.yaml`; Create `backend/scripts/export_openapi.py`, `backend/tests/contract/test_openapi_contract.py`

**Interfaces:**
- `contracts/openapi.yaml` describes `/health`, `/health/ready`, `/api/v1/meta`, components `Problem`, `ValidationProblem`, `Page` (with `items`, `next_cursor`), parameters `Limit`, `Cursor`, header `X-Request-ID`, and the 4xx/5xx `application/problem+json` responses.
- `export_openapi.py` prints `app.openapi()` as YAML (helps authors, never writes the contract automatically).

- [ ] **Step 1: Failing test**
```python
def test_running_api_matches_contract():
    contract = yaml.safe_load(Path("../contracts/openapi.yaml").read_text())
    assert normalise(create_app(test_settings()).openapi()) == normalise(contract)
```
`normalise` drops `info.description` and sorts keys; anything else differing fails with a readable diff.
- [ ] **Step 2–4:** FAIL → write the contract by hand and set FastAPI route metadata (`operation_id`, response models, `responses=`) until equal → PASS.
- [ ] **Step 5:** Commit `feat(contract): contract test (FR-015)`.

## Part B — Frontend shell

### Task 13: Angular workspace and bilingual shell

**Files:** Create the Angular workspace in `frontend/` (app name `web`, standalone, zoneless, SCSS, routing, no SSR); `src/app/core/language.service.ts`, `src/app/shell/shell.component.{ts,html,scss}`, `src/app/home/home.component.ts`, `src/assets/i18n/{ar,en}.json`, `src/styles/_tokens.scss`, `src/styles.scss`, `proxy.conf.json` (`/api` and `/health` → `http://localhost:8000`). Tests next to each file (`*.spec.ts`, CLI default runner).

**Interfaces:**
- `LanguageService`: `readonly lang: Signal<'ar'|'en'>`, `readonly dir: Signal<'rtl'|'ltr'>`, `set(lang: 'ar'|'en'): void`. On change: sets `<html lang dir>`, calls Transloco `setActiveLang`, stores the choice under `localStorage['af.lang']` inside try/catch. Initial value: stored choice, else `navigator.language` primary subtag if `ar`/`en`, else `ar`.
- Shell: header with app name (`app.name`), a language toggle button (`shell.switch_to` → shows the *other* language's name), `<main>` with router outlet; home shows `home.placeholder`.
- `_tokens.scss`: CSS custom properties on `:root` — `--af-color-{bg,surface,text,muted,primary,on-primary,border}`, `--af-font-{latin,arabic}`, `--af-space-{1..8}` (4 px steps), `--af-radius-{sm,md,lg}`, `--af-text-{sm,md,lg,xl}`; neutral greys plus one placeholder primary. Components use only these variables. `:lang(ar)` uses `--af-font-arabic` (Noto Sans Arabic), otherwise `--af-font-latin` (Noto Sans), both via `@fontsource`.

- [ ] **Step 1: Failing tests:** `set('en')` → `document.documentElement.dir === 'ltr'` and `lang === 'en'`; default with no storage and `navigator.language = 'fr'` → `ar`/`rtl`; `localStorage.setItem` throwing → `set()` still works; shell renders the toggle and clicking it flips `dir`.
- [ ] **Step 2–4:** FAIL → implement → PASS (`npm test -- --watch=false`).
- [ ] **Step 5:** Commit `feat(web): bilingual Angular shell and design tokens (FR-021, FR-022, FR-024)`.

### Task 14: Frontend guards — logical CSS, translation keys, generated client

**Files:** Create `frontend/.stylelintrc.json`, `frontend/scripts/check-i18n-keys.mjs`, `frontend/ng-openapi-gen.json`, `frontend/src/app/api/` (generated, committed); Modify `frontend/package.json` scripts.

**Interfaces:**
- `npm run lint` = `ng lint` + `stylelint "src/**/*.scss"` with `plugin/use-logical: "always"` (flags `left/right/margin-left/padding-right/text-align: left/float: left/border-left…`).
- `npm run i18n:check` exits 1 listing keys present in one of `src/assets/i18n/{ar,en}.json` but not the other (nested keys flattened with `.`), or empty values.
- `npm run api:generate` regenerates `src/app/api/` from `../contracts/openapi.yaml`; `npm run api:check` regenerates into a temp dir and fails if it differs from the committed client.

- [ ] **Step 1:** Add a temporary `margin-left: 4px` and confirm `npm run lint` fails; remove it.
- [ ] **Step 2:** Add a key to `en.json` only and confirm `npm run i18n:check` fails listing it; remove it.
- [ ] **Step 3:** Generate the client; change `contracts/openapi.yaml` locally without regenerating and confirm `npm run api:check` fails; revert.
- [ ] **Step 4:** Home page calls the generated `MetaService` and shows `default_language` (proves the client works through the proxy). Unit test with `HttpTestingController`.
- [ ] **Step 5:** Commit `feat(web): logical-CSS lint, translation-key check, generated API client (FR-015, FR-022, FR-023)`.

### Task 15: RTL/LTR layout check

**Files:** Create `frontend/e2e/shell-direction.spec.ts`, `frontend/playwright.config.ts`

**Interfaces:** `npm run e2e` runs Playwright (Chromium) against `ng serve` with API calls stubbed by `page.route`.

- [ ] **Step 1: Failing test** for each width in `[360, 768, 1440]` and each language:
  - `html[dir]` matches the language;
  - the app name's box is at the inline start (`x + width/2 > viewport/2` in Arabic, `< viewport/2` in English) and the toggle at the inline end;
  - `document.documentElement.scrollWidth <= viewport width` (no horizontal overflow);
  - a full-page screenshot is saved to `test-results/` as CI evidence (SC-005).
- [ ] **Step 2–4:** FAIL (before the shell has the layout) → adjust shell SCSS (flex with `justify-content: space-between`, logical properties only) → PASS.
- [ ] **Step 5:** Commit `test(web): RTL/LTR layout check at 3 widths (SC-005)`.

## Part C — Environment, CI, release, repository

### Task 16: One-command local stack

**Files:** Modify `deploy/docker-compose.yml`, `deploy/.env.example`, `README.md`; Create `frontend/Dockerfile`, `frontend/nginx.conf`, `backend/scripts/entrypoint-migrate.sh`; Modify `backend/Dockerfile` (uv, non-root, `HEALTHCHECK`)

**Interfaces:** Services and order:
`db` (pgvector/pgvector:pg16, healthcheck) → `migrate` (backend image, runs `db_bootstrap.py` with the admin URL then `alembic upgrade head` with the owner URL, `restart: "no"`) →
`api` (`depends_on: migrate: condition: service_completed_successfully`, connects as `af_app`), `worker`, `beat` (same image, different commands, worker healthcheck = Task 11 command), `redis`, `web` (nginx serving the built Angular app, proxying `/api` and `/health` to `api`). `ollama` stays under profile `ai`. Every service has a memory limit (`mem_limit`) so the optional model cannot starve PostgreSQL.
The one command: `docker compose -f deploy/docker-compose.yml --env-file deploy/.env up -d --build`.

- [ ] **Step 1:** From a clean clone on Windows: copy `.env.example` → `.env`, run the command, then `curl http://localhost:8000/health/ready` → 200 and open `http://localhost:8080` → shell in Arabic. Record the elapsed time.
- [ ] **Step 2:** `docker compose ... ps` shows `api`, `worker`, `beat`, `web`, `db`, `redis` healthy and `migrate` exited 0.
- [ ] **Step 3:** README "Quick start" documents exactly these steps plus `npm start` for frontend hot reload and `uv run uvicorn app.main:app --reload` for backend.
- [ ] **Step 4:** Commit `feat(deploy): one-command local stack (FR-025, SC-001)`.

### Task 17: Complete the CI gate

**Files:** Modify `.github/workflows/ci.yml`

**Interfaces — jobs (all on `pull_request` and `push` to `main`):**
- `backend`: ruff check, ruff format check, mypy, lint-imports, `pytest -m unit`, `pytest -m integration` (services: pgvector, redis; bootstrap + migrations run first), contract test.
- `migrations`: fresh DB → bootstrap → `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head` → `alembic check` (no model drift). If a `v*` tag exists, a second step checks out the latest tag, migrates to its head, then checks out the PR and runs `upgrade head` (FR-010; skipped with a notice until the first release tag).
- `frontend`: `npm ci`, `npm run lint`, `npm run i18n:check`, `npm run api:check`, `npm test -- --watch=false`, `npm run build`. Remove the "detect Angular" step.
- `e2e`: Playwright Chromium, uploads `test-results/` as an artifact.
- `licences`: `pip-licenses --allow-only="<allow-list>"` on the backend env; `license-checker-rseidelsohn --production --onlyAllow "<allow-list>"` on the frontend.
- `compose`, `secrets`: unchanged.
- Run `github-actions-hardening` skill review on the final workflow; all third-party actions pinned to a commit SHA with the version in a comment.

- [ ] **Step 1:** Push the branch; all jobs green. Record durations: backend-only path < 8 min, whole run < 12 min (SC-002). If over, add `paths` filters and uv/npm caching before going on.
- [ ] **Step 2:** Commit `ci: full merge gate (FR-026, SC-002)`.

### Task 18: Release images

**Files:** Create `.github/workflows/release.yml`; Modify `.github/workflows/deploy.yml` comment to point to it.

**Interfaces:** On tag `v*.*.*`: build and push `ghcr.io/mohamedsayed17/agent-factory-backend:<version>` and `…-web:<version>` (plus `:sha-<short>`), with `permissions: packages: write, contents: read`, OCI labels (source, revision, licence AGPL-3.0), and build provenance attestation.

- [ ] **Step 1:** Push tag `v0.1.0-rc.1` on the branch after merge; both images appear in GHCR and `docker run --rm ghcr.io/…-backend:0.1.0-rc.1 python -c "import app"` exits 0.
- [ ] **Step 2:** Commit `ci: release images to GHCR (FR-028)`.

### Task 19: Repository governance

**Files:** Modify `frontend/README.md`, `backend/README.md`, `specs/README.md`; repository settings via `gh`.

- [ ] **Step 1 (FR-001):** Every top-level folder has a README; `.claude/` and `.github/` are described in the root README.
- [ ] **Step 2 (FR-030):** Create project "agent-factory delivery" with `gh project create`; set the Status field options to Backlog, Spec in review, Ready, In progress, In review, Done (GraphQL `updateProjectV2Field`); link the repository; add issues for specs 001–002 and tasks T1–T20.
- [ ] **Step 3 (FR-027):** Repository settings: squash merge only, delete branch on merge. Branch protection (repository public per ADR-0006): require PR, 1 approval from CODEOWNERS, status checks `backend, migrations, frontend, e2e, licences, compose, secrets`, no force push, include administrators.
- [ ] **Step 4 (FR-029):** Already satisfied on `main` (templates and PR template); verify only.
- [ ] **Step 5:** Commit `docs: folder READMEs and governance (FR-001, FR-029, FR-030)`.

### Task 20: Prove the success criteria

**Files:** Create `docs/reviews/2026-xx-xx-spec-001-verification.md`

- [ ] **Step 1 (SC-003):** On a throwaway branch, open one draft PR with six commits, each reverting the previous one's break: lint error, cross-module import, contract drift, missing translation key, fake secret (`AKIA` test key), a migration that runs DDL as `af_app`. Record that CI failed for each (6/6), then close the PR and delete the branch.
- [ ] **Step 2 (SC-001):** Two team members on Windows and one on Linux/macOS time the quick start from clone; record times (target < 10 min).
- [ ] **Step 3 (SC-002, SC-004, SC-005, SC-006):** Link the CI runs, test names and Playwright screenshots that prove them.
- [ ] **Step 4:** Update spec 001 status to **Done** in `specs/README.md`; commit `docs: spec 001 verification`.

## Open items for the tech lead / owner
1. ~~FR-027 branch protection blocked by the GitHub plan.~~ Resolved by ADR-0006 (repository public, 2026-11-09).
2. Worker health via CLI instead of HTTP (Decision 12): accepted with the plan, 2026-11-09.
3. Two images instead of three (Decision 11): accepted with the plan, 2026-11-09.
