---
Document ID: STYLE-001
Title: SMRITI Documentation Style Guide
Owner: Chief Architect
Audience: Developer / Architect / Support
Module: Core
Version: 1.0.0
Status: Frozen
Primary Document: Yes
Depends On: ""
Related Modules: ""
Last Updated: 2026-06-25
Last Reviewed: 2026-06-25
AI Generated: Yes
Reviewed By: Jawahar R. Mallah
---

# SMRITI Documentation Style Guide

**Governance Version**: 1.0.0  
**Status**: FROZEN  
**Effective Date**: 2026-06-25  
**Change Control**: Chief Architect Approval Required  

---

## Heading Hierarchy

All documents must follow standard markdown title and section hierarchies:
- `#` (H1) — Document Title (Only one per document).
- `##` (H2) — Major Sections (Overview, Steps, Examples, Related Documents, Revision History).
- `###` (H3) — Sub-sections.
- `####` (H4) — Sub-sub-sections or specific file modifiers.

---

## Tone & Voice

- **Professional & Precise**: Use clear, concise language. Avoid jargon or conversational filler.
- **Instructional**: Write user guides with direct, active verbs (e.g., "Run this command", "Select this role").
- **Explainable**: For any formulas or logic, explain the business meaning first before detailing variables and calculations.

---

## Markdown Formatting Conventions

- **Code blocks**: Use fenced code blocks with language specification:
  ```python
  def calculate_score():
      pass
  ```
- **Tables**: Use tables to organize comparative details, parameter descriptions, or inventories.
- **Bold text**: Emphasize UI elements (e.g., "Click **Save**").
- **File Links**: Always use repository-relative links. **Absolute `file:///` URLs are strictly prohibited.**
  - *Correct*: `[ARCH-011](./08-architecture/clienteling_architecture_blueprint.md)`
  - *Incorrect*: `[ARCH-011](./08-architecture/clienteling_architecture_blueprint.md)`

---

## Emoji & Callout Standards

Use GitHub-style alert callouts strategically to highlight key info:

> [!NOTE]
> Used for background context, useful tips, or minor details.

> [!IMPORTANT]
> Used for essential configuration steps or mandatory workflows.

> [!WARNING]
> Used to warn against potential pitfalls, deprecations, or upgrades.

> [!CAUTION]
> Used for high-risk actions (e.g., database migrations, data loss).

---

## Mandatory Header Metadata Schema

Every document must begin with a YAML frontmatter block. The authoritative schema is defined in [documentation_schema.yaml](./tools/documentation_schema.yaml).

```yaml
---
Document ID: PREFIX-###
Title: Official Document Title
Owner: [Team or Role - e.g., Chief Architect / Finance Team]
Audience: [Product / User / Admin / Developer / Architect]
Module: [Related SMRITI module or Core]
Version: 1.0.0
Status: [Draft / Review / Approved / Active / Deprecated / Archived]
Primary Document: [Yes / No]
Depends On: [Optional - Other Document IDs]
Related Modules: [Optional - List of other modules]
Last Updated: YYYY-MM-DD
Last Reviewed: YYYY-MM-DD
AI Generated: [Yes / No]
Reviewed By: Jawahar R. Mallah
---
```

### ID Prefix Mappings:
- `PROD-###` — 01-product
- `USER-###` — 02-user-guide
- `ADMIN-###` — 03-admin-guide
- `INSTALL-###` — 04-installation
- `DEV-###` — 05-developer
- `API-###` — 06-api
- `KB-###` — 07-kb
- `ARCH-###` — 08-architecture
- `REL-###` — 09-release-notes

---

## Formula & Metric Explainability Format

Any calculated KPI or metric must contain the following section:

### Formula Explainability: [Metric Name]
1. **Business Meaning**: What does the metric track and why is it valuable to a business user?
2. **Formula Expression**: The mathematical formula.
3. **Worked Example**: An arithmetic walkthrough using realistic retail values.
4. **Data Sources**: Source databases or transaction tables.
5. **Interpretation Guide**: Health thresholds/score bands.
6. **Recommended Actions**: Guidelines on what steps to take next.

---

## Revision History Format

All modifications must be recorded at the bottom of the document using this table format:

```markdown
## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | YYYY-MM-DD | [Author Name] | Initial creation |
```

---

## Author Attribution

Every document must include the standard Author block at the end:

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah

---

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial frozen release of SMRITI Documentation Style Guide v1.0.0 |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah
