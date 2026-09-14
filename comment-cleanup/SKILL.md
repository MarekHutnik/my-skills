---
name: comment-cleanup
description: Clean code comments so each says what the code is or must be, cutting history, rationale, consequences and measurements, and catching comments that describe code which no longer exists. Use when asked to clean up, trim, audit or review comments or docstrings, when preparing a PR for review, or when comments have drifted from the code around them.
---

# Comment cleanup

Clean the comments in every file this branch touches — the **whole file**, not only the
lines this change introduced. Comments only: no behaviour changes.

## The rule

A comment says what the code **is** or **must be**. If it says what it used to be, what
would break, or why we chose this — that belongs in a test name, the PR body, or `docs/`.
Measurements never go in comments; they go in the PR that made them.

## Keep

- What the code does, and what must hold for it to be correct
- A mechanism when it explains a non-obvious constraint (e.g. "`close()` takes the lock a
  blocked `readline()` holds") — that is *what is*, not *why we chose*
- `Args:` / `Returns:` / `Raises:` blocks
- ⚠️ flags for AI review, trimmed per below

## Cut

- **History**: "it used to be…", "before X…", "this was changed when…"
- **Consequences**: "without this, X would break", "if this ever stops holding…"
- **Rationale and design process**: "we chose this because…", rejected alternatives,
  "WHY THIS IS NOT \<library\>"
- **Measurements**: timings, sizes, byte counts, benchmark numbers
- **Narrating section headers**: "THE FAILURE THIS PREVENTS", "THE DEPENDENCY THIS GUARDS"
- **Test names cited inside implementation comments**

## ⚠️ flags for AI review

Keep them — they stop future reviews re-raising known issues. They follow the same
discipline: a pure description of the problem and why it is rejected. No narrative, no
measurements.

## Test docstrings

Same rule. Keep only what the test **name** does not already say. If the name covers it,
delete the body, or the whole docstring. No narrative, no measurements.

## Do NOT trim

- **`docs/`** — narrative, rationale and history legitimately live there. Do still remove
  measurements: those belong in the PR that made them.
- **Error and exception messages** — user-facing, and free to explain.

## Two checks that matter more than style

1. **Staleness.** A comment describing code that no longer exists is the worst offender.
   Verify every factual claim against the current code and *fix* it — don't just shorten a
   sentence that is wrong. This is the highest-value part of the pass.
2. **Duplication.** A comment restating a `docs/` file goes stale *because* it is a
   duplicate with no test and no reader. Replace it with a short statement of what the code
   is, plus a pointer to the doc. Check the doc is actually correct before pointing at it.

## Finally

- Check no comment was orphaned above the wrong statement by an earlier code move.
- Run lint and the full test suite: a comments-only pass must be a no-op.
- Report net comment lines removed vs. added, and list any staleness you found.
