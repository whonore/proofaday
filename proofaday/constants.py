import os

from appdirs import user_data_dir, user_log_dir
from typing_extensions import Final

URL: Final = "https://proofwiki.org/wiki/"
RANDOM: Final = "Special:Random"

NPREFETCH: Final = 10
LOG_PATH: Final = user_log_dir("proofaday")
try:
    _data_path = os.path.join(os.environ["XDG_RUNTIME_DIR"], "proofaday")
except KeyError:
    _data_path = user_data_dir("proofaday")
finally:
    DATA_PATH: Final = _data_path
LOG_FILE: Final = "proofaday.log"
STATUS_FILE: Final = ".proofaday.status"

HOST: Final = "localhost"
PORT: Final = 48484

CLIENT_TIMEOUT: Final = 3
