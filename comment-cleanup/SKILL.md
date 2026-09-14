---
name: comment-cleanup
description: Clean code comments and docstrings so each says what the code is or must be — cutting history, rationale, consequences and measurements — catch comments and docstrings that describe code which no longer exists, and report functions, methods and classes that are missing a docstring. Use this whenever the user asks to clean up, trim, tidy, audit or review comments or docstrings, whenever they mention docstring coverage or missing docstrings, when preparing a branch or PR for review, or when comments have drifted from the code around them — even if they don't use the word "comment".
---

# Comment and docstring cleanup

Clean the comments and docstrings in every file this branch touches — the **whole file**, not
only the lines this change introduced. Comments only: no behaviour changes.

## The rule

A comment says what the code **is** or **must be**. If it says what it used to be, what
would break, or why we chose this — that belongs in a test name, the PR body, or `docs/`.
Measurements never go in comments; they go in the PR that made them.

This holds for docstrings too. A docstring is a comment with a contract attached.

## Keep

- What the code does, and what must hold for it to be correct
- A mechanism when it explains a non-obvious constraint (e.g. "`close()` takes the lock a
  blocked `readline()` holds") — that is *what is*, not *why we chose*
- `Args:` / `Returns:` / `Raises:` blocks — they are the contract, not narrative
- ⚠️ flags for AI review, trimmed per below

## Cut

- **History**: "it used to be…", "before X…", "this was changed when…"
- **Consequences**: "without this, X would break", "if this ever stops holding…"
- **Rationale and design process**: "we chose this because…", rejected alternatives,
  "WHY THIS IS NOT \<library\>"
- **Measurements**: timings, sizes, byte counts, benchmark numbers
- **Narrating section headers**: "THE FAILURE THIS PREVENTS", "THE DEPENDENCY THIS GUARDS"
- **Test names cited inside implementation comments**

## Docstrings

A docstring says what the thing does and what a caller must know to use it correctly. The cuts
above apply — a rejected-alternatives essay is no more useful under `"""` than beside `#`.

Three shapes worth looking for specifically:

**Module docstrings drift hardest.** They describe system-level shape — key formats, wire
contracts, invariants spanning several files — which changes without anyone reopening the file
that documents it. Check every factual claim in one against the current code. This is
routinely where the worst staleness is hiding, and fixing it is worth more than every line of
narrative you remove.

**A docstring that restates a `docs/` page will go stale for the same reason** a duplicated
comment does: no test covers it and no reader compares them. Say what the thing is in a
sentence or two and point at the doc.

**A docstring that only restates the signature earns nothing.** `"""Returns the name."""` over
`def get_name() -> str` costs a line and a maintenance obligation to say what the reader
already read. Either give it something the signature doesn't (what the name is *of*, when it
can be empty, what it raises) or delete it.

### Test docstrings

Keep only what the test **name** does not already say. If the name covers it, delete the body,
or the whole docstring.

## Missing docstrings

While you are in the file, note every function, method and class with no docstring. Add one
where it earns its place, and say which ones you deliberately left bare — the report matters
as much as the edits, because the user may hold a different line than you do.

**It earns its place when a caller could get it wrong.** Anything public; anything that
raises, mutates an argument, has an ordering or threading requirement, returns `None` where a
value looks likely, or whose name could honestly describe two different behaviours.

**It does not when the name already says it and nothing surprising happens.** A private
`_job_dir(root)` returning `root / "jobs"` gains nothing from a line repeating that. Adding one
is the same waste this skill exists to remove, wearing a different hat — and a file padded to
satisfy a coverage number reads worse than the one you started with.

**A project convention outranks this judgment.** If the repo documents every public symbol, or
requires an `Args:` block, or runs a docstring linter (`ruff` `D` rules, `pydocstyle`,
`flake8-docstrings`), follow it. Check the linter config and the surrounding files before
deciding a docstring is unnecessary — matching the neighbours matters more than being right in
the abstract.

For Python, `scripts/find_missing_docstrings.py` lists what is missing so you spend your
attention on judgment rather than on scanning:

```bash
python scripts/find_missing_docstrings.py src/            # public symbols
python scripts/find_missing_docstrings.py src/ --all      # private ones too
python scripts/find_missing_docstrings.py src/ --changed  # only files this branch touched
```

## ⚠️ flags for AI review

Keep them — they stop future reviews re-raising known issues. They follow the same discipline:
a pure description of the problem and why it is rejected. No narrative, no measurements.

## Do NOT trim

- **`docs/`** — narrative, rationale and history legitimately live there. Do still remove
  measurements: those belong in the PR that made them.
- **Error and exception messages** — user-facing, and free to explain at length.
  Not trimming them is not the same as leaving them alone: an error stating something that is
  no longer true is worse than a verbose one, because someone reads it under pressure and acts
  on it. Correct the fact and keep the length.

## Two checks that matter more than style

1. **Staleness.** Prose describing code that no longer exists is the worst offender, wherever it
   sits: comment, docstring, or the text of an error. Verify every factual claim against the
   current code and *fix* it — don't just shorten a sentence that is wrong.
   This is the highest-value part of the pass.
2. **Duplication.** Prose restating a `docs/` file goes stale *because* it is a duplicate with
   no test and no reader. Replace it with a short statement of what the code is, plus a
   pointer. Check the doc is actually correct before pointing at it.

## Finally

- Check no comment was orphaned above the wrong statement by an earlier code move.
- Run lint and the full test suite: a comments-only pass must be a no-op.
- Report, briefly:
  - net comment and docstring lines removed vs. added
  - any staleness found, and what it claimed
  - docstrings added, and which missing ones you left bare and why
