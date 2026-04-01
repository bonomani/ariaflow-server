# TIC Oracle — Ariaflow

Profile: ariaflow-engine
TIC ref: tic@7cfba80
Test file: `tests/test_tic.py`

## Test Inventory

### Session lifecycle (ASM Axis 1)

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_enqueue_creates_queue_item` | Adding a URL opens a session and creates a queued job | item.status == "queued", session_started_at set, action log contains "add" with session_id | ASM: none→open, Job: →queued |
| `test_new_session_closes_previous_and_starts_fresh` | Starting a new session closes the prior one | new session_id != old, session_started_at set, session_closed_at is None | ASM: open→closed→open |

### Preflight / UIC gates (ASM Axis 4 + UIC)

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_preflight_emits_gate_results` | Preflight produces structured gate results | result contains "gates", "status", exit_code in {0,1}, no action_log leak | UIC: gate evaluation |
| `test_preflight_bootstraps_aria2_when_rpc_is_initially_unavailable` | Preflight recovers by starting aria2 when initially unreachable | aria2_available gate satisfied, ensure_daemon called once | ASM: daemon absent→available (recovery) |
| `test_auto_preflight_default_is_disabled` | Auto-preflight preference defaults to off | auto_preflight_on_run.value == False | UIC: preference default |
| `test_concurrency_default_is_sequential` | Default concurrency is 1 (sequential) | max_simultaneous_downloads.value == 1 | UIC: preference default, Coherence CR-6 |
| `test_duplicate_active_transfer_default_is_remove` | Duplicate transfer policy defaults to "remove" | duplicate_active_transfer_action.value == "remove" | UIC: preference default |

### Bandwidth probing

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_probe_fallback_reports_reason` | Probe fallback uses safe default when tool unavailable | source == "default", reason == "probe_unavailable", cap_bytes_per_sec == 250000 | UCC: observation/fallback |
| `test_probe_uses_machine_readable_networkquality_output` | Probe parses networkQuality JSON correctly | source == "networkquality", downlink_mbps == 80.0, cap_mbps == 64.0 | UCC: observation |
| `test_probe_timeout_without_parse_uses_default_floor` | Probe timeout with no parse falls back to default | source == "default", reason == "probe_timeout_no_parse", partial == True | UCC: observation/fallback |
| `test_should_probe_bandwidth_uses_interval` | Probe respects 180s interval | True when no prior probe, False at 100s, True at 181s | UCC: rate limiting |
| `test_apply_bandwidth_probe_reuses_recent_probe` | Recent probe result is reused without re-probing | probe_bandwidth not called, cap_mbps == 64.0 | UCC: caching |
| `test_apply_bandwidth_probe_refreshes_stale_probe` | Stale probe triggers fresh measurement and applies bandwidth | probe_bandwidth called, set_bandwidth called with 4000000 | UCC: observation refresh |

### Active transfer management

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_discover_active_transfer_prefers_state_gid` | Active transfer discovery uses state.active_gid first | gid == "gid-1", status == "active", percent == 10.0 | UCC: observation |
| `test_discover_active_transfer_recovers_url_from_queue` | Missing URL recovered from queue by gid match | url == recovered URL from queue item | ASM: recovery |
| `test_deduplicate_active_transfers_removes_less_advanced_duplicates_by_default` | Dedup keeps most-advanced transfer, removes others | kept contains "gid-keep", paused contains "gid-drop", action == "remove" | UIC: duplicate policy, Coherence CR-6 |

### Queue reconciliation

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_reconcile_live_queue_adopts_unmatched_active_job` | Unmatched live download is adopted into queue | changed == True, recovered == 1 | ASM: recovery, Job: →downloading |
| `test_reconcile_live_queue_updates_old_session_item_in_place` | Stale session item updated to match live state | changed == True, recovered == 1 | ASM: session transition |
| `test_reconcile_live_queue_collapses_duplicate_rows_for_same_live_download` | Duplicate queue rows for same URL collapsed to one | len(saved) == 1, gid == live gid, completedLength preserved | Job: dedup |

### Execution / UCC result semantics (ASM Axis 2 + 3)

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_process_queue_marks_completed_tracked_download_done` | Completed download transitions to "done" with post_action | result[0].status == "done", gid == "gid-1", post_action present | ASM: Job downloading→complete→done, Run running→idle |
| `test_process_queue_resumes_paused_tracked_download` | Paused tracked download is resumed and completes | unpause RPC called, result[0].status == "done" | ASM: Job paused→queued→downloading→done |
| `test_ucc_returns_structured_result` | run_ucc produces UCC-compliant structured output | result contains "result", "meta", result.observation, result.outcome | UCC: contract shape |

### Install / uninstall lifecycle

| Test | Intent | Oracle | Trace Target |
|---|---|---|---|
| `test_install_dry_run_is_describable` | Install dry-run returns UCC-shaped plan | meta.contract == "UCC", observation == "ok", outcome == "changed" | UCC: lifecycle |
| `test_install_dry_run_with_aria2_is_describable` | Install with aria2 includes launchd component | "aria2-launchd" in plan, reason == "install" | UCC: lifecycle |
| `test_lifecycle_reports_status_shape` | Status report covers all components with UCC shape | all 4 components present, meta.contract == "UCC" | UCC: observation |
| `test_lifecycle_status_includes_versions` | Status includes version strings in messages | version strings present in messages | UCC: observation |
| `test_networkquality_status_reports_availability_without_probe` | networkquality status check doesn't trigger probe | run not called, installed == True, usable == True | UCC: observation |
| `test_uninstall_dry_run_is_describable` | Uninstall dry-run returns UCC-shaped plan | meta.contract == "UCC", reason == "uninstall" | UCC: lifecycle |
| `test_uninstall_dry_run_with_aria2_is_describable` | Uninstall with aria2 includes launchd component | "aria2-launchd" in plan, reason == "uninstall" | UCC: lifecycle |

## Coverage Summary

| Trace Target | Tests |
|---|---|
| ASM: Session axis | 2 |
| ASM: Run axis | 2 |
| ASM: Job axis | 5 |
| ASM: Daemon axis (recovery) | 2 |
| ASM: Coherence rules | 2 |
| UIC: gates / preferences | 5 |
| UCC: execution results | 10 |
| UCC: lifecycle | 5 |
