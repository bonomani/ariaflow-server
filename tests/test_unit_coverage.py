"""Unit tests for 35 previously-untested public functions."""
from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class _TempDirMixin:
    """setUp/tearDown that points ARIA_QUEUE_DIR at a temp directory."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_env = os.environ.get("ARIA_QUEUE_DIR")
        os.environ["ARIA_QUEUE_DIR"] = self._tmpdir.name

    def tearDown(self) -> None:
        if self._orig_env is None:
            os.environ.pop("ARIA_QUEUE_DIR", None)
        else:
            os.environ["ARIA_QUEUE_DIR"] = self._orig_env
        self._tmpdir.cleanup()


# ── storage.py ──────────────────────────────────────────────────────


class TestStoragePaths(_TempDirMixin, unittest.TestCase):
    def test_config_dir_returns_path(self) -> None:
        from aria_queue.core import config_dir
        result = config_dir()
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), self._tmpdir.name)

    def test_queue_path(self) -> None:
        from aria_queue.core import config_dir, queue_path
        self.assertEqual(queue_path(), config_dir() / "queue.json")

    def test_state_path(self) -> None:
        from aria_queue.core import config_dir, state_path
        self.assertEqual(state_path(), config_dir() / "state.json")

    def test_log_path(self) -> None:
        from aria_queue.core import config_dir, log_path
        self.assertEqual(log_path(), config_dir() / "aria2.log")

    def test_action_log_path(self) -> None:
        from aria_queue.core import config_dir, action_log_path
        self.assertEqual(action_log_path(), config_dir() / "actions.jsonl")

    def test_archive_path(self) -> None:
        from aria_queue.core import config_dir, archive_path
        self.assertEqual(archive_path(), config_dir() / "archive.json")

    def test_sessions_log_path(self) -> None:
        from aria_queue.core import config_dir, sessions_log_path
        self.assertEqual(sessions_log_path(), config_dir() / "sessions.jsonl")

    def test_storage_lock_path(self) -> None:
        from aria_queue.core import config_dir, storage_lock_path
        self.assertEqual(storage_lock_path(), config_dir() / ".storage.lock")


class TestEnsureStorage(_TempDirMixin, unittest.TestCase):
    def test_creates_directory(self) -> None:
        from aria_queue.core import ensure_storage, config_dir
        subdir = Path(self._tmpdir.name) / "sub" / "dir"
        os.environ["ARIA_QUEUE_DIR"] = str(subdir)
        ensure_storage()
        self.assertTrue(subdir.is_dir())


class TestReadJson(_TempDirMixin, unittest.TestCase):
    def test_normal_read(self) -> None:
        from aria_queue.core import read_json
        p = Path(self._tmpdir.name) / "data.json"
        p.write_text(json.dumps({"a": 1}), encoding="utf-8")
        self.assertEqual(read_json(p, {}), {"a": 1})

    def test_missing_file_returns_default(self) -> None:
        from aria_queue.core import read_json
        p = Path(self._tmpdir.name) / "nope.json"
        self.assertEqual(read_json(p, []), [])

    def test_corrupted_file_creates_backup(self) -> None:
        from aria_queue.core import read_json
        p = Path(self._tmpdir.name) / "bad.json"
        p.write_text("{{{not json", encoding="utf-8")
        result = read_json(p, "default")
        self.assertEqual(result, "default")
        bak = p.with_suffix(".json.corrupt.bak")
        self.assertTrue(bak.exists())


class TestWriteJson(_TempDirMixin, unittest.TestCase):
    def test_write_then_read(self) -> None:
        from aria_queue.core import read_json, write_json
        p = Path(self._tmpdir.name) / "rw.json"
        write_json(p, {"x": 42})
        self.assertEqual(read_json(p, None), {"x": 42})


# ── state.py ────────────────────────────────────────────────────────


class TestEnsureStateSession(_TempDirMixin, unittest.TestCase):
    def test_creates_session_id(self) -> None:
        from aria_queue.core import ensure_state_session
        state = ensure_state_session()
        self.assertIsNotNone(state.get("session_id"))
        self.assertIsNotNone(state.get("session_started_at"))


class TestTouchStateSession(_TempDirMixin, unittest.TestCase):
    def test_updates_last_seen(self) -> None:
        from aria_queue.core import ensure_state_session, touch_state_session
        ensure_state_session()
        state = touch_state_session()
        self.assertIsNotNone(state.get("session_last_seen_at"))


class TestCloseStateSession(_TempDirMixin, unittest.TestCase):
    def test_sets_closed_fields(self) -> None:
        from aria_queue.core import ensure_state_session, close_state_session
        ensure_state_session()
        state = close_state_session("test_reason")
        self.assertIsNotNone(state.get("session_closed_at"))
        self.assertEqual(state.get("session_closed_reason"), "test_reason")


class TestLoadSessionHistory(_TempDirMixin, unittest.TestCase):
    def test_returns_list(self) -> None:
        from aria_queue.core import load_session_history
        result = load_session_history()
        self.assertIsInstance(result, list)


class TestSessionStats(_TempDirMixin, unittest.TestCase):
    def test_returns_dict_with_keys(self) -> None:
        from aria_queue.core import ensure_state_session, session_stats
        ensure_state_session()
        result = session_stats()
        self.assertIsInstance(result, dict)
        for key in ("session_id", "items_total", "items_done", "items_error",
                     "items_queued", "items_downloading", "items_paused",
                     "bytes_completed"):
            self.assertIn(key, result)


class TestAppendActionLog(_TempDirMixin, unittest.TestCase):
    def test_appends_entry(self) -> None:
        from aria_queue.core import append_action_log, action_log_path
        append_action_log({"action": "test", "target": "unit"})
        lines = action_log_path().read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 1)
        entry = json.loads(lines[-1])
        self.assertEqual(entry["action"], "test")


class TestLoadArchive(_TempDirMixin, unittest.TestCase):
    def test_returns_list(self) -> None:
        from aria_queue.core import load_archive
        self.assertIsInstance(load_archive(), list)


class TestSaveArchive(_TempDirMixin, unittest.TestCase):
    def test_roundtrip(self) -> None:
        from aria_queue.core import save_archive, load_archive
        items = [{"id": "a", "status": "complete"}]
        save_archive(items)
        self.assertEqual(load_archive(), items)


class TestArchiveItem(_TempDirMixin, unittest.TestCase):
    def test_adds_to_archive(self) -> None:
        from aria_queue.core import archive_item, load_archive
        archive_item({"id": "x", "status": "complete"})
        archived = load_archive()
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0]["id"], "x")
        self.assertIn("archived_at", archived[0])


class TestAutoCleanupQueue(_TempDirMixin, unittest.TestCase):
    def test_removes_old_done(self) -> None:
        from aria_queue.core import (
            auto_cleanup_queue, save_queue, load_queue, load_archive,
            ensure_storage,
        )
        ensure_storage()
        old_time = "2020-01-01T00:00:00+00:00"
        items = [
            {"id": "1", "status": "complete", "completed_at": old_time},
            {"id": "2", "status": "queued"},
        ]
        save_queue(items)
        result = auto_cleanup_queue(max_done_age_days=1)
        self.assertEqual(result["archived"], 1)
        remaining = load_queue()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], "2")


class TestLogTransferPoll(_TempDirMixin, unittest.TestCase):
    def test_appends_to_action_log(self) -> None:
        from aria_queue.core import log_transfer_poll, action_log_path
        log_transfer_poll(
            gid="abc",
            item={"id": "1", "url": "http://x"},
            info={"status": "active", "downloadSpeed": "100"},
        )
        self.assertTrue(action_log_path().exists())
        lines = action_log_path().read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 1)


# ── queue_ops.py ────────────────────────────────────────────────────


class TestDetectDownloadMode(unittest.TestCase):
    def test_http(self) -> None:
        from aria_queue.core import detect_download_mode
        self.assertEqual(detect_download_mode("http://example.com/file.zip"), "http")

    def test_magnet(self) -> None:
        from aria_queue.core import detect_download_mode
        self.assertEqual(detect_download_mode("magnet:?xt=urn:btih:abc"), "magnet")

    def test_torrent(self) -> None:
        from aria_queue.core import detect_download_mode
        self.assertEqual(detect_download_mode("http://x/file.torrent"), "torrent")

    def test_metalink(self) -> None:
        from aria_queue.core import detect_download_mode
        self.assertEqual(detect_download_mode("http://x/file.metalink"), "metalink")
        self.assertEqual(detect_download_mode("http://x/file.meta4"), "metalink")

    def test_mirror(self) -> None:
        from aria_queue.core import detect_download_mode
        self.assertEqual(
            detect_download_mode("http://a/f", mirrors=["http://a/f", "http://b/f"]),
            "mirror",
        )


class TestFindQueueItemByGid(_TempDirMixin, unittest.TestCase):
    def test_finds_item(self) -> None:
        from aria_queue.core import find_queue_item_by_gid, save_queue
        save_queue([{"id": "1", "gid": "g1", "status": "active"}])
        result = find_queue_item_by_gid("g1")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "1")

    def test_returns_none_for_missing(self) -> None:
        from aria_queue.core import find_queue_item_by_gid, save_queue
        save_queue([])
        self.assertIsNone(find_queue_item_by_gid("nope"))


class TestSummarizeQueue(unittest.TestCase):
    def test_counts_by_status(self) -> None:
        from aria_queue.core import summarize_queue
        items = [
            {"status": "queued"},
            {"status": "queued"},
            {"status": "active"},
            {"status": "complete"},
        ]
        result = summarize_queue(items)
        self.assertEqual(result["total"], 4)
        self.assertEqual(result["queued"], 2)
        self.assertEqual(result["active"], 1)
        self.assertEqual(result["complete"], 1)


# ── contracts.py ────────────────────────────────────────────────────


class TestDeclarationPath(_TempDirMixin, unittest.TestCase):
    def test_returns_path(self) -> None:
        from aria_queue.contracts import declaration_path
        result = declaration_path()
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result).endswith("declaration.json"))


class TestEnsureDeclaration(_TempDirMixin, unittest.TestCase):
    def test_creates_default(self) -> None:
        from aria_queue.contracts import ensure_declaration, declaration_path
        result = ensure_declaration()
        self.assertIsInstance(result, dict)
        self.assertIn("meta", result)
        self.assertTrue(declaration_path().exists())


# ── install.py ──────────────────────────────────────────────────────


class TestCurrentAriaflowVersion(unittest.TestCase):
    def test_returns_string(self) -> None:
        from aria_queue.install import current_ariaflow_version
        v = current_ariaflow_version()
        self.assertIsInstance(v, str)
        self.assertTrue(len(v) > 0)


class TestUccEnvelope(unittest.TestCase):
    def test_returns_dict_with_keys(self) -> None:
        from aria_queue.install import ucc_envelope
        result = ucc_envelope(
            target="queue", observed=True, outcome="ok",
        )
        self.assertIn("meta", result)
        self.assertIn("result", result)
        self.assertEqual(result["meta"]["target"], "queue")
        self.assertEqual(result["result"]["outcome"], "ok")


class TestUccRecord(unittest.TestCase):
    def test_returns_dict(self) -> None:
        from aria_queue.install import ucc_record
        result = ucc_record(target="t", observed=False, outcome="fail")
        self.assertIn("meta", result)
        self.assertEqual(result["result"]["observation"], "failed")


# ── bonjour.py ──────────────────────────────────────────────────────


class TestBonjourAvailable(unittest.TestCase):
    def test_returns_bool(self) -> None:
        from aria_queue.bonjour import bonjour_available
        self.assertIsInstance(bonjour_available(), bool)


class TestAdvertiseHttpService(unittest.TestCase):
    @patch("aria_queue.bonjour.bonjour_available", return_value=False)
    def test_context_manager_noop(self, _mock: MagicMock) -> None:
        from aria_queue.bonjour import advertise_http_service
        with advertise_http_service(
            role="api", port=8080, path="/", product="test", version="0.1"
        ):
            pass  # should not crash


# ── aria2_rpc.py ────────────────────────────────────────────────────


class TestAria2SetDownloadBandwidth(unittest.TestCase):
    @patch("aria_queue.aria2_rpc.aria2_change_option")
    def test_calls_change_option(self, mock_co: MagicMock) -> None:
        from aria_queue.aria2_rpc import aria2_set_download_bandwidth
        aria2_set_download_bandwidth("gid1", 1000, port=6800)
        mock_co.assert_called_once()
        args, kwargs = mock_co.call_args
        self.assertEqual(args[0], "gid1")


# ── transfers.py ────────────────────────────────────────────────────


class TestPauseActiveTransfer(_TempDirMixin, unittest.TestCase):
    @patch("aria_queue.core.aria2_tell_active", return_value=[])
    def test_no_active_returns_not_paused(self, _mock: MagicMock) -> None:
        from aria_queue.core import pause_active_transfer, ensure_storage
        ensure_storage()
        result = pause_active_transfer()
        self.assertFalse(result["paused"])
        self.assertEqual(result["reason"], "no_active_transfer")


# ── scheduler.py ────────────────────────────────────────────────────


class TestStopBackgroundProcess(_TempDirMixin, unittest.TestCase):
    def test_not_running_returns_stopped_false(self) -> None:
        from aria_queue.core import stop_background_process, ensure_storage
        ensure_storage()
        result = stop_background_process()
        self.assertFalse(result["stopped"])
        self.assertEqual(result["reason"], "not_running")


# ── bandwidth.py ────────────────────────────────────────────────────


class TestBandwidthConfig(_TempDirMixin, unittest.TestCase):
    def test_returns_dict_with_free_percent(self) -> None:
        from aria_queue.core import bandwidth_config, ensure_storage

        ensure_storage()
        result = bandwidth_config()
        self.assertIsInstance(result, dict)
        self.assertIn("down_free_percent", result)
        self.assertIn("probe_interval_seconds", result)


class TestBandwidthStatus(_TempDirMixin, unittest.TestCase):
    @patch("aria_queue.core.aria2_current_bandwidth", return_value={"limit": "0"})
    def test_returns_dict_with_config_and_bandwidth(self, _mock: MagicMock) -> None:
        from aria_queue.core import bandwidth_status, ensure_storage

        ensure_storage()
        result = bandwidth_status()
        self.assertIsInstance(result, dict)
        self.assertIn("config", result)
        self.assertIn("current_limit", result)


class TestManualProbe(_TempDirMixin, unittest.TestCase):
    @patch("aria_queue.core.probe_bandwidth", return_value={
        "source": "default",
        "reason": "probe_unavailable",
        "cap_mbps": 2,
        "cap_bytes_per_sec": 250000,
    })
    @patch("aria_queue.core.aria2_set_bandwidth")
    def test_returns_probe_result(self, _set: MagicMock, _probe: MagicMock) -> None:
        from aria_queue.core import manual_probe, ensure_storage

        ensure_storage()
        result = manual_probe()
        self.assertIsInstance(result, dict)
        self.assertIn("probe", result)


if __name__ == "__main__":
    unittest.main()
