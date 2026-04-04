# Codebase Audit — ariaflow

Updated: 2026-04-03. Basis: 385 tests, 9 modules, 5317 source lines.

---

## Completed

| Phase | What was done |
|---|---|
| P1 Security | URL/path/ID validation, error masking |
| P2 Performance | aria2_multicall batching (10x RPC reduction) |
| P3 API consistency | Standardized error format via _error_payload, fixed status codes |
| P4 Correctness | Silent exceptions reviewed — all intentional best-effort patterns |
| P5 Observability | /api/health endpoint |
| P6 Dead code | Removed format_bytes, INDEX_HTML, DOWNLOAD_MODES |
| P8 DevEx | Makefile |
| Naming | 11 automated convention tests, NAMING_GAPS.md removed (enforced by code) |

## Remaining — Ordered by effort/value

### R4: OpenAPI spec version sync — 1 min

`src/aria_queue/openapi.yaml` line 7 says `version: 0.1.38`, pyproject.toml says `0.1.98`.
**Fix:** Update 1 line.

### R6: CONTRIBUTING.md — 20 min

Does not exist. Should cover: dev setup, `make test`, `make check`, code style, commit conventions, release process, docs.
**Fix:** Write ~60 lines.

### R7: Pre-commit hooks — 20 min

No `.pre-commit-config.yaml`. Should include: ruff (lint+format), trailing whitespace, YAML/JSON check.
**Fix:** Write ~30 lines, test with `pre-commit run --all-files`.

### R5: CI matrix — 30 min

Current: Ubuntu + Python 3.12 only. Missing: Python 3.10, 3.11; Windows.
**Fix:** Add matrix strategy to release.yml (~50 lines YAML).

### R2: Unit test coverage — 6 hours

35 public functions have zero direct test references:

| Module | Untested functions | Effort |
|---|---|---|
| storage.py | 11 (path helpers, JSON I/O) | Quick — 5 min each |
| state.py | 11 (session, archive, action log) | Medium — 15 min each |
| queue_ops.py | 3 (detect_download_mode, find_by_gid, summarize) | Quick |
| contracts.py | 2 (declaration_path, ensure_declaration) | Quick |
| install.py | 3 (version, ucc_envelope, ucc_record) | Quick |
| bonjour.py | 2 (bonjour_available, advertise) | Medium |
| scheduler.py | 1 (stop_background_process) | Complex |
| aria2_rpc.py | 7 (6 new aria2_set_* + aria2_current_bandwidth) | Quick |
| transfers.py | 1 (pause_active_transfer) | Complex |

Quick (21 functions × 5 min): 1h45m
Medium (10 × 15 min): 2h30m
Complex (4 × 30 min): 2h

**Total: ~6h15m**

## Not needed (evaluated and closed)

- **R1 (Silent exceptions):** All 50 instances reviewed — intentional best-effort fallbacks for RPC, bonjour, optional features.
- **R3 (TIC oracle stale names):** Re-audited — no stale names found. Document uses correct status names.
