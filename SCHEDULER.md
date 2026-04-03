# af-scheduler — Scheduler and aria2 Interaction Model

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  ariaflow process                                            │
│                                                              │
│  ┌─────────────────┐         ┌────────────────────────────┐  │
│  │  af-api          │ ──────► │  af-scheduler              │  │
│  │  (main thread)   │ start/  │  (daemon thread)           │  │
│  │                  │ stop    │                            │  │
│  │  POST /api/run   │         │  process_queue() loop      │  │
│  │  POST /api/pause │         │  polls every 2s            │  │
│  │  POST /api/resume│         │  priority-sorted scheduling│  │
│  └─────────────────┘         └────────────┬───────────────┘  │
│                                            │                  │
│                                            │ JSON-RPC :6800   │
│                                            │                  │
│  ┌─────────────────────────────────────────▼──────────────┐   │
│  │  State files                                           │   │
│  │  state.json   — scheduler + session state              │   │
│  │  queue.json   — item list                              │   │
│  │  archive.json — soft-deleted items                     │   │
│  └────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                              │
                              │ JSON-RPC over HTTP
                              ▼
                 ┌─────────────────────────┐
                 │  aria2c process          │
                 │  (external, port 6800)   │
                 │                          │
                 │  Manages:                │
                 │  - HTTP/FTP downloads    │
                 │  - BitTorrent/magnet     │
                 │  - Metalink              │
                 │  - Bandwidth limits      │
                 │  - File I/O              │
                 └─────────────────────────┘
```

## af-scheduler States

```
              POST /api/run
              {action: start}
                    │
                    ▼
    ┌───────┐    ┌──────────┐    POST /api/run
    │ idle  │───►│ running  │    {action: stop}
    └───┬───┘    └──┬───┬───┘────────────┐
        ▲           │   │                ▼
        │     POST  │   │ all items   ┌──────────────┐
        │   /api/   │   │ terminal    │stop_requested│
        │   pause   │   │             └──────┬───────┘
        │           ▼   │                    │ drain
        │     ┌────────┐│                    │ complete
        │     │ paused ││                    │
        │     └───┬────┘│                    │
        │  POST   │     │                    │
        │  /api/  │     │                    │
        │  resume │     │                    │
        │         ▼     ▼                    │
        └─────────────────────────────────────┘
                   (back to idle)
```

| State | `running` | `paused` | `stop_requested` | Description |
|---|---|---|---|---|
| **idle** | false | false | false | Not processing. Waiting for `POST /api/run {action: start}` |
| **running** | true | false | false | Scheduling and polling items every 2s |
| **paused** | true | true | false | Loop active but not scheduling new items. Existing aria2 downloads paused |
| **stop_requested** | true | — | true | Draining: pausing all active aria2 downloads, then → idle |

### Transitions

| From | To | Trigger |
|---|---|---|
| idle → running | `POST /api/run {action: start}` | Spawns daemon thread |
| running → paused | `POST /api/pause` | Pauses all active aria2 GIDs, sets `state.paused=true` |
| paused → running | `POST /api/resume` | Unpauses all aria2 GIDs, sets `state.paused=false` |
| running → stop_requested | `POST /api/run {action: stop}` | Sets `state.stop_requested=true` |
| stop_requested → idle | Automatic | Loop detects flag, pauses all GIDs, closes session |
| running → idle | Automatic | All items in terminal state (queue_complete) |
| paused → idle | Automatic | All items in terminal state (queue_complete) |

## aria2c States (per GID)

aria2 manages downloads independently. ariaflow reads aria2 state via `aria2.tellStatus(gid)`:

```
              aria2.addUri
                  │
                  ▼
             ┌─────────┐
             │ waiting  │  (queued in aria2, slot limit)
             └────┬─────┘
                  │ slot available
                  ▼
             ┌─────────┐
             │ active   │  (transferring data)
             └──┬──┬──┬─┘
                │  │  │
     complete   │  │  │ error
                ▼  │  ▼
          ┌────────┐ ┌───────┐
          │complete│ │ error │
          └────────┘ └───────┘
                │
                │ aria2.pause / aria2.remove
                ▼
          ┌────────┐    ┌─────────┐
          │ paused │    │ removed │
          └────────┘    └─────────┘
```

| aria2 status | Meaning | ariaflow maps to |
|---|---|---|
| `waiting` | Queued in aria2, waiting for slot | item.status = `queued`, item.live_status = `waiting` |
| `active` | Transferring data | item.status = `downloading`, item.live_status = `active` |
| `paused` | Paused in aria2 | item.status = `paused`, item.live_status = `paused` |
| `complete` | Transfer finished | item.status = `done` |
| `error` | Transfer failed | item.status = `error` |
| `removed` | GID removed from aria2 | item.status = `stopped` |

## Interaction: af-scheduler ↔ aria2c

### Startup sequence

```
1. ensure_aria_daemon()
   │── aria2.getVersion()         ← check if already running
   │   └── success → return       ← already running
   │   └── fail → spawn aria2c
   │       └── sleep(2)
   │       └── aria2.getVersion() ← verify it started
   │           └── fail → raise RuntimeError
   │
2. deduplicate_active_transfers()
   │── aria2.tellActive()         ← get all active GIDs
   │── group by URL
   │── keep best progress per URL
   │── aria2.remove(duplicate_gid) or aria2.pause(duplicate_gid)
   │
3. reconcile_live_queue()
   │── aria2.tellActive()         ← get all active GIDs
   │── match to queue items by GID/URL
   │── adopt orphaned aria2 jobs into queue
   │── update session_id on recovered items
```

### Main loop (every 2s)

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: Load (locked)                                 │
│  ├── load queue.json                                    │
│  ├── load state.json                                    │
│  └── check stop_requested → if true, drain and exit     │
├─────────────────────────────────────────────────────────┤
│  Phase 2: RPC calls (unlocked)                          │
│  ├── _poll_tracked_jobs()                               │
│  │   └── for each item with gid:                        │
│  │       ├── aria2.tellStatus(gid)                      │
│  │       ├── active → item.status = downloading         │
│  │       ├── waiting → item.status = queued             │
│  │       ├── paused → item.status = paused              │
│  │       ├── complete → item.status = done              │
│  │       ├── error → item.status = error                │
│  │       ├── removed → item.status = stopped            │
│  │       └── RPC fail × 5 → item.status = error         │
│  │           (error_code = "rpc_unreachable")           │
│  │                                                       │
│  ├── _apply_bandwidth_probe()                           │
│  │   └── probe_bandwidth() if interval elapsed          │
│  │       └── networkQuality -u -c -s                    │
│  │   └── aria2.changeGlobalOption(max-download-limit)   │
│  │                                                       │
│  ├── Schedule new downloads (if not paused):            │
│  │   └── for each queued item (sorted by priority):     │
│  │       └── aria2.addUri([urls], options)               │
│  │           or aria2.addTorrent(base64, options)        │
│  │           or aria2.addMetalink(base64, options)       │
│  │       └── item.status = downloading                  │
│  │       └── respect max_simultaneous_downloads slots   │
├─────────────────────────────────────────────────────────┤
│  Phase 3: Save (locked)                                 │
│  ├── save queue.json                                    │
│  ├── update state.json (active_gid, active_url)         │
│  └── check if all items terminal → exit (queue_complete)│
├─────────────────────────────────────────────────────────┤
│  sleep(2) → repeat                                      │
└─────────────────────────────────────────────────────────┘
```

### Stop/drain sequence

```
1. User calls POST /api/run {action: stop}
   └── state.stop_requested = true

2. Next loop iteration detects stop_requested:
   ├── aria2.tellActive()          ← get all active GIDs
   ├── for each GID:
   │   └── aria2.pause(gid)        ← pause in aria2
   │   └── item.status = paused    ← update queue item
   ├── state.running = false
   ├── state.stop_requested = false
   ├── state.paused = false
   ├── close_state_session(reason="stop_requested")
   └── return items
```

### Global pause/resume

```
POST /api/pause:
├── aria2.tellActive()             ← get all active GIDs
├── for each GID:
│   └── aria2.pause(gid)           ← pause in aria2
│   └── item.status = paused
│   └── item.paused_at = now
├── state.paused = true
└── scheduler loop continues but skips scheduling new items

POST /api/resume:
├── for each paused item with GID:
│   └── aria2.unpause(gid)         ← resume in aria2
│   └── item.status = downloading
│   └── item.resumed_at = now
├── state.paused = false
└── scheduler loop resumes scheduling
```

### Per-item actions (independent of scheduler)

```
POST /api/item/{id}/pause:
├── aria2.pause(gid)               ← pause just this GID
├── item.status = paused
├── item.paused_at = now
└── scheduler will NOT auto-resume this item

POST /api/item/{id}/resume:
├── aria2.unpause(gid)             ← resume just this GID
├── item.status = downloading
├── item.resumed_at = now
└── if no gid: item.status = queued (re-scheduled)

POST /api/item/{id}/remove:
├── aria2.remove(gid)              ← remove from aria2
├── item.status = cancelled
├── item → archive.json
└── removed from queue.json

POST /api/item/{id}/retry:
├── item.status = queued
├── clear: gid, error_code, error_message, error_at
├── clear: recovered, recovered_at, recovery_session_id
└── scheduler will pick it up on next loop
```

## Download Mode → aria2 RPC Mapping

| Mode | aria2 RPC | Options |
|---|---|---|
| `http` | `aria2.addUri([url], opts)` | max-download-limit, allow-overwrite, continue |
| `magnet` | `aria2.addUri([url], opts)` | + pause-metadata=true |
| `torrent` | `aria2.addUri([url], opts)` | + pause-metadata=true |
| `metalink` | `aria2.addUri([url], opts)` | + pause-metadata=true |
| `mirror` | `aria2.addUri([url1,url2,...], opts)` | multiple URIs for same file |
| `torrent_data` | `aria2.addTorrent(base64, [], opts)` | + pause-metadata=true |
| `metalink_data` | `aria2.addMetalink(base64, opts)` | returns list of GIDs |

## Bandwidth Control

```
probe_bandwidth()
├── networkQuality -u -c -s -M 8    ← macOS system tool
├── parse: downlink_mbps, uplink_mbps, responsiveness
├── apply config:
│   ├── down_cap = downlink × (1 - free_percent/100)
│   ├── if free_absolute > 0: down_cap = min(down_cap, downlink - free_absolute)
│   └── up_cap = same logic for uplink
└── aria2.changeGlobalOption({max-overall-download-limit: cap_bytes})

Probes run:
- Automatically every bandwidth_probe_interval_seconds (default 180)
- Manually via POST /api/bandwidth/probe
```

## State Files

| File | Content | Updated by |
|---|---|---|
| `state.json` | running, paused, stop_requested, session_id, _rev, bandwidth probe cache | af-scheduler, af-api |
| `queue.json` | items list with status, gid, mode, priority, timestamps | af-scheduler, af-api |
| `archive.json` | soft-deleted items | af-api (on remove/cleanup) |
| `declaration.json` | UIC gates, preferences, policies | af-api |
| `actions.jsonl` | audit log of all operations | af-scheduler, af-api |
| `sessions.jsonl` | session history | af-scheduler (on close) |
| `.storage.lock` | file lock (fcntl) | both (mutual exclusion) |
