from __future__ import annotations
from datetime import datetime
from threading import Lock
from pathlib import Path


class Logger:
    """Simple thread-safe file logger."""

    def __init__(self, filepath: str) -> None:
        self.path = Path(filepath)
        self._lock = Lock()
        # ensure parent folder exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}\n"
        with self._lock:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line)
