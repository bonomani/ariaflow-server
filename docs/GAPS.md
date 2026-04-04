# ariaflow — Feature Gap Analysis (Backend)

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

Per-item endpoints: `POST /api/item/<id>/pause`, `resume`, `remove`, `retry`. Each validates state, logs to `actions.jsonl`, and triggers SSE events.

### 3.1 Torrent/metalink file selection

Supports `.torrent`, `.metalink`, magnet URLs with `--pause-metadata=true`. File picker via `GET /api/item/<id>/files` and selection via `POST /api/item/<id>/files` with `{select: [1,3,5]}`.

### 4.1 aria2 global options proxy

`POST /api/aria2/change_global_option` with 3-tier safety: managed options (download/upload limits, seed) blocked from generic API, safe options (concurrency, split, timeout) allowed, unsafe options require `aria2_unsafe_options` preference. Logs changes.

### 5.2 Docker image

Dockerfile installs aria2 + ariaflow + ariaflow-web. Exposes ports 8000/8001. Volume mount for downloads/config.

## Remaining

### 3.2 DirectURL / file serving — deferred

Completed files sit in aria2's download directory with no API to serve them. **Recommendation:** document how to point a static file server (nginx, caddy) at the download directory (zero code). Add `GET /api/files` later if demand exists.
