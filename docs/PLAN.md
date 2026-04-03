# Plan

### [R4] OpenAPI spec version sync — 1 min

**What:** Update version in openapi.yaml to match pyproject.toml
**Where:** `src/aria_queue/openapi.yaml` line 7
**Why:** `0.1.38` vs current `0.1.98`
**Scope:** 1 line

### [R6] CONTRIBUTING.md — 20 min

**What:** Write contributor guide
**Where:** `CONTRIBUTING.md` (root)
**Why:** No onboarding doc for new developers
**Scope:** ~60 lines

### [R7] Pre-commit hooks — 20 min

**What:** Add `.pre-commit-config.yaml` with ruff + basic checks
**Where:** `.pre-commit-config.yaml` (root)
**Why:** No automated code quality checks before commit
**Scope:** ~30 lines

### [R5] CI matrix — 30 min

**What:** Add Python 3.10/3.11 and Windows to CI
**Where:** `.github/workflows/release.yml`
**Why:** Only tests Python 3.12 on Ubuntu
**Scope:** ~50 lines YAML

### [R2] Unit test coverage — 6h

**What:** Add direct unit tests for 35 untested public functions
**Where:** `tests/` (new test files)
**Why:** Functions tested only indirectly — changes may not be caught
**Scope:** ~400 lines across multiple test files
**Depends on:** R4-R7 done first (clean baseline)

---

## How to use this file

This is the **single plan file** for the project. Do not create separate plan files.

### Rules

0. **Task 0: clean git before starting.** Before executing any plan item, verify `git status` is clean (no uncommitted changes, no untracked files except `.claude/`). Show the output as evidence. If not clean, commit or stash first. Never start work on a dirty tree.
1. **One plan file.** All planned work goes here. No `BUGFIX_PLAN.md`, `REFACTOR_PLAN.md`, etc.
2. **Done → remove.** When an item is completed, delete it from this file. Git history has the record.
3. **Declined → keep briefly.** If an item was evaluated and rejected, keep a one-liner with the reason. This prevents re-proposing the same idea.
4. **Empty → keep the file.** Even with no open items, keep this file with the instructions.
5. **Prioritize.** Items are ordered by priority. Top = do first.
6. **Be concrete.** Each item has: what to change, where in the code, why, and estimated scope.
7. **Checkpoint after each item.** Run tests, commit, update docs.
8. **No stale plans.** If a plan item has been open for more than 2 sessions without progress, re-evaluate it — either do it or decline it.

### Execution workflow

Before starting:
```
□ git status                    # must be clean
□ git pull --rebase origin main # start from latest
□ python -m pytest tests/ -x -q # all tests pass
```

For each plan item:
```
□ read the plan item
□ read the code to change
□ implement the change (smallest diff possible)
□ python -m pytest tests/ -x -q # all tests pass
□ update docs if affected
□ git add <specific files>      # no git add -A
□ git commit                    # descriptive message
□ remove the item from PLAN.md
□ git add docs/PLAN.md
□ git commit "Update plan"
□ git push origin main          # if rejected: pull --rebase, re-test, push
```

After all items done:
```
□ python -m pytest tests/ -x -q # final pass
□ python scripts/gen_rpc_docs.py # regenerate if code changed
□ python scripts/gen_all_variables.py --check # naming compliance
□ verify PLAN.md says "No open items"
□ git push origin main
□ rm -rf .claude/worktrees/     # clean temp working folders
□ git status                    # confirm clean tree
```

### What NOT to do

- Don't start coding without checking `git status` first
- Don't batch multiple plan items into one commit
- Don't use `git add -A` (risk of committing secrets or generated files)
- Don't skip tests between items
- Don't leave uncommitted changes when stopping work
- Don't create plan files other than this one
- Don't `git checkout` or `git reset --hard` without understanding what will be lost (uncommitted work is gone forever)
- Don't modify code you haven't read first

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
