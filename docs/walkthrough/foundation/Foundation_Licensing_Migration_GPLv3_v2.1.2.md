# Walkthrough - Foundation Licensing Migration GPLv3 v2.1.2

Migration of the SMRITI Retail OS primary repository and the SMRITI Foundation SDK repository from the MIT License to the **GNU General Public License v3.0 (GPL-3.0-only)** has been successfully completed and verified.

## 1. Scope
- Update repository-wide primary licensing documents (`LICENSE`, `COPYING`).
- Formulate notice and dependency license registries (`NOTICE`, `THIRD_PARTY_LICENSES.md`).
- Restore the `smriti_foundation` SDK repository under `apps/smriti_foundation` to enable deployment pull syncing into the testing environment (`F:\Smriti9`).
- Migrate `smriti_foundation` to GPL-3.0-only.
- Safely migrate source code comment headers in all SMRITI-owned files (518 in `smriti_retail_os` + 17 in `smriti_foundation` + 8 workspace scripts/tools).

## 2. Files Created
- [COPYING](file:///D:/Smriti_Retail_OS/COPYING)
- [NOTICE](file:///D:/Smriti_Retail_OS/NOTICE)
- [THIRD_PARTY_LICENSES.md](file:///D:/Smriti_Retail_OS/THIRD_PARTY_LICENSES.md)
- [apps/smriti_foundation/LICENSE](file:///D:/Smriti_Retail_OS/apps/smriti_foundation/LICENSE)

## 3. Files Modified
- [LICENSE](file:///D:/Smriti_Retail_OS/LICENSE)
- [README.md](file:///D:/Smriti_Retail_OS/README.md)
- [pyproject.toml](file:///D:/Smriti_Retail_OS/pyproject.toml)
- [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [.agents/AGENTS.md](file:///D:/Smriti_Retail_OS/.agents/AGENTS.md)
- [.gitignore](file:///D:/Smriti_Retail_OS/.gitignore)
- [apps/smriti_foundation/pyproject.toml](file:///D:/Smriti_Retail_OS/apps/smriti_foundation/pyproject.toml)
- [apps/smriti_foundation/README.md](file:///D:/Smriti_Retail_OS/apps/smriti_foundation/README.md)
- [apps/smriti_foundation/smriti_foundation/hooks.py](file:///D:/Smriti_Retail_OS/apps/smriti_foundation/smriti_foundation/hooks.py)
- 543 SMRITI-owned source files containing license headers (`.py`, `.html`, `.css`, `.js`)

## 4. Verification Plan

### Automated Linters
- Ran `python smriti_retail_os/tools/validate_tokens.py smriti_retail_os/public/css`. Output matches original baseline (5 pre-existing errors in `sas.css` and `smriti_purchase.css`).
- Ran `python smriti_retail_os/tools/validate_architecture.py`. Matches baseline.

### Staging Verification
- Verified that `git pull` inside `F:\Smriti9\apps\smriti_foundation` pulls and fast-forwards cleanly from `d:\Smriti_Retail_OS\apps\smriti_foundation`.
- Verified page loads in browser without errors.
