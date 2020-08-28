from pathlib import Path

from typing_extensions import Final

URL: Final = "https://proofwiki.org/wiki/"
RANDOM: Final = "Special:Random"

NPREFETCH: Final = 10
LOG_PATH: Final = Path(__file__).parent
LOG_FILE: Final = "proofaday.log"
STATUS_PATH: Final = Path(__file__).parent
STATUS_FILE: Final = ".proofaday.status"

HOST: Final = "localhost"
PORT: Final = 48484

CLIENT_TIMEOUT: Final = 3
