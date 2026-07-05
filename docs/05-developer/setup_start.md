---
Document ID: "DEV-056"
Title: "start Container"
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

# start Container

Once your compose file is ready, start all containers with a single command:

```bash
docker compose -p frappe -f compose.custom.yaml up -d
```

```bash
podman-compose --in-pod=1 --project-name frappe -f compose.custom.yaml up -d
```

The `-p` (or `--project-name`) flag names the project `frappe`, allowing you to easily reference and manage all containers together.

# Create a site and install apps

Frappe is now running, but it's not yet configured. You need to create a site and install your apps.

## Basic site creation

```bash
docker compose -p frappe exec backend bench new-site <sitename> --mariadb-user-host-login-scope='172.%.%.%'
docker compose -p frappe exec backend bench --site <sitename> install-app erpnext
```

```bash
podman exec -ti erpnext_backend_1 /bin/bash
bench new-site <sitename> --mariadb-user-host-login-scope='172.%.%.%'
bench --site <sitename> install-app erpnext
```

Replace `<sitename>` with your desired site name.

## Create site with app installation

You can install apps during site creation:

```bash
docker compose -p frappe exec backend bench new-site <sitename> \
  --mariadb-user-host-login-scope='%' \
  --db-root-password <db-password> \
  --admin-password <admin-password> \
  --install-app erpnext
```

> **Note:** Wait for the `db` service to start and `configurator` to exit before trying to create a new site. Usually this takes up to 10 seconds.

For more site operations, refer to [site operations](../02-user-guide/site_operations.md).

> ## Understanding the MariaDB User Scope
>
> The flag --mariadb-user-host-login-scope='172.%.%.%' allows database connections from any IP address within the 172.0.0.0/8 range. This includes all containers and virtual machines running on your machine.
>
> **Why is this necessary?** Docker and Podman assign dynamic IP addresses to containers. If you set a fixed IP address instead, database connections will fail when the container restarts and receives a new IP. The wildcard pattern ensures connections always work, regardless of IP changes.
>
> **Security note:** This scope is sufficient because only the backend container accesses the database. If you need external database access, adjust the scope accordingly, but be cautious with overly permissive settings.

---

**Back:** [Build Setup →](setup_build.md)

**Next:** [Setup Examples →](setup_examples.md)

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