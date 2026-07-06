# SMRITI Retail OS — Remediation Brief for an AI Coding Agent

Give this whole file to Claude Code (or another coding agent) **run from inside
your actual repo, with a working `bench` and a disposable staging site** —
none of this should be run against production first. The agent needs a live
Frappe+MariaDB environment for phases 2–4; phase 1 is safe anywhere.

Do the phases **in order**. Each has a "Definition of Done" the agent must
satisfy before moving on — don't let it mark something done just because it
edited files.

---

## Phase 0 — Baseline (5 min)

Prompt:
> Before changing anything, run the full test suite (`bench --site <site>
> run-tests --app smriti_retail_os`) and save the output to
> `baseline_test_results.txt`. Also run `python sdc/discovery.py` and
> `python smriti_architecture_guard.py` and save their output. Commit nothing
> yet — this is just so we can prove what got better vs. worse.

**Done when:** three baseline log files exist and are committed to a
throwaway branch.

---

## Phase 1 — Safe, static fixes (no live bench needed)

These are already drafted for you — attached: `check_ignore_permissions.py`
(put in `tools/audit/`), `ci_additions.yml` (merge into
`.github/workflows/smriti_ci.yml`), the corrected `NOTICE`, and the corrected
`TECHNICAL_DEBT_REPORT.md` §2.2.

Prompt:
> Apply the attached NOTICE and TECHNICAL_DEBT_REPORT.md fixes verbatim.
> Add tools/audit/check_ignore_permissions.py and merge ci_additions.yml
> into .github/workflows/smriti_ci.yml as new jobs. Run
> `python3 tools/audit/check_ignore_permissions.py` and paste the output —
> don't fix the 92 flagged call sites yet, just confirm the gate runs and
> correctly lists them.

**Done when:** the gate script runs and lists ~92 unreviewed call sites; CI
YAML is valid (`actionlint` or a YAML linter passes on it).

---

## Phase 2 — Permission audit (needs a staging bench + real roles set up)

This is the highest-value, highest-risk item. Go function-by-function, not in
bulk — a bulk regex "fix" here is how you break checkout.

Attached: `ignore_permissions_RISK_REVIEW.csv` — the 92 whitelisted functions
that actually bypass permissions (already filtered out of the noisy 1,070;
tests and non-endpoint helpers are excluded).

Prompt (repeat per file, e.g. `billing_api.py`, then `security_api.py`, etc.
— don't hand the agent the whole CSV at once, it'll rush):
> Open billing_api.py. For each function listed in
> ignore_permissions_RISK_REVIEW.csv for this file, do the following:
> 1. Explain in one sentence why permissions are bypassed here (e.g. "writes
>    a document type the calling user legitimately can't access directly,
>    like a ledger entry created as a side-effect of billing").
> 2. Decide: is the bypass necessary, or can it be replaced with an explicit
>    role check (`frappe.has_permission(...)` or a role decorator) instead?
> 3. If necessary: add the `# reviewed-ignore-permissions: <one-line reason>`
>    comment directly above the call so the Phase-1 CI gate passes.
> 4. If NOT necessary: remove ignore_permissions=True and add the narrower
>    permission check instead.
> 5. Run the existing tests for this file
>    (`bench --site <site> run-tests --module smriti_retail_os.tests.test_billing_api`)
>    after each change, not at the end. If a test breaks, stop and report —
>    don't loosen the test to make it pass.
> Do not touch other files in this pass.

**Done when:** all 92 sites are either tagged with a reason or tightened, the
Phase-1 CI gate goes green, and per-file tests still pass. Expect this phase
to take real back-and-forth — treat any "all done, no issues found" response
from the agent on the first try as a signal to push back and ask it to show
its reasoning per function.

---

## Phase 3 — Wire real tests into CI (needs your actual CI infra)

Prompt:
> The smriti-integration-tests job in ci_additions.yml needs a self-hosted
> runner with a working bench. Set that up (or point me at docs for your
> infra), then run the job once manually and fix whatever it reveals —
> starting with the pre-existing failures already logged in KNOWN_ISSUES.md
> (KI-001, KI-002, KI-006, KI-007). For each: find the actual test-isolation
> bug (shared state between tests, not a code bug), fix the setUp/tearDown,
> and update KNOWN_ISSUES.md to mark it resolved with the commit reference.

**Done when:** the integration test job runs green on a real PR, and
KNOWN_ISSUES.md reflects reality (no more "pre-existing, fix target: v2.0.1"
items sitting open for two major versions).

---

## Phase 4 — Schema migration off setup.py (biggest, do last, do slowly)

This is the largest and riskiest item — don't let an agent attempt this in
one shot. Do it doctype-by-doctype, on a disposable site, with a rollback
plan for each.

Prompt (one doctype at a time):
> Take the "SMRITI Benefit Ledger" doctype currently defined in setup.py.
> Generate the equivalent standard Frappe JSON doctype definition
> (smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_ledger/
> smriti_benefit_ledger.json) matching the fields, types, and options exactly.
> Write a Frappe patch that: (a) checks if the JSON doctype already exists
> from a prior setup.py run, (b) does nothing destructive to existing data,
> (c) removes the setup.py registration for this doctype only. Run
> `bench --site <staging-site> migrate` on a COPY of staging data, not prod,
> and confirm no fields were dropped by comparing `desc tabSMRITI Benefit
> Ledger` before and after. Report field-by-field diff.

**Done when:** one doctype's schema now lives in JSON, migrates cleanly on a
copy of real data with zero field loss, and existing reads/writes against it
(via the repository layer) still pass their tests. Repeat per doctype — do
not batch multiple doctypes per migration until you've proven the pattern
works once.

---

## Guardrails to give the agent up front, every phase

- Never run anything against a production site or database.
- Never widen a test to make it pass; if a fix breaks a test, the fix (or
  the test's original assumption) is wrong — investigate, don't paper over.
- Commit in small, reviewable diffs per function/file/doctype, not one giant
  commit per phase.
- If asked to touch `billing_api.py`, `psv_ledger_service.py`, or anything
  under `services/udne`, require a full test run before AND after — these
  touch money and inventory ledgers.
- Update the relevant .md file (KNOWN_ISSUES.md, TECHNICAL_DEBT_REPORT.md,
  QUALITY_DASHBOARD.md) in the same commit as the fix, so docs don't drift
  from code again the way the PIN fix did.

---

## Files referenced in this brief (attach alongside it)

- `ignore_permissions_RISK_REVIEW.csv` — the 92 real call sites to review
- `ignore_permissions_audit.csv` — full 1,070-row raw audit (for reference)
- `check_ignore_permissions.py` — CI gate script
- `ci_additions.yml` — CI job drafts
- `NOTICE`, `TECHNICAL_DEBT_REPORT.md` — corrected versions
