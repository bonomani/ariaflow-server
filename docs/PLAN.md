# Plan

### [Medium] BG-13: Detect WSL and default download dir to Windows filesystem

**What:** When running on WSL, default aria2's download directory to
`/mnt/c/Users/<windows-user>/Downloads` so files are accessible from
Windows Explorer natively.

**Why:** On WSL2, `~/Downloads` is on the Linux ext4 filesystem — slow
via `\\wsl$\` and invisible to most Windows apps.

**Where / steps:**

1. `src/aria_queue/platform/detect.py` — add `is_wsl() -> bool`:
   check if `/proc/version` contains `microsoft` (case-insensitive).
   Also add `wsl_windows_downloads() -> Path | None`: resolve the
   Windows Downloads folder via `/mnt/c/Users/<user>/Downloads`
   (use `wslvar USERPROFILE` or fall back to `$USER`).
   **Scope:** ~20 lines

2. `src/aria_queue/platform/linux.py:84` — in `install_aria2_systemd()`,
   replace `Path.home() / "Downloads"` with a call that checks
   `is_wsl()` first and uses `wsl_windows_downloads()` if available.
   Same change in `_build_unit()`.
   **Scope:** ~5 lines changed

3. `tests/test_platform.py` — add tests for `is_wsl()` with mocked
   `/proc/version` content, and `wsl_windows_downloads()` with mocked
   subprocess.
   **Scope:** ~30 lines

**Verify:** `python -m pytest tests/test_platform.py -x -q`

---

### [Low] BG-14: Expose `archivable_count` in status summary

**What:** Add `archivable_count` to the `summary` object in
`GET /api/status` so the frontend knows whether the Archive button
should be enabled.

**Why:** The frontend enables Archive when `sumDone > 0 || sumError > 0`,
but `POST /api/downloads/cleanup` applies age/count thresholds. Users
click Archive and see "0 archived" — confusing. Blocks FE-20.

**Where / steps:**

1. `src/aria_queue/state.py` — extract the archivability check from
   `auto_cleanup_queue()` into a pure function
   `count_archivable(items, max_done_age_hours=168) -> int` that counts
   items matching: status in `{complete, error, failed, stopped, removed}`
   AND (`completed_at` or `error_at` or `created_at`) older than
   `max_done_age_hours` (default 168 = 7 days).
   **Scope:** ~20 lines

2. `src/aria_queue/core.py` — re-export `count_archivable` via
   `from .state import *`.
   **Scope:** 0 lines (wildcard)

3. `src/aria_queue/webapp.py:283` — in `_status_payload()`, after
   `summarize_queue(items)`, add:
   ```python
   summary["archivable_count"] = count_archivable(items)
   ```
   **Scope:** 2 lines

4. `src/aria_queue/openapi.yaml` + `src/aria_queue/openapi_schemas.py` —
   add `archivable_count: {type: integer}` to the status summary schema.
   **Scope:** ~3 lines each

5. `tests/` — add a test that verifies `archivable_count` appears in
   status response and is 0 when no items qualify.
   **Scope:** ~15 lines

**Verify:** `python -m pytest tests/ -x -q`

---

Deferred (informational only):
- `check_declaration_drift.py` reports 23 prefs missing from the *user's local* `~/.config/aria-queue/declaration.json`. Not a repo issue — per-machine state. The existing `|| true` in the Makefile is correct.

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
- **Per-torrent Bonjour advertisement** — Replaced by API-based discovery (`GET /api/torrents`). Single `_ariaflow._tcp` service is simpler and Apple-compliant.
- **Scheduler start/stop API** — Scheduler now auto-starts with `ariaflow serve`. Users can only pause/resume. Simpler state model.
