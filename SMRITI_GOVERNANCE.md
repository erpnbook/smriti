# SMRITI Governance & CI Specification
**Status:** DRAFT
**File:** `/SMRITI_GOVERNANCE.md`
**Internal Version:** 1.0.0 (Established 2026-07-01)

---

## Evidence Levels

SMRITI utilizes a structured evidence framework to categorize and evaluate all verification claims made by developer agents:

### Evidence Level A (Verifiable Live Artifacts)
- **Definition:** Raw, reproducible log outputs directly from the system, or a verifiable Git commit hash.
- **Examples:**
  - Standard output/error of a test runner (e.g. `pytest` or `bench run-tests`)
  - A real, pushed git commit hash (e.g. `39cdcfb` verified in `git log`)
  - Actual console output of an AST linter or validator
- **Usage:** Required for SPC-003 (Refactoring) and SPC-004 (Completion).

### Evidence Level B (Attached Visual/Static Artifacts)
- **Definition:** Human-verifiable attachments that document a state but are not directly executable in a terminal.
- **Examples:**
  - Raw directory scan outputs (grep / ripgrep logs)
  - Browser screenshots showing UI rendering
  - Video recordings of automated browser tests
- **Usage:** Required for SPC-001 (Leakage) and SPC-002 (Prior-Art).

### Evidence Level C (Reference to Existing Passing Test)
- **Definition:** Pointing to an automated test that is already integrated into the main branch test suite.
- **Usage:** Used for verifying regression safety.

### Evidence Level D (Agent Assertion Only)
- **Definition:** Pure prose statements, summaries, or assertions made by the agent without attached logs, hashes, or screenshots.
- **Usage:** **EXPLICITLY REJECTED** as evidence of completion or correctness.

---

## Enforcement Levels & CI Actions

Each SMRITI Policy Constraint (SPC) is mapped to a severity level that defines its behavior in the CI/CD pipeline:

| Severity | PR Merge Effect | CI Status | Action on FAIL |
|---|---|---|---|
| **Critical** | Blocks merge automatically | FAIL | PR cannot be merged. Exit 1. |
| **Major** | Blocks merge unless exempt | FAIL | PR blocked unless a valid ADR is attached. |
| **Minor** | Warning only | WARNING | PR can merge. Issues logged in summary. |
| **Informational** | No block, logged | INFO | Educational logging only. |

---

## CI Status Reporting Format & Verified Controls

The active governance verification controls are executed dynamically in CI or via pre-commit hooks:

| Rule | Description | Enforcement Mechanism | Status |
|---|---|---|---|
| **SPC-000** | The Golden Rule | `smriti_architecture_guard.py` (Persistence boundary) | CI-Verified |
| **SPC-001** | No Framework Leakage | `scripts/validate_html_templates.py` (TEMPLATE-01 pre-commit check) | Verified |
| **SPC-002** | Single Source of Truth | Manual PR / Prior-Art Search Review | Manual |
| **SPC-003** | Safe Refactoring | Manual PR dependency scan attachment check | Manual |
| **SPC-004** | Evidence-First Completion | Automated linter rule checking for commit hashes / test logs | Planned |
| **SPC-005** | AI Honesty Principle | Human check of terminal logs and Git commits | Manual |
| **SPC-006** | Scope Integrity | Git diff vs PR description check | Manual |
| **SPC-007** | Single Source of Evidence | Structure validation (Evidence -> Findings -> Conclusion) | Manual |
| **SPC-008** | Standing Governance Principle | Document Change Budget validation | Manual |
| **SPC-009** | Policy Before Implementation | SSDL Capability Ownership Matrix alignment check | Manual |
| **SPC-010** | Ownership Before Construction | SSDL Capability Ownership Map verification | Manual |
| **SPC-011** | Conflict Escalation | Architecture Review / ADR Registry check | Manual |

---

## Active Gating Tools

The active enforcement validators are:
1. **Pre-Commit HTML Template Leak Checker (`scripts/validate_html_templates.py`)**: Runs on staged `.html` files before commit to catch framework leakages.
2. **Whitelist ignore_permissions Linter (`tools/audit/check_ignore_permissions.py`)**: Fails builds if whitelisted API decorators bypass permission verification without a `# reviewed-ignore-permissions` tag.
3. **SMRITI Architecture Guard (`smriti_architecture_guard.py`)**: Checks for persistence boundary violations.
4. **Pre-Commit Phantom Link & Authority Validators (Planned)**: Checkers to validate link references and precedence hierarchies.

Run all active Python audit checkers locally:
```bash
python smriti_architecture_guard.py
python tools/audit/check_ignore_permissions.py
```