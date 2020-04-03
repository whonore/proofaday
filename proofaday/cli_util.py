from pathlib import Path
from typing import Optional

import click


class ClickPath(click.Path):
    def convert(  # type: ignore[override]
        self,
        value: str,
        param: Optional[click.core.Parameter],
        ctx: Optional[click.core.Context],
    ) -> Path:
        return Path(super().convert(value, param, ctx))
