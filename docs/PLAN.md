# Plan

No open items.

---

## How to use this file

This is the **single plan file** for the project. Do not create separate plan files.

### Rules

1. **One plan file.** All planned work goes here. No `BUGFIX_PLAN.md`, `REFACTOR_PLAN.md`, etc.
2. **Done → remove.** When an item is completed, delete it from this file. Git history has the record.
3. **Declined → keep briefly.** If an item was evaluated and rejected, keep a one-liner with the reason. This prevents re-proposing the same idea.
4. **Empty → keep the file.** Even with no open items, keep this file with the instructions.
5. **Prioritize.** Items are ordered by priority. Top = do first.
6. **Be concrete.** Each item has: what to change, where in the code, why, and estimated scope.
7. **Checkpoint after each item.** Run tests, commit, update docs.
8. **No stale plans.** If a plan item has been open for more than 2 sessions without progress, re-evaluate it — either do it or decline it.

### Item template

```
### [Priority] Short title

**What:** Description of the change
**Where:** File(s) and function(s) affected
**Why:** Problem it solves or value it adds
**Scope:** Estimated lines changed / files touched
**Depends on:** Other items that must be done first (if any)
```

---

## Declined

_Items evaluated and rejected. Kept to prevent re-proposing._

- **Remove `stopped` status** — `stopped` (system decided) vs `cancelled` (user decided) is a useful distinction. Merging them loses information.
