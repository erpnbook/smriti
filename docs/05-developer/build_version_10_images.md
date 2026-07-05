---
Document ID: "DEV-003"
Title: "Build Version 10 Images"
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

Clone the version-10 branch of this repo

```shell
git clone https://github.com/frappe/frappe_docker.git -b version-10 && cd frappe_docker
```

Build the images

```shell
export DOCKER_REGISTRY_PREFIX=frappe
docker build -t ${DOCKER_REGISTRY_PREFIX}/frappe-socketio:v10 -f build/frappe-socketio/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/frappe-nginx:v10 -f build/frappe-nginx/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/erpnext-nginx:v10 -f build/erpnext-nginx/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/frappe-worker:v10 -f build/frappe-worker/Dockerfile .
docker build -t ${DOCKER_REGISTRY_PREFIX}/erpnext-worker:v10 -f build/erpnext-worker/Dockerfile .
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