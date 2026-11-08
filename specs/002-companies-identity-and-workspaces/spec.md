# Spec 002 — Companies, identity and workspaces

**Status:** Ready for approval (clarifications resolved 2026-11-08) · **Release:** R1, sprint 1–2 · **Owner:** tech lead
**Depends on:** spec 001, ADR-0003 (built-in auth), ADR-0004 (workspace model)
**Blocks:** every spec that stores customer data (003 onward)

## Why
The platform holds many companies' data on one server. If one company can ever see another's
data, the product is finished. This spec defines who the users are, how they sign in, how they
belong to companies and workspaces, what each role may do, and how the database itself enforces
isolation, so that every later spec inherits isolation instead of re-implementing it.

## Concepts
- **Company:** a customer organisation (tenant). Owns all its data.
- **Workspace:** an isolated area inside a company, such as *HR* or *Support* (ADR-0004). Data,
  agents, sources and gaps belong to exactly one workspace. A company has at least one workspace.
- **User:** one person with one login (email). A user can belong to several companies and to
  several workspaces in each, with a role in each.
- **Membership:** the link between a user and a company (company role) or a workspace (workspace role).
- **Platform operator:** our own staff who run the hosted service. Not a member of any company.
- **Visitor:** an anonymous person using a public website widget. Not a user; handled in spec 035.

## Roles (initial)
| Level | Role | Can |
|---|---|---|
| Company | **Owner** | Everything in the company, including deleting it and transferring ownership. At least one per company. |
| Company | **Admin** | Manage company settings, members and workspaces; cannot delete the company or remove the last owner. |
| Company | **Member** | Belongs to the company; sees only workspaces they are a member of. |
| Workspace | **Workspace admin** | Manage that workspace's members and settings. |
| Workspace | **Editor** | Create and change sources, mappings and agents in that workspace (later specs). |
| Workspace | **Viewer** | Read-only access and chat in that workspace. |

Company owners and admins have implicit workspace-admin rights in every workspace of their company.
Later specs may add permissions to roles but not new roles without amending this spec.

## User stories

**US-1 — Create a company (P1).** As a new customer, I create an account and a company, and I
become its owner with a first workspace, so I can start.
- *Given* a valid email and password, *when* I sign up and verify my email, *then* I own a new
  company with one workspace named by me, and I land in that workspace.

**US-2 — Sign in and out (P1).** As a user, I sign in with email and password and stay signed in
across page reloads until I sign out or my session expires.
- *Given* wrong credentials, *when* I sign in, *then* I see one generic message that does not
  reveal whether the email exists.
- *Given* 5 failed attempts for one account within 15 minutes, *then* further attempts for that
  account are delayed and the event is audited.

**US-3 — Invite people (P1).** As a company admin, I invite a person by email to the company and
to chosen workspaces with a role, and they join by accepting the invitation.
- *Given* an invitation older than 7 days, *when* it is opened, *then* it is refused and the admin
  can resend it.
- *Given* the invitee already has an account, *when* they accept, *then* the company is added to
  their existing login; no second account is created.

**US-4 — Switch company and workspace (P1).** As a user in several companies or workspaces, I
switch between them, and every screen and API call afterwards shows only the selected one's data.

**US-5 — Isolation holds even if code is wrong (P1).** As the owner of the platform, I know that a
bug in application code that forgets a filter still cannot return another company's or another
workspace's rows, because the database refuses.
- *Given* a request in company A's context, *when* the application queries any tenant table with
  no filter, *then* only company A's rows (and only workspaces the user may see) are returned.

**US-6 — Manage members (P1).** As a company admin, I change a member's roles or remove them; the
change takes effect on their next request, and it is audited.
- *Given* I try to remove or demote the last owner, *then* the action is refused.

**US-7 — Reset my password (P1).** As a user who forgot my password, I reset it through a link
sent to my email; all my other sessions are then signed out.

**US-8 — Two-step sign-in (P1).** As a company owner or admin, I must protect my account with an authenticator
app code in addition to my password (mandatory for owners and admins, FR-007).

**US-9 — Use the platform in my language (P2).** As a user, my chosen language (Arabic or English)
is remembered and used for the interface, emails and error messages.

**US-10 — See who did what (P2).** As a company owner, I see an audit list of sign-ins, invitations,
role changes and removals in my company.

**US-11 — Leave or delete (P3).** As a user I leave a company; as an owner I delete a company,
which removes access immediately and schedules its data for deletion after a 30-day grace period.

## Functional requirements

### Identity and sessions (ADR-0003)
- **FR-001** Users sign in with email and password. Emails are compared case-insensitively and
  are unique across the platform.
- **FR-002** Passwords are stored only as a salted, memory-hard hash (Argon2id). Minimum length
  10; passwords found in a known-breached list are refused.
- **FR-003** Sessions are server-side and revocable. The browser holds only an opaque session
  token in an `HttpOnly`, `Secure`, `SameSite` cookie; state-changing requests are protected
  against cross-site request forgery.
- **FR-004** Idle session timeout 8 hours, absolute timeout 7 days. Signing out, password change,
  password reset and removal from all companies revoke the affected sessions.
- **FR-005** Email verification is required before a user can create or join a company.
- **FR-006** Sign-in, sign-up, password reset and invitation-accept endpoints are rate limited per
  account and per IP address.
- **FR-007** TOTP two-step sign-in (US-8) with one-time recovery codes. It is **mandatory for
  company owners and admins**: a user who holds either role must set it up before they can use
  the company, and cannot remove it while they hold the role. It is optional for other users.
  *(Decided by owner 2026-11-08.)*
- **FR-008** The identity design keeps a place for external sign-in (OIDC/SSO for the Enterprise
  plan, R4) without changing the user or membership model.

### Companies, workspaces and memberships (ADR-0004)
- **FR-009** A company has a name (Arabic and/or English), a default language, a unique URL slug,
  a status (active, suspended, pending deletion) and at least one owner and one workspace.
- **FR-010** A workspace belongs to one company, has a name and a slug unique within the company,
  and can be archived. Archived workspaces are read-only.
- **FR-011** Memberships record user, company or workspace, role, who granted it and when.
- **FR-012** Roles and permissions follow the table above. Permission checks happen in one place in
  the gateway layer, from a single permission map, not scattered through endpoints.
- **FR-013** Invitations carry company, workspaces, roles, inviter, expiry (7 days) and are
  single-use. An invitation link reveals nothing about the company before the invitee signs in or
  signs up with the invited email.
- **FR-014** Sign-up mode is configurable per deployment: *open* (anyone may create a company) or
  *invite-only* (only platform operators create companies). The hosted service runs
  **invite-only during the pilot**. *(Decided by owner 2026-11-08.)*

### Database isolation (constitution Article III)
- **FR-015** Every company-owned table has `company_id`; every workspace-owned table also has
  `workspace_id`. Both are non-null and enforced by foreign keys.
- **FR-016** Global tables and why they are global: `users` (one login across companies);
  `user_sessions`, `password_resets`, `email_verifications` and `user_mfa` (belong to a login,
  not a company); `platform_operators`. These are not readable through tenant endpoints except a
  user's own rows.
- **FR-017** Every company- or workspace-owned table has row-level security forced on. Policies
  admit a row only when its `company_id` matches the transaction's tenant context and, for
  workspace-owned tables, its `workspace_id` is in the set of workspaces the current user may
  access.
- **FR-018** Tenant context (user, company, allowed workspaces) is set at the start of each
  transaction from the authenticated session, and cleared at its end. With no context set, tenant
  tables return no rows and refuse writes.
- **FR-019** A write that sets a `company_id` or `workspace_id` different from the current context
  is refused by the database, not only by the application.
- **FR-020** Background jobs run with an explicit tenant context passed with the job; a job with no
  context cannot read tenant tables.
- **FR-021** Platform operators have **no access to customer data in R1**. They can create,
  suspend and delete companies and see platform audit events, but cannot read any company- or
  workspace-owned rows. An owner-granted, time-limited support access may be specified in a later
  release. *(Decided by owner 2026-11-08.)*

### Audit
- **FR-022** Audit events are written for: sign-up, sign-in success and failure, sign-out,
  password change and reset, two-step setup and removal, invitation sent/accepted/revoked,
  membership and role changes, workspace create/archive, company create/suspend/delete, and any
  denied cross-tenant access attempt.
- **FR-023** Audit events are append-only for the app role and carry actor, action, target, time,
  IP address and request id; they never contain passwords or tokens. Events tied to a company carry
  its `company_id` and are covered by row-level security. Events with no company (for example a
  failed sign-in for an unknown email) are platform events, visible only to platform operators.
- **FR-024** Owners and admins can list and filter their company's audit events (US-10).

### Email and language
- **FR-025** Verification, invitation and password-reset emails are sent in the recipient's
  language (Arabic or English), right-to-left for Arabic.
- **FR-026** Outgoing email goes through one email-sending interface so the provider can change
  without touching features. Locally and in CI, emails are captured, not sent.

### Lifecycle
- **FR-027** Suspending a company blocks all its sessions and API access immediately; data is kept.
- **FR-028** Deleting a company blocks access immediately and permanently erases its data after
  30 days unless restored by an owner within that window.
- **FR-029** A user can export their own profile data and delete their own login; deleting the
  login is refused while they are the last owner of any company.

## Out of scope
- Plans, licences and limits (R2 billing). The `licenses` table from HANDOFF §9 is created by the
  billing spec.
- SSO / OIDC sign-in (R4), social sign-in.
- Widget visitors and customer-facing identities (spec 035).
- Per-record or per-field permissions inside a workspace (tool gateway, spec 009).
- API keys for machine access (spec 013 or later).

## Success criteria
- **SC-001** Cross-tenant leak test suite: for every tenant table, reads, updates and deletes from
  company A's context touch 0 rows of company B; workspace-scoped reads from a viewer of workspace
  W1 touch 0 rows of W2. Runs in CI on every PR and must pass 100%.
- **SC-002** A deliberately unfiltered query in application code (test fixture) returns only the
  current tenant's rows.
- **SC-003** With no tenant context set, every tenant table returns 0 rows.
- **SC-004** Sign-in completes in under 500 ms at p95 on the reference server, excluding the
  deliberate password-hash cost.
- **SC-005** A role change or removal takes effect on the member's next request (no stale access
  after the change is saved).
- **SC-006** A new customer goes from sign-up to their first workspace in under 3 minutes in a
  usability test with 5 people, in Arabic and in English.
- **SC-007** An external security review of the sign-in, session and isolation design finds no
  high or critical issue before the pilot (week 12).

## Key entities
`users`, `user_sessions`, `password_resets`, `email_verifications`, `user_mfa` (global, per login);
`platform_operators` (global);
`companies`, `company_members`, `invitations`, `audit_events` (company-owned);
`workspaces`, `workspace_members` (company-owned; workspace rows scoped by `workspace_id`).

## Assumptions
- One login per email across the platform (ADR-0004).
- An email provider will be chosen in `plan.md`; until then, emails are captured locally.
- Arabic is the default language for new companies and users unless the browser asks for English.

## Open questions
None. FR-007, FR-014 and FR-021 were answered by the owner on 2026-11-08.
