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
