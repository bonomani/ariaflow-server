# Naming Gaps — ariaflow vs aria2

Variables and statuses derived from aria2 should keep names consistent with aria2's vocabulary. This document maps the gaps.

## Status Name Mapping

| aria2 status | ariaflow status | Match? | Notes |
|---|---|---|---|
| `active` | `downloading` | **Mismatch** | aria2 calls it `active`, ariaflow calls it `downloading` |
| `waiting` | `waiting` | OK | |
| `paused` | `paused` | OK | |
| `complete` | `done` | **Mismatch** | aria2 calls it `complete`, ariaflow calls it `done` |
| `error` | `error` | OK | |
| `removed` | `stopped` | **Mismatch** | aria2 calls it `removed`, ariaflow calls it `stopped` |

### ariaflow-only statuses (no aria2 equivalent)

| ariaflow status | Purpose |
|---|---|
| `discovering` | Pre-submission mode detection (ariaflow concept) |
| `queued` | Safety-net fallback when aria2 unreachable (ariaflow concept) |
| `cancelled` | User-initiated removal with archive (ariaflow concept) |

## Field Name Mapping

| aria2 field | ariaflow field | Match? | Notes |
|---|---|---|---|
| `gid` | `gid` | OK | |
| `status` | `status` / `live_status` | **Split** | ariaflow stores its own `status` (mapped) and `live_status` (raw aria2 value) |
| `downloadSpeed` | `downloadSpeed` | OK | Stored as-is from aria2 |
| `completedLength` | `completedLength` | OK | Stored as-is from aria2 |
| `totalLength` | `totalLength` | OK | Stored as-is from aria2 |
| `errorCode` | `error_code` | **Mismatch** | aria2 uses camelCase, ariaflow uses snake_case |
| `errorMessage` | `error_message` | **Mismatch** | aria2 uses camelCase, ariaflow uses snake_case |
| `files` | `files` | OK | |

## Function Name Mapping

All 36 `aria2_*` wrapper functions use consistent `aria2_` + snake_case naming. These are 1:1 with aria2 RPC methods. **No gaps.**

## Summary of Mismatches

| Category | aria2 name | ariaflow name | Breaking to fix? | Recommendation |
|---|---|---|---|---|
| Status: active | `active` | `downloading` | Yes — API contract | **Align** in next major version |
| Status: complete | `complete` | `done` | Yes — API contract | **Align** in next major version |
| Status: removed | `removed` | `stopped` | Yes — API contract | **Keep** — ariaflow adds semantic meaning (`stopped` = system, `cancelled` = user) |
| Field: errorCode | `errorCode` | `error_code` | Yes — API contract | **Keep** — ariaflow follows Python snake_case convention |
| Field: errorMessage | `errorMessage` | `error_message` | Yes — API contract | **Keep** — same reason |
| Field: live_status | _(none)_ | `live_status` | No | **Keep** — stores raw aria2 status alongside mapped ariaflow status |

## Recommended Actions

### Do now (no breaking change)

None. All mismatches require API contract changes.

### Do in next major version

1. **Rename `downloading` → `active`** — matches aria2 vocabulary, 42 code+test references
2. **Rename `done` → `complete`** — matches aria2 vocabulary, similar scope

### Keep as-is (justified divergence)

1. **`stopped` vs `removed`** — ariaflow distinguishes `stopped` (system decided) from `cancelled` (user decided). aria2's `removed` doesn't carry this distinction.
2. **`error_code` vs `errorCode`** — ariaflow follows Python snake_case. The raw aria2 camelCase values are accessible via `live_status` and direct RPC calls.
3. **`live_status` field** — ariaflow-specific concept. Stores the raw aria2 status for cases where the mapped ariaflow status diverges.
