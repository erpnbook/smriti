# SMRITI AI Agent Workflow Guide
**Status:** DRAFT
**File:** `/SMRITI_AI_AGENT_GUIDE.md`
**Internal Version:** 1.0.0 (Established 2026-07-01)

---

## Pre-Task Agent Checklist

BEFORE writing, editing, or deleting any code in this repository, you MUST run this checklist, state responses inline in the chat, and adhere to each step. Do not skip this because a task "seems small."

### Step 1. Read the SMRITI Product Constitution (SPC)
- Read `/SMRITI_PRODUCT_CONSTITUTION.md` in full.
- Verify the active status at the top of the file (DRAFT / LOCKED / FROZEN).

### Step 2. Identify Applicable SPC Articles
- Identify which Adopted Articles (SPC-001 through SPC-007) apply to this task.
- State exactly what evidence you will produce to satisfy each applicable article's enforcement requirement.

### Step 3. Confirm Candidate Articles are Parked
- Review the Candidate Articles table.
- Do not cite Candidate Articles as a reason to block, refuse, or restructure a task. If you believe one should apply, ask explicitly.

### Step 4. Formulate Evidence-First Strategy (SPC-004 / SPC-007)
- Plan exactly what Evidence Level A or B artifact you will produce.
- Never write reports that present conclusions or scores (e.g. "100/100") without preceding them with raw logs/hashes/screenshots.

### Step 5. Safe Refactoring Verification (SPC-003)
- If the task requires deleting, renaming, or moving any file, function, route, or DocType, perform a dependency/reference scan first.
- Paste the raw search logs in the chat BEFORE making the change.

### Step 6. Prior-Art Search (SPC-002)
- If creating a menu, report, DocType, route, API endpoint, widget, or nav entry, search the repository for an existing equivalent first.
- Document in the chat: what was searched, what was found, why it was not reused.

### Step 7. Define Scope Boundary (SPC-006)
- Clearly define the boundaries of the assigned task.
- Explicitly list which files will be modified and verify no extraneous files are touched.

### Step 8. Validate Negative Results (SPC-005)
- If a scan or test produces a negative result (e.g. "NONE" or "0 violations"), paste the exact command run and the literal empty output.
- Never use a self-defeating filter that excludes the files being checked.

---

## PR Description Template

Every Pull Request description submitted by an AI agent must utilize this template:

```markdown
# PR Title: [Brief summary]

## Scope Integrity (SPC-006)
- **Requested Scope:** [Scope defined by user]
- **Implemented Scope:** [List of modified files]
- **Additional Changes:** [List any extra changes, or "None"]

## Prior-Art Search (SPC-002)
- **Search Query:** [Search term used]
- **Results:** [Found equivalent files/functions]
- **Justification for New Creation:** [Why reuse was not possible]

## Refactoring Dependency Scan (SPC-003)
- **Deleted/Modified Items:** [List or "None"]
- **Scan Command:** [rg/grep command]
- **Scan Results:** [Paste raw results showing 0 references]

## Verification Evidence (SPC-004)
- **Evidence Level A:** [Pasted test terminal logs or commit hash]
- **Evidence Level B:** [Screenshots or scan logs]
```