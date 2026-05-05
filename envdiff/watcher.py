"""Watch .env files for changes and report diffs automatically."""

import os
import time
from typing import Callable, Dict, Optional

from envdiff.parser import parse_env_file
from envdiff.differ import diff_envs, EnvDiffResult


class EnvWatcher:
    """Watch one or more .env files and trigger callbacks on change."""

    def __init__(
        self,
        paths: list[str],
        on_change: Callable[[str, EnvDiffResult], None],
        poll_interval: float = 1.0,
    ) -> None:
        self.paths = paths
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._snapshots: Dict[str, Dict[str, str]] = {}
        self._mtimes: Dict[str, float] = {}

    def _load_snapshot(self, path: str) -> Optional[Dict[str, str]]:
        """Parse and return env file contents, or None if unreadable."""
        try:
            return parse_env_file(path)
        except (OSError, ValueError):
            return None

    def _get_mtime(self, path: str) -> float:
        """Return file modification time, or 0.0 if unavailable."""
        try:
            return os.path.getmtime(path)
        except OSError:
            return 0.0

    def initialize(self) -> None:
        """Take initial snapshots of all watched files."""
        for path in self.paths:
            snapshot = self._load_snapshot(path)
            if snapshot is not None:
                self._snapshots[path] = snapshot
                self._mtimes[path] = self._get_mtime(path)

    def check_once(self) -> None:
        """Check all watched files for changes and fire callbacks."""
        for path in self.paths:
            current_mtime = self._get_mtime(path)
            previous_mtime = self._mtimes.get(path, 0.0)

            if current_mtime <= previous_mtime:
                continue

            new_snapshot = self._load_snapshot(path)
            if new_snapshot is None:
                continue

            old_snapshot = self._snapshots.get(path, {})
            result = diff_envs(old_snapshot, new_snapshot)

            self._snapshots[path] = new_snapshot
            self._mtimes[path] = current_mtime
            self.on_change(path, result)

    def watch(self, max_iterations: Optional[int] = None) -> None:
        """Poll files in a loop. Runs indefinitely unless max_iterations set."""
        self.initialize()
        iterations = 0
        while max_iterations is None or iterations < max_iterations:
            self.check_once()
            time.sleep(self.poll_interval)
            iterations += 1
