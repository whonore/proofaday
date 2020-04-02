import json
import threading
import time
from pathlib import Path
from typing import Any, Optional
from typing_extensions import TypedDict

import proofaday.constants as consts

StatusData = TypedDict("StatusData", {"pid": int, "host": str, "port": int})


class Status:
    poll_interval = 0.5

    def __init__(self, path: Path) -> None:
        self.file = path / consts.STATUS_FILE

    def read(self) -> Optional[StatusData]:
        if self.file.is_file():
            return json.loads(self.file.read_text())  # type: ignore[no-any-return]
        return None

    def write(self, **kwargs: Any) -> bool:
        try:
            self.file.write_text(json.dumps(kwargs))
            return True
        except Exception:
            return False

    def remove(self) -> bool:
        try:
            self.file.unlink()
            return True
        except Exception:
            return False

    def _wait(self, exist: bool, stop: threading.Event) -> None:
        while self.file.is_file() != exist and not stop.is_set():
            time.sleep(Status.poll_interval)

    def wait(self, exist: bool, timeout: Optional[float] = 1.5) -> bool:
        stop = threading.Event()
        wait_thread = threading.Thread(target=self._wait, args=(exist, stop))
        wait_thread.start()
        wait_thread.join(timeout=timeout)
        stop.set()
        return self.file.is_file() == exist
