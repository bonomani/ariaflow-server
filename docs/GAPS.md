# ariaflow-server — Feature Gap Analysis (Backend)

Reference: [webui-aria2](https://github.com/ziahamza/webui-aria2)

For frontend-only items, see `../ariaflow-web/GAPS.md`.

## Status Summary

| # | Feature | Value | Status |
|---|---|---|---|
| 2.3 | Per-item action API | high | done |
| 3.1 | Torrent/metalink file selection | medium | done |
| 3.2 | DirectURL / file serving | medium | deferred |
| 4.1 | aria2 global options proxy | low-medium | done (safe subset) |
| 5.2 | Docker image | medium | done |

## Implemented

### 2.3 Per-item action API

Per-item endpoints: `POST /api/downloads/<id>/pause`, `resume`, `remove`, `retry`. Each validates state, logs to `actions.jsonl`, and triggers SSE events.

### 3.1 Torrent/metalink file selection

Supports `.torrent`, `.metalink`, magnet URLs with `--pause-metadata=true`. File picker via `GET /api/downloads/<id>/files` and selection via `POST /api/downloads/<id>/files` with `{select: [1,3,5]}`.

### 4.1 aria2 global options proxy

`POST /api/aria2/change_global_option` with 3-tier safety: managed options (download/upload limits, seed) blocked from generic API, safe options (concurrency, split, timeout) allowed, unsafe options require `aria2_unsafe_options` preference. Logs changes.

### 5.2 Docker image

Dockerfile installs aria2 + ariaflow-server + ariaflow-web. Exposes ports 8000/8001. Volume mount for downloads/config.

## Remaining

### 3.2 DirectURL / file serving — deferred

Completed files sit in aria2's download directory with no API to serve them. **Recommendation:** document how to point a static file server (nginx, caddy) at the download directory (zero code). Add `GET /api/files` later if demand exists.

---

## Internal gaps

### G-1 Config migration has no logging — low

`storage.py:config_dir()` auto-renames `~/.config/aria-queue/` → `~/.config/ariaflow-server/` but logs nothing. If rename fails (permissions, disk), user gets a silent fallback to the wrong dir. **Fix:** log the migration or raise on failure.

### G-2 No test for config dir migration — low

The old→new dir rename in `storage.py` has no dedicated test. Currently relies on all tests using `ARIAFLOW_DIR` env var which bypasses the migration path entirely.

### G-3 `is_nated()` only covers WSL2 — low

Docker, VMs, and other NAT environments return `False`. Acceptable for now but limits usefulness of the function. Could check for `172.x/10.x` private IPs with no route to LAN peers.

### G-4 No runtime warning when Bonjour unavailable — low

Peer discovery is silently disabled. A log message or `/api/status` field indicating "discovery: unavailable" would help debugging.

### G-5 Write boundary hook uses hardcoded path — medium

`.claude/settings.json` PreToolUse hook hardcodes `/home/bc/repos/github/bonomani/ariaflow-server`. Breaks if repo cloned elsewhere. **Fix:** use `git rev-parse --show-toplevel`.

### G-6 No TIC registration hook — medium

Commit hook checks "src/ changed → tests/ must change" but not "tests/ changed → tic-oracle.md must change". `scripts/check_tic_coverage.py` catches this in CI but not at commit time.

### G-7 TIC oracle numbering uses sub-IDs — low

Entries like `22a`, `232b`, `428a` create ambiguity. Should be renumbered sequentially on next major TIC update.

### G-8 BGS version refs may be stale — medium

`bgs@58c1467` and all member refs pinned to a specific SHA. If BGS upstream has evolved, these should be updated and re-validated with `check-bgs-compliance.py`.

### G-9 README missing Windows/WSL setup — medium

No documentation for: Bonjour requirement on Windows (iTunes/SDK), WSL2 mirrored networking for LAN discovery, `ARIAFLOW_DIR` env var.

### G-10 No CHANGELOG or migration guide — low

Users upgrading from pre-rename versions (`aria-queue` config dir, `ARIA_QUEUE_DIR` env var, `ariaflow` API keys) have no migration guide. The auto-migration handles config dir, but API key changes are breaking.

### G-11 Release workflow Python version mismatch — low

CI tests with Python 3.12, Homebrew formula installs system Python (3.14 on macOS). No test coverage on 3.14.

### G-12 PLAN.md Declined section references old service type — trivial

"Single `_ariaflow-server._tcp` service" in the Declined section — this is now the current name, not a declined alternative. Text is confusing.

## Cross-project gaps

Backend gaps reported by the frontend are tracked in `docs/BACKEND_GAPS_REQUESTED_BY_FRONTEND.md`
(written by the frontend agent per the cross-repo boundary rules).

Current status:

| ID | Gap | Status |
|---|---|---|
| BG-1 | SSE pushes rev-only | Done (SSE now pushes full payload) |
| BG-2 | No PATCH for declaration preferences | Done (`PATCH /api/declaration/preferences` added) |
| BG-3 | openapi.yaml lacks response field schemas | Done (openapi_schemas.py + gen_openapi.py) |
| BG-4 | openapi.yaml info.version is hardcoded | Done (gen_openapi.py injects `__version__`) |
| BG-5 | Bonjour instance name should be the short hostname | Done (`bonjour.py` `_short_hostname` + `_instance_name`) |
| BG-6 | Bonjour TXT records need a `hostname` key | Done (`hostname=<short>` added to dns-sd/avahi cmds) |
| BG-7 | SSE push for action_log entries (drop `/api/log` polling) | Done (`append_action_log` publishes `action_logged` event) |
| BG-8 | Merge `/api/health` into `/api/status` (drop `_heroTimer` polling) | Done (`/api/status` carries a `health` object) |
| BG-9 | Scheduler backoff when aria2 unreachable | Done (exponential 2s→60s in `process_queue`) |
| BG-10 | Under-specified response schemas in openapi.yaml (9 endpoints) | Done (typed nested schemas + reusable UccEnvelope component + 5 TIC pinning tests) |
| BG-11 | Residual under-specified fields after BG-10 (14 fields, 5 endpoints) | Done (8 backend-side via Aria2Health/AriaflowHealth/ActiveTransfer/extended QueueItem; 6 dropped from frontend schemas after frontend agent verified they were never read) |
