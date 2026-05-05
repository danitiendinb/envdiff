"""Tests for envdiff.watcher module."""

import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest

from envdiff.watcher import EnvWatcher
from envdiff.differ import EnvDiffResult


def _write_env(path: str, content: str) -> None:
    with open(path, "w") as f:
        f.write(content)


class TestEnvWatcherInitialize:
    def test_initialize_loads_snapshots(self, tmp_path):
        env_file = tmp_path / ".env"
        _write_env(str(env_file), "KEY=value\n")

        watcher = EnvWatcher([str(env_file)], on_change=MagicMock())
        watcher.initialize()

        assert str(env_file) in watcher._snapshots
        assert watcher._snapshots[str(env_file)] == {"KEY": "value"}

    def test_initialize_skips_missing_files(self, tmp_path):
        missing = str(tmp_path / "missing.env")
        watcher = EnvWatcher([missing], on_change=MagicMock())
        watcher.initialize()

        assert missing not in watcher._snapshots


class TestEnvWatcherCheckOnce:
    def test_no_callback_when_file_unchanged(self, tmp_path):
        env_file = tmp_path / ".env"
        _write_env(str(env_file), "KEY=value\n")

        callback = MagicMock()
        watcher = EnvWatcher([str(env_file)], on_change=callback)
        watcher.initialize()
        watcher.check_once()

        callback.assert_not_called()

    def test_callback_fired_on_change(self, tmp_path):
        env_file = tmp_path / ".env"
        _write_env(str(env_file), "KEY=old\n")

        callback = MagicMock()
        watcher = EnvWatcher([str(env_file)], on_change=callback)
        watcher.initialize()

        # Force mtime to appear older so change is detected
        watcher._mtimes[str(env_file)] -= 2.0
        _write_env(str(env_file), "KEY=new\n")

        watcher.check_once()

        callback.assert_called_once()
        path_arg, result_arg = callback.call_args[0]
        assert path_arg == str(env_file)
        assert isinstance(result_arg, EnvDiffResult)

    def test_diff_result_reflects_change(self, tmp_path):
        env_file = tmp_path / ".env"
        _write_env(str(env_file), "ALPHA=1\n")

        callback = MagicMock()
        watcher = EnvWatcher([str(env_file)], on_change=callback)
        watcher.initialize()
        watcher._mtimes[str(env_file)] -= 2.0

        _write_env(str(env_file), "ALPHA=1\nBETA=2\n")
        watcher.check_once()

        _, result = callback.call_args[0]
        assert "BETA" in result.extra_keys

    def test_snapshot_updated_after_change(self, tmp_path):
        env_file = tmp_path / ".env"
        _write_env(str(env_file), "X=1\n")

        watcher = EnvWatcher([str(env_file)], on_change=MagicMock())
        watcher.initialize()
        watcher._mtimes[str(env_file)] -= 2.0

        _write_env(str(env_file), "X=2\n")
        watcher.check_once()

        assert watcher._snapshots[str(env_file)] == {"X": "2"}
