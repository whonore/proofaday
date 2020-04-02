import json
from pathlib import Path
from typing import Any, Optional
from typing_extensions import TypedDict

import proofaday.constants as consts

Status = TypedDict("Status", {"pid": int, "host": str, "port": int})


def read_status(status_path: Path) -> Optional[Status]:
    status_file = status_path / consts.STATUS_FILE
    if status_file.is_file():
        return json.loads(status_file.read_text())  # type: ignore[no-any-return]
    return None


def write_status(status_path: Path, **kwargs: Any) -> None:
    status_file = status_path / consts.STATUS_FILE
    status_file.write_text(json.dumps(kwargs))
