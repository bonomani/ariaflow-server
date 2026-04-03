# Improvement Plan — Remaining Work

**Completed:** Phase A (defensive fixes), Phase B (hybrid queue migration), Phase B+ (priority delegation to aria2).

All 6 hybrid design principles are implemented. No code changes are planned.

---

## Phase C — Cleanup (evaluate, no commitment)

These are optional improvements. Evaluate when stable.

### C1: Consider removing `stopped` status

`stopped` only occurs when aria2 reports `removed`. Could map to `cancelled` instead. Would reduce states from 9 to 8.

**Decision:** Not planned. Evaluate if `stopped` still occurs in practice.

### C2: Consider renaming `downloading` to `active`

Matches aria2 vocabulary. Breaking API change — needs versioning.

**Decision:** Not planned. Breaking change, low value.

---

## Phase D — BGS compliance (docs only, no code)

### Issue #13: TIC oracle — add missing test trace targets

`tic-oracle.md` documents 330 tests, `pytest` finds 374+. Add missing trace targets.

### Issue #14: bgs-decision.yaml — update stale limitation counts

Update "33 test-to-trace-target mappings" to reflect actual coverage.

### Checkpoint D

```
  □ pytest -x                          final pass
  □ python scripts/gen_rpc_docs.py     final regeneration
  □ git commit "Update BGS compliance docs"
  □ full BGS §2.9 re-check
  □ review all docs/ for consistency
```
