# All Variables — ariaflow

## Item Fields (31 fields stored in queue.json)

| Field | snake_case |
|---|---|
| `cancelled_at` | yes |
| `completed_at` | yes |
| `completed_length` | yes |
| `created_at` | yes |
| `download_speed` | yes |
| `error_at` | yes |
| `error_code` | yes |
| `error_message` | yes |
| `gid` | yes |
| `id` | yes |
| `live_status` | yes |
| `metalink_data` | yes |
| `mirrors` | yes |
| `mode` | yes |
| `output` | yes |
| `paused_at` | yes |
| `post_action` | yes |
| `post_action_rule` | yes |
| `priority` | yes |
| `recovered` | yes |
| `recovered_at` | yes |
| `recovery_session_id` | yes |
| `removed_at` | yes |
| `resumed_at` | yes |
| `rpc_failures` | yes |
| `session_history` | yes |
| `session_id` | yes |
| `status` | yes |
| `torrent_data` | yes |
| `total_length` | yes |
| `url` | yes |

## State Fields (13 fields stored in state.json)

| Field | snake_case |
|---|---|
| `_rev` | yes |
| `active_gid` | yes |
| `active_url` | yes |
| `last_bandwidth_probe` | yes |
| `last_bandwidth_probe_at` | yes |
| `paused` | yes |
| `running` | yes |
| `session_closed_at` | yes |
| `session_closed_reason` | yes |
| `session_id` | yes |
| `session_last_seen_at` | yes |
| `session_started_at` | yes |
| `stop_requested` | yes |

## Constants (22)

| Module | Name |
|---|---|
| `aria2_rpc` | `_BITS_PER_MEGABIT` |
| `aria2_rpc` | `_BYTES_PER_MEGABIT` |
| `aria2_rpc` | `_SAFE_ARIA2_OPTIONS` |
| `bandwidth` | `_NETWORKQUALITY_CANDIDATES` |
| `bandwidth` | `_NETWORKQUALITY_MAX_RUNTIME` |
| `bandwidth` | `_NETWORKQUALITY_PROBE_INTERVAL` |
| `bandwidth` | `_NETWORKQUALITY_TIMEOUT` |
| `contracts` | `DEFAULT_DECLARATION` |
| `platform.launchd` | `ARIA2_LABEL` |
| `queue_ops` | `DOWNLOAD_MODES` |
| `queue_ops` | `ITEM_STATUSES` |
| `queue_ops` | `_TERMINAL_STATUSES` |
| `scheduler` | `_ARIA2_TO_ITEM` |
| `scheduler` | `_MAX_RPC_FAILURES` |
| `state` | `_ACTION_LOG_KEEP_LINES` |
| `state` | `_ACTION_LOG_MAX_LINES` |
| `storage` | `_STORAGE_LOCK` |
| `storage` | `_STORAGE_LOCK_STATE` |
| `webapp` | `API_ONLY_HTML` |
| `webapp` | `API_SCHEMA_VERSION` |
| `webapp` | `INDEX_HTML` |
| `webapp` | `STATUS_CACHE_TTL` |

## Classes (3)

| Module | Name |
|---|---|
| `contracts` | `UCCResult` |
| `queue_ops` | `QueueItem` |
| `webapp` | `AriaFlowHandler` |

## aria2_ Functions (49)

| Module | Function |
|---|---|
| `aria2_rpc` | `aria2_add_download` |
| `aria2_rpc` | `aria2_add_metalink` |
| `aria2_rpc` | `aria2_add_torrent` |
| `aria2_rpc` | `aria2_add_uri` |
| `aria2_rpc` | `aria2_change_global_option` |
| `aria2_rpc` | `aria2_change_option` |
| `aria2_rpc` | `aria2_change_options` |
| `aria2_rpc` | `aria2_change_position` |
| `aria2_rpc` | `aria2_change_uri` |
| `aria2_rpc` | `aria2_current_bandwidth` |
| `aria2_rpc` | `aria2_current_global_options` |
| `aria2_rpc` | `aria2_ensure_daemon` |
| `aria2_rpc` | `aria2_force_pause` |
| `aria2_rpc` | `aria2_force_pause_all` |
| `aria2_rpc` | `aria2_force_remove` |
| `aria2_rpc` | `aria2_force_shutdown` |
| `aria2_rpc` | `aria2_get_files` |
| `aria2_rpc` | `aria2_get_global_option` |
| `aria2_rpc` | `aria2_get_global_stat` |
| `aria2_rpc` | `aria2_get_option` |
| `aria2_rpc` | `aria2_get_peers` |
| `aria2_rpc` | `aria2_get_servers` |
| `aria2_rpc` | `aria2_get_session_info` |
| `aria2_rpc` | `aria2_get_uris` |
| `aria2_rpc` | `aria2_get_version` |
| `aria2_rpc` | `aria2_list_methods` |
| `aria2_rpc` | `aria2_list_notifications` |
| `aria2_rpc` | `aria2_multicall` |
| `aria2_rpc` | `aria2_pause` |
| `aria2_rpc` | `aria2_pause_all` |
| `aria2_rpc` | `aria2_purge_download_result` |
| `aria2_rpc` | `aria2_remove` |
| `aria2_rpc` | `aria2_remove_download_result` |
| `aria2_rpc` | `aria2_save_session` |
| `aria2_rpc` | `aria2_set_bandwidth` |
| `aria2_rpc` | `aria2_set_download_bandwidth` |
| `aria2_rpc` | `aria2_shutdown` |
| `aria2_rpc` | `aria2_status` |
| `aria2_rpc` | `aria2_tell_active` |
| `aria2_rpc` | `aria2_tell_status` |
| `aria2_rpc` | `aria2_tell_stopped` |
| `aria2_rpc` | `aria2_tell_waiting` |
| `aria2_rpc` | `aria2_unpause` |
| `aria2_rpc` | `aria2_unpause_all` |
| `platform.launchd` | `aria2_plist_path` |
| `platform.launchd` | `aria2_session_dir` |
| `platform.launchd` | `aria2_status` |
| `queue_ops` | `aria2_active_status` |
| `queue_ops` | `aria2_discover_active_transfer` |

## Public Functions (88)

| Module | Function |
|---|---|
| `aria2_rpc` | `aria_rpc` |
| `bandwidth` | `bandwidth_config` |
| `bandwidth` | `bandwidth_status` |
| `bandwidth` | `manual_probe` |
| `bandwidth` | `probe_bandwidth` |
| `bonjour` | `advertise_http_service` |
| `bonjour` | `bonjour_available` |
| `cli` | `build_parser` |
| `cli` | `main` |
| `contracts` | `declaration_path` |
| `contracts` | `ensure_declaration` |
| `contracts` | `load_declaration` |
| `contracts` | `preflight` |
| `contracts` | `run_ucc` |
| `contracts` | `save_declaration` |
| `install` | `brew_is_installed` |
| `install` | `brew_package_version` |
| `install` | `current_ariaflow_version` |
| `install` | `homebrew_install_ariaflow` |
| `install` | `homebrew_uninstall_ariaflow` |
| `install` | `install_all` |
| `install` | `networkquality_status` |
| `install` | `status_all` |
| `install` | `ucc_envelope` |
| `install` | `ucc_record` |
| `install` | `uninstall_all` |
| `platform.launchd` | `install_aria2_launchd` |
| `platform.launchd` | `is_macos` |
| `platform.launchd` | `launch_agents_dir` |
| `platform.launchd` | `uninstall_aria2_launchd` |
| `queue_ops` | `add_queue_item` |
| `queue_ops` | `dedup_active_transfer_action` |
| `queue_ops` | `detect_download_mode` |
| `queue_ops` | `find_queue_item_by_gid` |
| `queue_ops` | `find_queue_item_by_url` |
| `queue_ops` | `format_bytes` |
| `queue_ops` | `format_mbps` |
| `queue_ops` | `format_rate` |
| `queue_ops` | `get_item_files` |
| `queue_ops` | `load_queue` |
| `queue_ops` | `max_simultaneous_downloads` |
| `queue_ops` | `pause_active_transfer` |
| `queue_ops` | `pause_queue_item` |
| `queue_ops` | `post_action` |
| `queue_ops` | `remove_queue_item` |
| `queue_ops` | `resume_active_transfer` |
| `queue_ops` | `resume_queue_item` |
| `queue_ops` | `retry_queue_item` |
| `queue_ops` | `save_queue` |
| `queue_ops` | `select_item_files` |
| `queue_ops` | `summarize_queue` |
| `reconcile` | `cleanup_queue_state` |
| `reconcile` | `deduplicate_active_transfers` |
| `reconcile` | `reconcile_live_queue` |
| `scheduler` | `auto_preflight_on_run` |
| `scheduler` | `get_active_progress` |
| `scheduler` | `process_queue` |
| `scheduler` | `start_background_process` |
| `scheduler` | `stop_background_process` |
| `state` | `append_action_log` |
| `state` | `archive_item` |
| `state` | `auto_cleanup_queue` |
| `state` | `close_state_session` |
| `state` | `ensure_state_session` |
| `state` | `load_action_log` |
| `state` | `load_archive` |
| `state` | `load_session_history` |
| `state` | `load_state` |
| `state` | `log_transfer_poll` |
| `state` | `record_action` |
| `state` | `save_archive` |
| `state` | `save_state` |
| `state` | `session_stats` |
| `state` | `start_new_state_session` |
| `state` | `touch_state_session` |
| `storage` | `action_log_path` |
| `storage` | `archive_path` |
| `storage` | `config_dir` |
| `storage` | `ensure_storage` |
| `storage` | `log_path` |
| `storage` | `queue_path` |
| `storage` | `read_json` |
| `storage` | `sessions_log_path` |
| `storage` | `state_path` |
| `storage` | `storage_lock_path` |
| `storage` | `storage_locked` |
| `storage` | `write_json` |
| `webapp` | `serve` |

## Private Functions (47)

| Module | Function |
|---|---|
| `aria2_rpc` | `_aria_speed_value` |
| `aria2_rpc` | `_cap_bytes_per_sec_from_mbps` |
| `aria2_rpc` | `_cap_mbps_from_bytes_per_sec` |
| `aria2_rpc` | `_core` |
| `aria2_rpc` | `_is_metadata_url` |
| `aria2_rpc` | `_rpc` |
| `bandwidth` | `_apply_bandwidth_probe` |
| `bandwidth` | `_apply_free_bandwidth_cap` |
| `bandwidth` | `_coerce_float` |
| `bandwidth` | `_core` |
| `bandwidth` | `_default_bandwidth_probe` |
| `bandwidth` | `_find_networkquality` |
| `bandwidth` | `_parse_networkquality_output` |
| `bandwidth` | `_should_probe_bandwidth` |
| `bonjour` | `_dns_sd_path` |
| `contracts` | `_aria_available` |
| `platform.launchd` | `_launchctl_list` |
| `platform.launchd` | `_launchctl_load` |
| `platform.launchd` | `_launchctl_unload` |
| `queue_ops` | `_apply_aria2_priority` |
| `queue_ops` | `_aria2_position_for_priority` |
| `queue_ops` | `_core` |
| `queue_ops` | `_find_queue_item_by_id` |
| `queue_ops` | `_pref_value` |
| `reconcile` | `_active_item_url` |
| `reconcile` | `_core` |
| `reconcile` | `_merge_active_status` |
| `reconcile` | `_merge_queue_rows` |
| `reconcile` | `_normalize_queue_row` |
| `reconcile` | `_queue_item_for_active_info` |
| `reconcile` | `_queue_item_preference` |
| `scheduler` | `_core` |
| `state` | `_core` |
| `state` | `_log_session_history` |
| `state` | `_rotate_action_log` |
| `webapp` | `_api_discovery` |
| `webapp` | `_error_payload` |
| `webapp` | `_find_openapi_spec` |
| `webapp` | `_lifecycle_payload` |
| `webapp` | `_parse_add_items` |
| `webapp` | `_resolve_auto_preflight_override` |
| `webapp` | `_run_tests` |
| `webapp` | `_session_fields` |
| `webapp` | `_sse_publish` |
| `webapp` | `_sse_subscribe` |
| `webapp` | `_sse_unsubscribe` |
| `webapp` | `_swagger_ui_html` |

## Summary

| Category | Count | Convention |
|---|---|---|
| Item fields | 31 | snake_case |
| State fields | 13 | snake_case |
| Constants | 22 | UPPER_SNAKE_CASE |
| Classes | 3 | PascalCase |
| aria2_ functions | 49 | aria2_ + snake_case |
| Public functions | 88 | snake_case |
| Private functions | 47 | _snake_case |
| **Total** | **253** | |
