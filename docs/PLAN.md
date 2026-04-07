# Plan

## Open items

Source: coherence analysis 2026-04-07 (governance ↔ code, governance ↔ governance, ASM rules ↔ enforcement).

### [P1] Enforce ASM CR-3 at the scheduler crash path

**What:** CR-3 (`job=active ⇒ run=running`) is currently a structural property of `process_queue()`, with one real runtime gap: when the scheduler thread crashes, `scheduler.py:55-60` flips `running=False` and clears `active_gid` but does *not* tell aria2 to stop transferring. Aria2 keeps downloading orphaned jobs until the next scheduler start. Pause aria2 inside the crash handler so the transition out of `running` is matched by an actual stop in the source of truth, not just the mirror.

**Where:**
- `src/aria_queue/scheduler.py:51-60` — wrap the existing `except Exception` block with a best-effort `core.aria2_pause_all(port=port, timeout=5)` call before writing `running=False`. Swallow any error from the pause (the daemon may itself be dead).
- `src/aria_queue/scheduler.py:67-70` — add a `# ASM CR-3` marker at `process_queue()` documenting that this is the sole path that enters `running=True`, so structural enforcement holds for the normal flow.
- `docs/governance/asm-state-model.md` (§4) — append one paragraph: "CR-3 is enforced at two points: structurally by `process_queue()` (the sole entry into `run=running` and the sole submission path into the active tier), and explicitly by the scheduler crash handler, which pauses aria2 before writing `run=False`."

**Why:** This is the only CR-N rule still missing explicit enforcement after the previous round. The fix is at the **right layer** (aria2 itself, not ariaflow's mirror) and at the **single chokepoint** (the only place `running` is set to `False`). It is the symmetric mate of the CR-4 fix already merged. Currently, a scheduler crash leaves orphaned aria2 transfers running until the next start — a foot-gun independent of governance.

**Scope:** ~6 lines of code in `scheduler.py`, ~5 lines of doc in `asm-state-model.md`. No new imports (`aria2_pause_all` already exists at `aria2_rpc.py:133`). One file for code, one file for doc.

**Verify:**
- `python -m pytest tests/ -x -q` — all 481 tests pass; the crash path is rarely exercised so risk is minimal, and the `try/except` around `aria2_pause_all` keeps tests with no aria2 daemon green.
- `python scripts/check_bgs_drift.py` — clean (upstream validator still PASS).
- Spot-check that `pause_active_transfer` (`transfers.py:119`) is untouched — it already calls `aria2_pause` per gid and is CR-3-correct.

**Out of scope (deliberate):**
- No guard inside `save_queue()` — would censor the mirror, not the cause.
- No guard at submission sites — aria2 controls when a request becomes active, not ariaflow.
- No new "scheduler stop" endpoint. If one is added later, the new code path must call `aria2_pause_all` itself; the model-doc paragraph flags this requirement for future contributors.

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
