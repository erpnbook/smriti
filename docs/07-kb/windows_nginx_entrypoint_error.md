---
Document ID: "KB-030"
Title: "Resolving Docker `nginx-entrypoint.sh` Script Not Found Error on Windows"
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

# Resolving Docker `nginx-entrypoint.sh` Script Not Found Error on Windows

If you're encountering the error `exec /usr/local/bin/nginx-entrypoint.sh: no such file or directory` in a Docker container on Windows, follow these steps to resolve the issue.

## 1. Check Line Endings

On Windows, files often have `CRLF` line endings, while Linux systems expect `LF`. This can cause issues when executing shell scripts in Linux containers.

- **Convert Line Endings using `dos2unix`:**
  ```bash
  dos2unix resources/core/nginx/nginx-entrypoint.sh
  ```

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