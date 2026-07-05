---
Document ID: "INSTALL-006"
Title: "Important Concept: Immutability and Persistence"
Owner: "Installation Team"
Audience: "Installer"
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

# Important Concept: Immutability and Persistence

A frequent source of confusion is how **Docker-based Frappe deployments handle persistence**.

### Containers Are Immutable

Docker containers are **not meant to be modified after they are built**.
You should only change:

- Environment variables
- Mounted volumes
- The Docker image itself (via rebuild)

### What Is Persistent

Typically, only these paths are persisted:

- Site data (`/sites`)
- Database storage

This allows you to:

- Create new sites
- Run migrations
- Perform backups and restores
- Recreate containers safely

## Installing Apps After Deployment

### ❌ Not Supported

Installing apps into a running container is **not supported**.

`bench get-app` is an examples of an common but unsupported action.

### Why?

- Apps are part of the **Docker image**
- Runtime changes are lost on container recreation
- This ensures reproducibility and stability

### Correct Workflow

1. Add the app to the image build configuration
2. Rebuild the Docker image
3. Redeploy the stack

This applies to **all production-oriented setups**.

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