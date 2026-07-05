---
Document ID: "DEV-022"
Title: "Debugging"
Owner: "Development Team"
Audience: "Developer"
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

Add the following configuration to `launch.json` `configurations` array to start bench console and use debugger. Replace `development.localhost` with appropriate site. Also replace `frappe-bench` with name of the bench directory.

```json
{
  "name": "Bench Console",
  "type": "python",
  "request": "launch",
  "program": "${workspaceFolder}/frappe-bench/apps/frappe/frappe/utils/bench_helper.py",
  "args": ["frappe", "--site", "development.localhost", "console"],
  "pythonPath": "${workspaceFolder}/frappe-bench/env/bin/python",
  "cwd": "${workspaceFolder}/frappe-bench/sites",
  "env": {
    "DEV_SERVER": "1"
  }
}
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