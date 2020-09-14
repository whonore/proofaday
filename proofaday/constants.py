from appdirs import user_data_dir, user_log_dir
from typing_extensions import Final

URL: Final = "https://proofwiki.org/wiki/"
RANDOM: Final = "Special:Random"

NPREFETCH: Final = 10
LOG_PATH: Final = user_log_dir("proofaday")
DATA_PATH: Final = user_data_dir("proofaday")
LOG_FILE: Final = "proofaday.log"
STATUS_FILE: Final = ".proofaday.status"

HOST: Final = "localhost"
PORT: Final = 48484

CLIENT_TIMEOUT: Final = 3
