# BGS Suite Adoption — Gap Analysis

Date: 2026-04-07
BGS suite analyzed: `../BGSPrivate` @ `58c1467`
Target slice: `BGS-State-Modeled-Governed-Verified`
Authoritative validator: `../BGSPrivate/bgs/tools/check-bgs-compliance.py`
Schema: `../BGSPrivate/bgs/schemas/decision-record.schema.json`

This file lists every divergence between ariaflow's current governance
artifacts and what the new BGS suite expects. Each gap is independently
actionable.

---

## G1 — Member layout changed: monorepo, not sibling repos

**Severity:** blocker — validator fails at every member ref.

`docs/governance/bgs-decision.yaml` pins member versions as if each
framework lived in its own sibling repo:

```yaml
member_version_refs:
  ucc: ucc@370c1f7
  uic: uic@11bd400
  asm: asm@dca032b
  tic: tic@7cfba80
```

In the new layout, BGSPrivate is a **single git repo** containing
`bgs/`, `ucc/`, `uic/`, `asm/`, `tic/` as subfolders. None of the
subfolders has a `.git` directory, so the validator's
`git rev-parse <ref>` lookup against `member_repos_root/<name>` cannot
resolve any of these refs.

**Resolution options (decision needed):**
- (A) Pin every member to the BGSPrivate repo SHA (e.g.
  `ucc: bgs@58c1467`, … all four). Simplest, reflects monorepo reality.
- (B) Wait for upstream to expose per-member refs another way and
  document the workaround in `limitations:` until then.

`scripts/check_bgs_drift.py` already maps every member to the same
`../BGSPrivate` directory (since it now points there for `bgs`). The
`_MEMBER_REPOS` mapping (lines 19–25) needs to be updated to point all
five members at `BGSPrivate` and the per-member git verification logic
re-checked, otherwise local drift detection drifts from upstream.

---

## G2 — Entry file `decision_record_path` is project-relative, not entry-relative

**Severity:** blocker — validator FAIL.

`docs/governance/BGS.md:11`:

```yaml
decision_record_path: "./docs/governance/bgs-decision.yaml"
```

The validator (`check-bgs-compliance.py:346`) resolves
`decision_record_path` relative to the entry file's parent directory,
not the project root. With the entry at `docs/governance/BGS.md`, the
validator looks for `docs/governance/docs/governance/bgs-decision.yaml`
and reports `decision record not found`.

**Fix:** change to `./bgs-decision.yaml` (sibling of BGS.md). All
internal `read_next:` paths in `BGS.md` should be re-checked the same
way — they are currently written project-relative as well.

---

## G3 — Evidence refs are project-relative, not decision-relative

**Severity:** blocker — every `evidence_refs` entry FAILs validation.

`bgs-decision.yaml:34-40` lists evidence with project-root paths
(`./docs/governance/biss-classification.md`, `./tests/`, etc.). The
validator resolves them relative to the decision file's directory,
which produces `docs/governance/docs/governance/...` for every entry.

**Fix:** rewrite each path relative to `docs/governance/`:

```yaml
evidence_refs:
  - ./biss-classification.md
  - ./asm-state-model.md
  - ./tic-oracle.md
  - ../../src/aria_queue/contracts.py
  - ../ARCHITECTURE.md
  - ../../tests/
```

---

## G4 — `bgs_version_ref` is the only ref that points at the suite

After G1 is resolved (option A), `bgs_version_ref: bgs@58c1467` is
correct in shape but redundant with member refs that all share the same
SHA. Document the chosen pinning convention either in the decision file
or in `BGS.md` so future updates don't drift one without the other.

---

## G5 — `external_controls` key casing is fragile

**Severity:** soft — currently passes (validator normalizes to lower).

`bgs-decision.yaml:28` uses `IAM_and_authorization` (mixed case). The
schema (`decision-record.schema.json`) declares the canonical key as
`iam_and_authorization`. The validator passes today because
`normalize_control_key()` lowercases keys before checking, but the
schema check will fail under any stricter validator (e.g. a generic
JSON-schema runner).

**Fix:** rename to lowercase to match the schema and `BGS.md` should be
updated identically (it has the same casing in line 24).

---

## G6 — `members_used` lists BISS but no `biss` ref is pinned

**Severity:** soft — schema does not currently require it.

`members_used` includes `BISS`, but `member_version_refs` has no `biss`
key. Since BISS lives inside the same monorepo as everything else
(after G1), add `biss: bgs@58c1467` for completeness so audits don't
have to infer it.

---

## G7 — Drift checker (`scripts/check_bgs_drift.py`) is unaware of the new validator

**Severity:** medium — local check passes while upstream check fails.

`scripts/check_bgs_drift.py` validates slice membership and member
presence but does not invoke `check-bgs-compliance.py`. With G1–G3
unresolved, ariaflow's `make check-drift` reports `BGS clean` while the
upstream validator FAILs ten times.

**Fix:** after G1–G3, extend `check_bgs_drift.py` to also shell out to
`../BGSPrivate/bgs/tools/check-bgs-compliance.py docs/governance/BGS.md
--member-repos-root ../BGSPrivate` and surface its exit code. Wire it
into the `check-drift` Make target so divergence is caught locally.

---

## G8 — Optional Grade-2 fields not declared

**Severity:** informational only.

The new schema accepts (but does not require) the additive G2 fields:
`profiles[]`, `policies[]`, `profiles_used`, `depends_on_decisions`. See
`bgs/BGS-EXTENSION-MODEL.md`. Ariaflow declares none. No action needed
unless we adopt a typed profile (e.g. an ariaflow-specific runtime
profile or a rate-limit policy reference).

---

## G9 — `last_reviewed: 2026-04-05` will go stale

**Severity:** informational.

The validator's `check_staleness` reads `last_reviewed` from the entry
file. The default `--max-staleness` is enforced when present. After
making the G1–G3 fixes, bump `last_reviewed` in `BGS.md` to today's
date (2026-04-07) and add a reminder rule (CI or cron) to keep it
current.

---

## Suggested fix order

1. G2 + G3 — pure path fixes, unblock the validator. (5 min)
2. G1 — agree on monorepo pinning convention, update both
   `bgs-decision.yaml` and `scripts/check_bgs_drift.py`. (30 min)
3. G5 + G6 — schema-alignment cleanup. (5 min)
4. G7 — wire upstream validator into `make check-drift`. (15 min)
5. G9 — bump `last_reviewed`.
6. G4, G8 — document or defer.
