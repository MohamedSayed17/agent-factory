# ADR-0003 — Built-in authentication in the FastAPI backend

**Status:** Accepted · **Date:** 2026-11-08 · **Deciders:** product owner

## Context
Spec 002 needs sign-in for company staff. Options were a self-hosted identity server (Keycloak),
built-in authentication, or a managed service (Auth0/Clerk).

## Decision
Authentication is built into the backend: email and password with Argon2id hashing, server-side
revocable sessions held in an HttpOnly cookie, email verification, password reset, optional TOTP
two-step sign-in, rate limiting and audit.

## Consequences
- No extra service to run; fits a single server and self-hosted editions.
- We own the security of sign-in, reset and two-step flows. Spec 002 SC-007 requires an external
  review before the pilot, and the implementation must use maintained libraries for hashing and
  TOTP rather than hand-written cryptography.
- Enterprise SSO (R4) needs OIDC sign-in added later; spec 002 FR-008 keeps the model ready for it.

## Options considered
- Keycloak — complete features and SSO, but another stateful service (~1 GB RAM) to run and theme.
- Managed service — fastest start, but a paid outside dependency, data held abroad, and harder
  self-hosting.
