# Plan

### [A1] Add `allowed_actions` to each item in status response

**What:** Compute and include `allowed_actions` list for each queue item based on its current status.
**Where:** `src/aria_queue/queue_ops.py` (new helper), `src/aria_queue/webapp.py` (status response)
**Why:** Frontend currently hardcodes which buttons to show per status. Backend should be authoritative.
**Scope:** ~20 lines

Rules:
- `queued`: pause, remove
- `waiting`: pause, remove
- `active`: pause, remove
- `paused`: resume, remove
- `complete`: remove
- `error`: retry, remove
- `stopped`: retry, remove
- `cancelled`: (none)

### [A2] Scheduler auto-retry with policy

**What:** Scheduler automatically retries failed items up to `max_retries` times with configurable backoff.
**Where:** `src/aria_queue/scheduler.py` (_poll_tracked_jobs), `src/aria_queue/contracts.py` (new preferences)
**Why:** Currently retry is manual only. Transient errors (network, aria2 restart) should auto-recover.
**Scope:** ~40 lines

New preferences:
- `max_retries`: default 3 (0 = no auto-retry)
- `retry_backoff_seconds`: default 30

New item fields:
- `retry_count`: incremented on each auto-retry
- `next_retry_at`: timestamp for backoff

Logic in scheduler:
- When _poll_tracked_jobs marks an item as `error`
- If `retry_count < max_retries` AND error is not `rpc_unreachable`
- Set `next_retry_at = now + retry_backoff_seconds * (retry_count + 1)`
- On next tick, if `status == error` AND `now >= next_retry_at`: auto-retry (same as manual retry + re-submit)
- User manual retry always works regardless of retry_count

### [A3] aria2 max-tries passthrough

**What:** Set aria2's `--max-tries` and `--retry-wait` on add_download to handle transient network errors at aria2 level.
**Where:** `src/aria_queue/aria2_rpc.py` (add_download options), `src/aria_queue/contracts.py` (preferences)
**Why:** aria2 handles connection resets and timeouts internally — no need for scheduler to see them as errors.
**Scope:** ~10 lines

New preferences:
- `aria2_max_tries`: default 5
- `aria2_retry_wait`: default 10 (seconds)

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
