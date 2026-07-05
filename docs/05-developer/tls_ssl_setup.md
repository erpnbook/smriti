---
Document ID: "DEV-060"
Title: "TLS/SSL Setup Overview"
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

# TLS/SSL Setup Overview

Frappe Docker supports multiple TLS/SSL approaches. Choose the one that matches your routing needs and where you want the proxy to run.

## Options

### Traefik (built-in HTTPS)

- Use `overrides/compose.https.yaml`
- Best for multi-site setups and advanced routing rules
- Requires `SITES_RULE` and `LETSENCRYPT_EMAIL`
- See [Environment Variables](./setup_env_variables.md) and [Setup Examples](./setup_examples.md#example-3-production-setup-with-https)

#### Traefik deployment models

- **Single stack (Traefik inside the stack):**
  - Use `compose.proxy.yaml` (HTTP) or `compose.https.yaml` (HTTPS)
  - Traefik runs as `proxy` in the same stack
- **Central Traefik for multiple stacks:**
  - Run a dedicated Traefik stack with `compose.traefik.yaml` (and optional `compose.traefik-ssl.yaml` for the dashboard)
  - Each Frappe stack uses `compose.multi-bench.yaml` (and optional `compose.multi-bench-ssl.yaml`)
  - This connects stacks to the shared `traefik-public` network

### nginx-proxy + acme-companion

- Use `overrides/compose.nginxproxy.yaml` plus `overrides/compose.nginxproxy-ssl.yaml`
- Simple host-based routing for single-bench or small setups
- Requires `NGINX_PROXY_HOSTS` and `LETSENCRYPT_EMAIL`
- See [nginx-proxy + acme-companion](nginx_proxy.md)

## Traefik vs nginx-proxy + acme-companion

| Topic               | Traefik (compose.https.yaml)                  | nginx-proxy + acme-companion                                                   |
| ------------------- | --------------------------------------------- | ------------------------------------------------------------------------------ |
| Configuration       | Labels with `SITES_RULE` expression           | Environment variables (`NGINX_PROXY_HOSTS`)                                    |
| Routing             | Flexible (rules, headers, paths)              | Host-based only                                                                |
| Multi-site          | Strong                                        | Works for simple host lists                                                    |
| TLS/ACME            | Built-in                                      | Separate companion container                                                   |
| Certificate storage | `cert-data` volume (`/letsencrypt/acme.json`) | `nginx-proxy-certs` + `acme-data` volumes (`/etc/nginx/certs`, `/etc/acme.sh`) |
| Complexity          | Moderate                                      | Low                                                                            |
| Observability       | Optional dashboard (not enabled here)         | No built-in dashboard                                                          |

### Caddy (external reverse proxy)

- Run Caddy on the host and proxy to the frontend container
- Useful for local HTTPS or when you already use Caddy
- See [Caddy reverse proxy](caddy_https.md)

## Common requirements

- DNS must point to the server for public TLS certificates
- Ports 80 and 443 must be reachable for HTTP-01 challenges
- Use `HTTP_PUBLISH_PORT` and `HTTPS_PUBLISH_PORT` if you need non-default ports

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