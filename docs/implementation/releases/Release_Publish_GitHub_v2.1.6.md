# Implementation Plan: SMRITI Release & GitHub Publication v2.1.6

## 1. Objective
Publish a new semantic patch/sub-release `v2.1.6` to GitHub, pushing all local security audit, architecture, and CI integration commits and tags, and publishing a GitHub Release with the compiled release notes.

## 2. Business Motivation
Deploy and lock in the pre-launch security hardening, linter compliance gates, and test execution framework for downstream environments and continuous integration.

## 3. Scope
- Update [VERSION.md](file:///D:/Smriti_Retail_OS/VERSION.md) to bump application version.
- Overwrite [RELEASE_NOTES.md](file:///D:/Smriti_Retail_OS/RELEASE_NOTES.md) for version `v2.1.6`.
- Stage and commit release files.
- Tag the commit as `v2.1.6`.
- Authenticate and push both main branch and the tag to GitHub `origin`.
- Publish a GitHub Release using the GitHub CLI `gh` tool.

## 4. Current State
Local `main` branch has the security remediation and test updates committed, tagged locally as `v2.1.6`. The GitHub remote repository is at commit `3e09918`.

## 5. Gap Analysis
The GitHub remote does not have the latest commits, tag, or release package for `v2.1.6`.

## 6. Architecture Impact
None.

## 7. Proposed Design
1. Update version tracking documents in the workspace.
2. Commit and tag.
3. Authenticate Git origin URL with the user's Personal Access Token (PAT).
4. Run `git push origin main` and `git push origin v2.1.6`.
5. Reset Git origin URL back to the clean public URL.
6. Authenticate and run `gh release create v2.1.6 --title "Release v2.1.6" --notes-file RELEASE_NOTES.md` using the same PAT.

## 8. Files Created
None.

## 9. Files Modified
- [VERSION.md](file:///D:/Smriti_Retail_OS/VERSION.md)
- [RELEASE_NOTES.md](file:///D:/Smriti_Retail_OS/RELEASE_NOTES.md)

## 10. Dependencies
GitHub CLI `gh` version 2.87.3.

## 11. Risks
Exposing the PAT in config files (mitigated by using `$env:GH_TOKEN` environment variable for `gh` CLI, and resetting the git remote URL immediately after push).

## 12. Rollback Strategy
Remove the remote tag and delete the GitHub release via `gh release delete v2.1.6 --yes`.

## 13. Verification Plan
Run `gh release view v2.1.6` and print the release details.

## 14. Test Plan
Ensure all 153/153 integration tests run and pass successfully before publishing (already completed and verified!).

## 15. Documentation Impact
`VERSION.md` and `RELEASE_NOTES.md` are updated to reflect the new release.

## 16. Deployment Plan
Pull the new release commits and tags on the test environment `F:\Smriti9`.

## 17. Status
Completed


## 18. Related ADRs
None.

## 19. Related Walkthroughs
- [Security_Redo_Permission_Audit_And_CI_Wiring_v2.1.6.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/security/Security_Redo_Permission_Audit_And_CI_Wiring_v2.1.6.md)
