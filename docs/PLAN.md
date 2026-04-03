# Plan

### [P1] Split queue_ops.py: extract transfer operations to transfers.py

**What:** Move aria2 transfer discovery and global pause/resume from `queue_ops.py` (850 lines) into a new `transfers.py` module.
**Where:** `src/aria_queue/queue_ops.py` → `src/aria_queue/transfers.py`
**Why:** `queue_ops.py` mixes two concerns: queue CRUD (add/pause/resume/remove/retry items) and transfer management (discover what's running in aria2, global pause/resume). Splitting makes each module answer one question.
**Scope:** ~250 lines moved. No behavior change.

Move to `transfers.py`:
- `discover_active_transfer()` — polls aria2 for active downloads
- `active_status()` — alias for discover_active_transfer
- `pause_active_transfer()` — pause all active aria2 downloads
- `resume_active_transfer()` — resume all paused aria2 downloads
- `dedup_active_transfer_action()` — reads dedup preference
- `max_simultaneous_downloads()` — reads concurrency preference
- `_pref_value()` — reads any preference from declaration

Keep in `queue_ops.py`:
- `QueueItem`, `ITEM_STATUSES`, `_TERMINAL_STATUSES`
- `load_queue`, `save_queue`, `summarize_queue`
- `add_queue_item`, `pause_queue_item`, `resume_queue_item`, `remove_queue_item`, `retry_queue_item`
- `get_item_files`, `select_item_files`
- `find_queue_item_by_gid`, `_find_queue_item_by_id`
- `detect_download_mode`, `format_bytes`, `post_action`
- `_aria2_position_for_priority`, `_aria2_apply_priority`

Steps:
1. Create `transfers.py` with moved functions, import from sibling modules via `_core()` pattern
2. Update `core.py` re-export hub: add `from .transfers import *`
3. Run tests (385 must pass)
4. Commit

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
