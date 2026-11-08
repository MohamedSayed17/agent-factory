## Spec
<!-- specs/NNN-name and the FR/US/SC ids this PR implements, e.g. FR-003, SC-001 -->

## Type
- [ ] Spec PR (spec.md / plan.md / tasks.md / ADR only)
- [ ] Implementation PR (the spec's status is **Approved**)

## How it was tested

## Checklist
- [ ] Contract (`contracts/`) updated first if API behaviour changed
- [ ] New tenant tables have `company_id` (+ `workspace_id`), FORCE RLS and leak tests
- [ ] User-facing text in Arabic and English; RTL checked
- [ ] No secrets, dumps or real customer data
