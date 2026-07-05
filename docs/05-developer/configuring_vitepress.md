---
Document ID: "DEV-020"
Title: "Configuring VitePress"
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

# Configuring VitePress

To modify any VitePress related settings, a JavaScript development environment is needed. Everything related to VitePress is contained in the `docs/` folder.

## Prerequisites

1. Node.js v24 or above is recommended. To install and manage Node.js [nvm](https://github.com/nvm-sh/nvm) is the preferred way for Linux and MacOS. For Windows either official installer or [fnm](https://github.com/Schniz/fnm).
2. pnpm package manager, v10.28 or above. Easiest way to install pnpm is using [corepack](https://pnpm.io/installation#using-corepack) which is part of Node.js.

## Development

To start a development environment,

1. Navigate to `/docs` directory in the terminal

```sh
cd docs
```

2. Install dependencies

```sh
pnpm install
```

3. Start the development server

```sh
pnpm run docs:dev
```

4. Open `http://localhost:5173/frappe_docker` in your browser to see the development version which will update the preview as you make changes.

## Configurations

1. Public assets related to VitePress site is added in the `docs/public` folder. This folder should **NOT** be used for adding images added inside the `.md` file.
2. VitePress uses `index.md` files to do some special things. For example the home page is configured using the `docs/index.md` file. Checkout the file for more details.
3. VitePress uses 'file based routing', meaning the URL paths mimics the directory and file structure inside the `docs/` directory.
4. VitePress specific config is `docs/.vitepress/config.mts`.
5. To auto populate the sidebar, a plugin called 'VitePress Sidebar' is used. The `config.mts` also include config for this plugin. More details can be found in the [documentation page](https://vitepress-sidebar.cdget.com/guide/getting-started).
6. Each subfolder has an `index.md` file. This is used to specify the group heading of the pages in the sidebar.

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