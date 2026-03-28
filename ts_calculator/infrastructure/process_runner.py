"""Subprocess wrapper with real-time stdout streaming and cancellation."""
from __future__ import annotations
import subprocess
import threading
import queue
import time
from pathlib import Path
from typing import Callable, Optional, List


class ProcessRunner:
    """
    Runs an external process and streams stdout line-by-line via a callback.
    Thread-safe cancel() is supported.
    """

    def __init__(
        self,
        command: List[str],
        cwd: Path,
        on_line: Optional[Callable[[str], None]] = None,
        env: Optional[dict] = None,
    ) -> None:
        self.command = command
        self.cwd = cwd
        self.on_line = on_line or (lambda _: None)
        self.env = env

        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._cancelled = threading.Event()
        self._done = threading.Event()
        self.returncode: Optional[int] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self) -> None:
        """Launch the process and begin streaming stdout in a background thread."""
        import os
        env = os.environ.copy()
        if self.env:
            env.update(self.env)

        self._process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        self.start_time = time.monotonic()
        self._thread = threading.Thread(target=self._stream, daemon=True)
        self._thread.start()

    def _stream(self) -> None:
        assert self._process is not None
        try:
            for line in self._process.stdout:  # type: ignore[union-attr]
                if self._cancelled.is_set():
                    break
                self.on_line(line.rstrip("\n"))
        finally:
            self._process.wait()
            self.returncode = self._process.returncode
            self.end_time = time.monotonic()
            self._done.set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        """Block until process finishes. Returns True if successful."""
        self._done.wait(timeout=timeout)
        return self.returncode == 0

    def cancel(self) -> None:
        """Request cancellation and terminate the process."""
        self._cancelled.set()
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                time.sleep(0.5)
                if self._process.poll() is None:
                    self._process.kill()
            except OSError:
                pass

    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def wall_time(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
