---
Document ID: "KB-002"
Title: "Arm64 Apple Silicon Issues"
Owner: "Support Team"
Audience: "Support Engineer"
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

## Notes on ARM64 and Apple Silicon

- Enable Docker Desktop's Rosetta emulation for initial builds when running on Apple Silicon with x86-only images.
- Prefer published multi-arch images (`frappe/bench`, `frappe/erpnext`) or build locally with `docker buildx bake --set *.platform=linux/amd64,linux/arm64` to cover both architectures in one pass.
- When using `pwd.yml`, export `DOCKER_DEFAULT_PLATFORM=linux/arm64` (or select the provided compose profile) to avoid unexpected emulation.
- Keep bind mounts under your user home directory and apply `:cached` or `:delegated` consistency flags for better performance on macOS.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL