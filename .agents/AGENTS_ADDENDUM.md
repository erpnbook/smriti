# SMRITI UI & Agent Verification Governance Rules — Addendum

The following two rules extend the existing 7 verification rules. They
close two failure modes observed in practice: a confident summary
attached to real evidence, and tool-call narration presented without
showing what the tool actually returned.

## 8. No Summary Judgments
Do not append an overall quality score, a star rating, a "production-ready"
verdict, or congratulatory framing (✅, "successfully," "robust," "strong
foundation") to a verification report.

- State only what was checked and what the literal output showed.
- Do not assign a numeric score (e.g. "9.8/10") to your own work, in
  whole or by category.
- Do not declare a module, file, or feature "production-ready" — that
  is a judgment for the human to make from the evidence presented, not
  a conclusion the agent reaches on its own behalf.
- If you want to indicate the work is complete, use the literal status
  words "Done" or "Unverified" (per Rule 7) and nothing more.

**Why:** a confident verdict attached to real evidence trains the human
to trust the verdict instead of reading the evidence. The evidence
should be sufficient on its own; the score is not load-bearing and
tends to survive even when the evidence underneath it later turns out
to be incomplete or fabricated.

## 9. Show Outputs, Not Just Actions
Narrating that a command was run, a file was edited, or a tool was used
is not evidence of what happened. Every action must be followed
immediately by the actual output it produced — not a transition
straight to the next step.

- "Ran command: `X`" must be followed by the literal stdout/stderr of
  that command, even if empty, even if it's a single line.
- "Edited `file.py`" must be followed by either the diff (per Rule 1)
  or, if the editing tool returned a confirmation/error, that literal
  return value.
- "Used tool: `Y`" must be followed by that tool's actual return value,
  not a paraphrase of what the agent expects or assumes it did.
- A sequence of "Ran command... Edited... Ran command..." steps with no
  shown output between them, followed only by a closing prose summary,
  does not satisfy Rules 1–7 even if the summary's claims are
  individually plausible.

**Why:** a list of actions taken, with no output shown, is structurally
identical whether every action succeeded, partially failed, or never
ran at all. The human reading it cannot tell the difference without
output — which means this format carries the same risk as the phantom
claims these rules exist to prevent, even when nothing is technically
asserted to be "done."

---

### Self-check before sending any report
Before presenting a verification report, the agent should confirm:
- [ ] Every modified file has a pasted diff (Rule 1), not a description
- [ ] Every test claim has pasted terminal output (Rule 2)
- [ ] Every lint/validator claim has pasted console output (Rule 3)
- [ ] Every metric has a shown before/after measurement (Rule 4)
- [ ] Prior session claims were independently re-checked, not assumed (Rule 5)
- [ ] Scope is enumerated file-by-file, not summarized at module level (Rule 6)
- [ ] Anything not fully verified is labeled "Unverified," not "Done" (Rule 7)
- [ ] No score, star rating, or "production-ready" verdict appears anywhere (Rule 8)
- [ ] Every "Ran command" / "Edited" / "Used tool" line is followed by its actual output (Rule 9)

If any box can't be checked, the report is incomplete — fix that before
sending it, don't send it with a caveat instead.
