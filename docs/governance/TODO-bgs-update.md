# BGS Evidence Update Instructions

These artifacts need manual updates to reflect code changes since 2026-04-01.

## 4. ASM State Model (`docs/governance/asm-state-model.md`)

Update Axis 3 (Job) to match the current state machine in `core.py`:

**Remove these states** (no longer in code):
- `pending` — removed, items start as `queued`
- `complete` — merged into `done`
- `failed` — merged into `error`
- `skipped` — removed
- `removed` — replaced by `cancelled`

**Add these states:**
- `discovering` — transitional — auto-detecting download mode (instant)
- `cancelled` — terminal — cancelled by user, archived

**Update transitions:**
```
discovering → queued        mode detected (synchronous)
queued → downloading        af-scheduler picks job (priority order)
downloading → done          aria2 reports success
downloading → error         aria2 reports failure
downloading → stopped       af-scheduler shutdown or GID removed
downloading → paused        user pause command
paused → queued             user resume (no gid)
paused → downloading        user resume (with gid)
error → queued              user retry (clears recovery fields)
Any → cancelled             user remove (soft-deleted to archive)
```

**Update derived states:**
- `engine_ready` → `scheduler_ready`
- `engine_active` → `scheduler_active`
- `engine_draining` → `scheduler_draining`

**Add download modes section:**
```
Modes: http, magnet, torrent, metalink, mirror, torrent_data, metalink_data
```

## 5. BISS Classification (`docs/governance/biss-classification.md`)

Add these new boundaries to the inventory table:

| Boundary | Type | Direction | Classification | Notes |
|---|---|---|---|---|
| SSE events | system-to-user | outbound | real-time state push | Server-Sent Events at /api/events |
| Archive store | system-to-storage | internal | soft-delete persistence | archive.json for cancelled/old items |
| Session history | system-to-storage | internal | audit persistence | sessions.jsonl for session log |
| OpenAPI/Swagger | system-to-user | outbound | documentation | /api/docs and /api/openapi.yaml |

## 6. TIC Oracle (`docs/governance/tic-oracle.md`)

The oracle currently maps 30 tests. The project now has 330 tests across 10 files.
Key new test areas to map:

**Per-item actions (10 tests in TicPerItemTests):**
- pause/resume/remove/retry with state validation
- Trace: ASM Job axis transitions, UCC execution

**Download modes (9 tests in TicTorrentAndOptionsTests):**
- Torrent metadata detection, file selection, aria2 options
- Trace: UCC execution modes

**API integration (77 tests in test_api.py):**
- Every endpoint tested with success and error cases
- Trace: UCC contract shape, UIC gate validation

**Cross-checks (51 tests in test_cross_check.py):**
- Every mutation verified against read endpoints
- Trace: UCC observation/outcome consistency

**Scenarios (16 tests in test_scenarios.py):**
- End-to-end workflows: download lifecycle, pause/resume, error/retry
- Trace: ASM full lifecycle, UIC preflight gates

**Regression tests (29 tests in test_regressions.py):**
- One test per bug fixed, plus security input validation
- Trace: ASM coherence rules, UCC execution safety

**CLI tests (25 tests in test_cli.py):**
- Every subcommand parser + execution
- Trace: UCC CLI interface contract

Recommended approach: update the oracle with test class summaries rather than
mapping all 330 individually. Group by trace target (ASM axis, UIC gate, UCC
execution) and reference the test file + class.
