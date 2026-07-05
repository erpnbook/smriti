---
Document ID: "ARCH-005"
Title: "SMRITI AI Content Policy (AI-GOV-01)"
Owner: "Architecture Team"
Audience: "Architect"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# SMRITI AI Content Policy (AI-GOV-01)

**Status:** LOCKED (Frozen for SMRITI v1.0)  
**Version:** 1.0  
**Effective:** 2026-06-21  
**Applies To:** All AI Coding Agents, Writers, and Automated Content Pipelines.  

---

## 1. Overview

SMRITI Retail OS leverages multiple AI agents (including Gemini, Claude, GPT, and custom internal assistants) for documentation generation, database glossary compilation, in-app explainers, and diagnostic logging. This policy enforces strict compliance rules to maintain high tone standards, prevent brand drift, and secure internal system architecture definitions.

---

## 2. Mandatory Writing Directives

All AI agents generating content for SMRITI must follow these rules:

1. **User Guides & Manuals**:
   * **Language**: Professional, clean, objective business English.
   * **Exclusions**: Founder notes, personal biographies, architectural descriptions, developer jargon, or informal commentary.
2. **Business Glossary & Dictionary**:
   * **Language**: English definition with a localized **Hinglish** equivalent (`hinglish_definition` database field). Hinglish is supported to aid floor managers and cashiers in understanding complex retail concepts.
3. **Developer Documents**:
   * **Language**: Technical English. Detail-oriented, containing database schemas, API specs, and hooks.

---

## 3. Compliance & Gating Rules

AI agents are strictly prohibited from:
* **Inventing Licensing Claims**: Do not write false statements about system features, warranties, trial limits, or support contracts.
* **Removing Required Attribution**: Do not remove open-source copyright statements, developer credits (`AITDL`), or trademark references.
* **Generating Unauthorized Branding**: Do not introduce alternative branding, compound logos, or unofficial style definitions.
* **Leaking Internal Architectures**: Do not expose database schemas, internal table indexes, raw code variables, or system designs inside operator-facing user guides.


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |