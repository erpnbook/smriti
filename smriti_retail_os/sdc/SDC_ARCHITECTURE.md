# SMRITI Documentation Compiler (SDC) — Architecture Manual (v1.1.2 GA)

---

## 1. Executive Summary & Core Identity

SMRITI Documentation Compiler (SDC) is a deterministic, compiler-driven knowledge extraction and validation engine built for **SMRITI Retail OS**. Unlike traditional documentation generators that parse source code and render outputs in a single execution loop, SDC implements a clean separation of concerns using a versioned, immutable **Intermediate Representation (IR)**.

SDC does not explain system behavior; it validates structural implementation evidence.

---

## 2. Decoupled Compilation Flow

The compiler pipelines documentation rendering through four distinct, isolated phases:

```
                  ┌─────────────────────────────────────┐
                  │      Repository Source Files        │
                  └──────────────────┬──────────────────┘
                                     │
                                     │ Phase 0: Discovery Parser (AST & JSON)
                                     ▼
                  ┌─────────────────────────────────────┐
                  │  Intermediate Representation (IR)   │  ◄── [IMMUTABLE SNAPSHOT]
                  └──────────────────┬──────────────────┘
                                     │
                                     │ Phase 1-6: Renderers & Transformers
                                     ▼
                  ┌─────────────────────────────────────┐
                  │      Generated Documentation        │
                  └──────────────────┬──────────────────┘
                                     │
                                     │ Phase 7: Quality Gate Validators
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        Validated Release            │
                  └─────────────────────────────────────┘
```

1. **Discovery (Phase 0)**: Scans the codebase, parses JSON schemas and Python AST structures, and writes the immutable Intermediate Representation (IR). This is the only phase permitted to access the source repository.
2. **Intermediate Representation (IR)**: A collection of static, version-controlled JSON files that act as the compiler's Single Source of Truth.
3. **Transformation & Rendering (Phases 1–6)**: Consumes the static JSON IR and renders output formats (Markdown, diagrams, PDF catalogs). This phase is barred from reading repository files.
4. **Validation Quality Gate (Phase 7)**: Executes automated integrity checks (schema conformance, provenance tracing, cross-link validation, cycle checks) to assert that the compiled output is publishable.

---

## 3. High-Level Design Principles

* **Single Source of Truth**: Documentation is generated directly from the machine-readable IR, which represents the direct physical footprint of the code.
* **Immutability of Context**: Once Phase 0 completes, all input data is locked. This eliminates compilation drift and context window exhaustions during long-running builds.
* **Traceability and Provenance**: Every generated document page carries clear metadata proving which source file and compiler pass produced it.
* **Stable Artifact Identity**: Moving files or refactoring directory layouts must never alter the unique identifiers allocated to the system components.

---

## 4. Governance Constitutions

### SDC Rule #13 — Evidence Before Explanation
A discovery phase must never explain behavior. It may only report implementation evidence. Behavioral explanations, architectural interpretations, recommendations, and user-facing descriptions belong exclusively to later phases that consume verified discovery artifacts.

### SDC Rule #14 — Deterministic Replay
Given the same repository commit, compiler configuration, and inputs, the Documentation Compiler must produce semantically identical artifacts. Differences are limited to timestamps, generation IDs, and other explicitly designated metadata. Any unexpected output differences are treated as regressions.

### SDC Rule #15 — Backward Compatibility
Any change to an IR schema, Artifact ID format, Evidence Type, or Provenance contract shall require an explicit schema version increment and a documented migration strategy. New compiler releases must either consume previous IR versions or fail with a clear compatibility error. Silent interpretation changes are prohibited.

### SDC Rule #16 — Stable Artifact Identity
Once an Artifact ID has been assigned to an implementation artifact, it shall remain stable for the lifetime of that artifact. File moves, directory reorganizations, or renderer changes must not change the Artifact ID. If an artifact is retired, its ID shall be marked as retired and never reused.

---

## Revision History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.1.2-GA | 2026-06-25 | Jawahar R. Mallah | Initial frozen release of SDC GA Architecture specification. |

---

## Author Profile

* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> 
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
