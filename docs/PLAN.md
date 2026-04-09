# Plan

### [High] Rename ariaflow → ariaflow-server

**What:** Rename the package, CLI command, service names, Homebrew refs,
and all documentation from `ariaflow` to `ariaflow-server`.

**Why:** Disambiguate the backend server from the frontend (`ariaflow-web`).

**Preserves:**
- Python module: stays `aria_queue` (no internal rename)
- Bonjour: stays `_ariaflow._tcp` (protocol identifier, breaking to change)
- API response key `"ariaflow"` in `/api/status`: stays (coordinate with frontend later)

---

#### Step 1: Package & CLI

**Where:**
- `pyproject.toml:6` — `name = "ariaflow"` → `"ariaflow-server"`
- `pyproject.toml:41` — entry point `ariaflow =` → `ariaflow-server =`
- `pyproject.toml:32-34` — GitHub URLs → `bonomani/ariaflow-server`
- `src/aria_queue/cli.py:17` — `prog="ariaflow"` → `prog="ariaflow-server"`
**Scope:** 4 files, ~6 lines

---

#### Step 2: Service/daemon names

**Where:**
- `src/aria_queue/platform/linux.py:8` — `ariaflow-aria2.service` → `ariaflow-server-aria2.service`
- `src/aria_queue/platform/windows.py:9` — `ariaflow-aria2` → `ariaflow-server-aria2`
- `src/aria_queue/platform/launchd.py:9` — `com.ariaflow.aria2` → `com.ariaflow-server.aria2`
**Scope:** 3 files, ~3 lines

---

#### Step 3: Homebrew & CI

**Where:**
- `src/aria_queue/install.py` — `brew install ariaflow` → `brew install ariaflow-server`
- `.github/workflows/macos-install.yml` — tap/install commands
- `.github/workflows/release.yml` — formula generation
- `scripts/homebrew_formula.py` — URL and name references
**Scope:** 4 files, ~15 lines

---

#### Step 4: Documentation

**Where:**
- `README.md` — title, command examples, URLs
- `CONTRIBUTING.md` — clone URL
- `SECURITY.md` — advisory URLs
- `docs/ARCHITECTURE.md`, `docs/ALL_VARIABLES.md` — references
- `openapi.yaml` (both copies) — info/title
- `docs/governance/` — all governance docs
**Scope:** ~10 files, ~30 lines

---

#### Step 5: Tests

**Where:** All test files that reference `ariaflow` in strings
(endpoint assertions, CLI prog name, homebrew formula, lifecycle mocks).
- `tests/test_unit.py`, `test_api.py`, `test_cli.py`, `test_web.py`,
  `test_scenarios.py`, `test_homebrew_formula.py`, `test_platform.py`
**Scope:** ~7 files, ~50 lines
**Approach:** Global find-replace `"ariaflow"` → `"ariaflow-server"` in
test strings, then manually verify each change (some should stay, e.g.
`_ariaflow._tcp`, `aria_queue` module name, `"ariaflow"` API key).

---

#### Step 6: Scripts

**Where:**
- `scripts/publish.py:13` — `REPO = "bonomani/ariaflow"`
- `scripts/homebrew_formula.py` — all references
**Scope:** 2 files, ~5 lines

---

#### Step 7: Cleanup

- Delete `src/ariaflow.egg-info/` if present (will regenerate)
- Run `pip install -e .` to regenerate
- `python -m pytest tests/ -x -q` — full pass
- Remove `docs/GAPS-RENAME.md` (done)

---

**Execution order:** 1 → 2 → 3 → 4 → 5 → 6 → 7 (single commit for atomicity)
**Total scope:** ~25 files, ~110 lines changed
**Risk:** Homebrew tap needs coordinated update. PyPI is a new package name.
Existing `pip install ariaflow` installs will not auto-upgrade.

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
