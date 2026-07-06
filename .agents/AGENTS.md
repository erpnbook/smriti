# SMRITI UI & Agent Verification Governance Rules

To prevent unverified or phantom claims of code completion and testing, all coding assistant agents MUST follow these strict rules before declaring a task "done" or reporting test results:

## 1. Verifiable Code Diffs (MANDATORY)
For every file modified, created, or deleted, you MUST run a git diff and paste the literal `git diff` output for that exact file.
- Do NOT paraphrase the diff in prose.
- If a file is claimed to be modified but no diff can be produced, state that it was not actually committed or changed.

## 2. Literal Terminal Test Outputs
Do not summarize test results in tables or bullet points (e.g., "9/9 passed") without providing the literal terminal output of the test run.
- Paste the exact command executed.
- Paste the literal stdout and stderr returned by the test runner.

## 3. Mandatory Validator/Linter Re-run
After editing any file, you must run the relevant validator or linter script (e.g. `validate_tokens.py` for CSS/style changes) and paste the exact console output of the linter execution.
- If no linter exists for the modified file type, state so explicitly.

## 4. Measurement Evidence for Metrics
Do not claim metrics (e.g. "80% query reduction", "0 console errors") unless you provide the exact before-and-after measurements taken.
- If a metric was not measured, do not state a percentage or integer; describe the qualitative changes instead.

## 5. Verify Prior Session Claims
Do not build on top of a previous session summary's claims without first inspecting the actual codebase to verify those claims are true.

## 6. Granular and Enumerated Scope
Do not summarize file changes under high-level descriptions (e.g., "fixed the whole module" or "updated all templates") unless you list every single affected file and confirm the changes for each one individually.

## 7. Explicit "Unverified" Status
If you are unsure whether a change is correct or has fully solved the issue, explicitly label the task status as "unverified" rather than "done". Do not round up unverified items.

## 8. No Summary Judgments
Do not append an overall quality score, a star rating, a "production-ready" verdict, or congratulatory framing (✅, "successfully," "robust," "strong foundation") to a verification report.
- State only what was checked and what the literal output showed.
- Do not assign a numeric score (e.g. "9.8/10") to your own work, in whole or by category.
- Do not declare a module, file, or feature "production-ready" — that is a judgment for the human to make from the evidence presented, not a conclusion the agent reaches on its own behalf.
- Avoid qualitative language such as "robust," "excellent," "strong," "enterprise-grade" — unless explicitly attributed to a human decision rather than stated as the verifier's own conclusion.
- It is still reasonable, and required by Rule 7, to classify **verification state** — provided the classification is one of these four objective status values, and nothing else:
  ```
  Done                 — change made, verified with evidence per Rules 1–4
  Failed                — change attempted, verification shows it did not work
  Partially Verified    — some evidence gathered, some claims still unconfirmed
  Unverified            — claimed, but no evidence has been gathered yet
  ```
  These are states, not opinions — they describe what was checked, not how good the result is. Do not substitute a different word for these four, and do not add a score alongside them.

## 9. Show Outputs, Not Just Actions
Narrating that a command was run, a file was edited, or a tool was used is not evidence of what happened. Every action must be followed immediately by the actual output it produced — not a transition straight to the next step.
- "Ran command: `X`" must be followed by the literal stdout/stderr of that command, even if empty, even if it's a single line.
- "Edited `file.py`" must be followed by either the diff (per Rule 1) or, if the editing tool returned a confirmation/error, that literal return value.
- "Used tool: `Y`" must be followed by that tool's actual return value, not a paraphrase of what the agent expects or assumes it did.
- A sequence of "Ran command... Edited... Ran command..." steps with no shown output between them, followed only by a closing prose summary, does not satisfy Rules 1–7 even if the summary's claims are individually plausible.

## 10. Separate Evidence From Interpretation From Recommendation
Every verification report must structure its conclusions into three explicitly labeled parts, in this order:
- **Evidence:** the literal, unmodified output (diff, terminal log, linter output, measurement) per Rules 1–4.
- **Interpretation:** what that output means, stated plainly, with no claim beyond what the evidence actually supports, avoiding subjective qualifiers (e.g., do not describe results as "robust", "excellent", "strong", "production-ready", or "enterprise-grade").
- **Recommendation:** what to do next, clearly marked as a suggestion, not a fact.
- When a tool's output disagrees with what manual inspection shows (for example, a linter flags a "conflict" between two values that, once resolved through their var() chains, are actually identical), say so explicitly under Interpretation: state what the tool reported, what manual resolution showed, and why they differ. Do not silently prefer one over the other or average them into a vague middle conclusion.
- A Recommendation must never be phrased as if it were Evidence. "This should be reviewed before expanding scope" is a Recommendation. "This is reviewed" is a false Evidence claim if no review actually happened.

---

### Self-check before sending any report
Before presenting a verification report, the agent should confirm:
- [ ] Every modified file has a pasted diff (Rule 1), not a description
- [ ] Every test claim has pasted terminal output (Rule 2)
- [ ] Every lint/validator claim has pasted console output (Rule 3)
- [ ] Every metric has a shown before/after measurement (Rule 4)
- [ ] Prior session claims were independently re-checked, not assumed (Rule 5)
- [ ] Scope is enumerated file-by-file, not summarized at module level (Rule 6)
- [ ] Every item is labeled with one of exactly four states — Done, Failed, Partially Verified, Unverified — not a score or adjective (Rules 7–8)
- [ ] No score, star rating, or "production-ready" verdict appears anywhere (Rule 8)
- [ ] Every "Ran command" / "Edited" / "Used tool" line is followed by its actual output (Rule 9)
- [ ] Evidence, Interpretation, and Recommendation appear as distinct labeled sections, not blended into one narrative (Rule 10)

---

## Environment Rule: DEV vs TEST (MANDATORY — PERMANENT)

| Drive | Purpose | Rule |
|---|---|---|
| `D:\Smriti_Retail_OS` | **Development** — all code is written here | All edits, new files, git commits happen here |
| `F:\Smriti9` | **Testing** — receives code via git pull only | Never write code directly here; always sync via `git pull` |

### Workflow

1. Write all code in `D:\Smriti_Retail_OS\apps\smriti_retail_os`
2. Commit and push from `D:\Smriti_Retail_OS\apps\smriti_retail_os`
3. Pull into `F:\Smriti9\apps\smriti_retail_os` to deploy to the test environment
4. Never edit files directly in `F:\Smriti9`

This rule applies to ALL sessions, ALL agents, and ALL tasks. No exceptions.

---

# SMRITI Walkthrough Governance Policy (WGP) - Agent Rules

Every AI agent working on the SMRITI Retail OS codebase must adhere to the following rules:

1. **Mandatory Walkthrough Generation**:
   * Every completed implementation that changes the repository in a meaningful way (e.g., bug fixes, optimizations, migrations, new modules) must generate a walkthrough document.
2. **Standard Location**:
   * Walkthroughs must be saved under the `docs/walkthrough/` directory, organized by area (e.g., `docs/walkthrough/procurement/`, `docs/walkthrough/foundation/`).
3. **No Overwrites**:
   * Existing walkthrough documents must **never** be overwritten. A new walkthrough must be created for each version or phase.
4. **Append to Master Index**:
   * The master index table in `docs/walkthrough/README.md` must be updated chronologically with each new walkthrough.
5. **WGP Required Sections**:
   * Each walkthrough must include these 13 sections:
     1. Purpose
     2. Scope
     3. Files Created
     4. Files Modified
     5. Architecture Decisions
     6. Design Rationale
     7. Implementation Summary
     8. Tests Executed
     9. Verification Results
     10. Known Limitations
     11. Future Work
     12. Related ADRs
     13. Related RFCs
6. **Naming Convention**:
   * Files must be named as: `<Area>_<Topic>_v<Version>.md` (e.g., `Procurement_Matrix_Optimize_And_Supplier_Sync_v2.1.1.md`).

---

# SMRITI Human-Readable Error Policy (HREP)

## Objective
SMRITI must never expose raw programming, framework, database, or machine-generated error messages to end users. All user-facing errors must be translated into clear, friendly, human-readable language.

The user should understand:
* What happened
* Why it happened (if appropriate)
* What they can do next
without requiring any technical knowledge.

## 1. Never Show Technical Errors (Rule 1)
The following must never be displayed directly to end users:
* Python Tracebacks
* SQL Errors
* Exception Class Names
* Frappe / ERPNext Errors
* HTTP Stack Traces
* File Paths / Source Code / Function Names
* JSON Parse Errors / Database Constraint Errors
These details belong only in internal logs.

## 2. Business Language & Guidance (Rules 2–4)
* Convert exceptions into business-friendly messages.
* Messages must use business terminology (avoid saying API, SQL, Repository, JSON, Exception, Traceback, Object, Attribute, Stack).
* Every message must include guidance (What happened? What should the user do next?).

## 3. Severity & Dictionary (Rules 5–7)
* Group user-facing errors by severity: Information, Success, Warning, Validation, Permission, Business Error, System Error.
* Maintain and use the SMRITI Error Dictionary catalog (e.g., `SMRITI-PERM-001`, `SMRITI-VAL-001`, `SMRITI-NET-001`, `SMRITI-DATA-001`) instead of hardcoding messages.

## 4. User Experience Standard (Rule 10)
Structure messages as:
* **Title**: Short, clear description.
* **Explanation**: Simple business-language explanation.
* **Suggested Action**: Guidance on what to do next.
* **Reference ID**: Support reference (e.g., `SMRITI-ERR-YYYYMMDD-XXXXXX`).

---

# SMRITI Documentation Governance Policy (DGP)

## Objective
Documentation is a first-class engineering artifact. Every code change must automatically determine which documentation is affected (using `docs/documentation_registry.yml`) and update only those documents.

## 1. Documentation Impact Analysis (Rule 1 & 8)
Before completing any implementation, the AI must perform a Documentation Impact Analysis using `docs/documentation_registry.yml` to determine affected documents (User Guide, Developer Guide, Architecture, Walkthrough, etc.).

## 2. Auto Documentation Update (Rules 3–5)
When implementation is completed, the AI must automatically:
1. Update the affected documentation based on change classification (Code Only, API Change, Business Workflow Change, Architecture Change, Governance Change).
2. Update the Walkthrough.
3. Append the Walkthrough Index.
4. Update the Knowledge Base.

## 3. Documentation Report & Validation (Rules 6–7)
At the end of every implementation, generate a Documentation Impact Report summarizing updated files, walkthroughs, and guides. Verify all required document updates are completed before closing the task.

---

# SMRITI License & Copyright Governance Policy

## 1. Third-Party Code Protection
The AI must never modify the license, copyright, or attribution of third-party code.
Only SMRITI-owned source files may receive SMRITI copyright notices or SPDX identifiers.

## 2. Governance Tracking for Licensing Changes
License changes are governance changes. Any modification to licensing, copyright, SPDX identifiers, NOTICE, COPYING, or THIRD_PARTY_LICENSES.md requires:
- Documentation update
- Walkthrough
- Knowledge Base update
- CHANGELOG entry

---

# SMRITI Implementation Plan Governance Policy (IPGP)

## 1. Mandatory Implementation Plan (Rules 1-2)
Before implementing any significant feature, enhancement, optimization, migration, refactoring, framework, SDK component, studio, API, security improvement, or infrastructure change, the AI must create or update an Implementation Plan.
All plans must be stored under `docs/implementation/` organized by area (e.g. `docs/implementation/foundation/`).

## 2. Engineering History & Identification (Rules 3-5)
The AI must never overwrite historical plans. Instead: create a new version, append new phases, mark previous plans as superseded, and preserve history.
Search `docs/implementation/` and identify existing plans before starting. Generate missing historical retrospective plans based on Git, walkthroughs, and ADRs where missing.

## 3. Master Index & Required Sections (Rules 6-7)
Maintain `docs/implementation/README.md` as a chronological master index table.
Every plan must contain these 19 sections:
1. Objective
2. Business Motivation
3. Scope
4. Current State
5. Gap Analysis
6. Architecture Impact
7. Proposed Design
8. Files Created
9. Files Modified
10. Dependencies
11. Risks
12. Rollback Strategy
13. Verification Plan
14. Test Plan
15. Documentation Impact
16. Deployment Plan
17. Status
18. Related ADRs
19. Related Walkthroughs

## 4. Documentation Sync & Lifecycle (Rules 8-9)
Create/update plans must automatically synchronize index tables, walkthroughs, Knowledge Base, CHANGELOG, architecture docs, and developer/user guides.
Lifecycle statuses allowed: Draft, Approved, In Progress, Completed, Superseded, Cancelled.

## 5. Definition of Done (Rule 12)
No task is completed until:
✓ Implementation Plan updated
✓ Walkthrough created
✓ Walkthrough Index updated
✓ Implementation Index updated
✓ Knowledge Base updated
✓ CHANGELOG updated
✓ Documentation synchronized
✓ Tests completed
✓ Architecture Guard passed
✓ License Guard reviewed (if applicable)
✓ Status marked Completed

