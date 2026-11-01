"""Step 0: shared logger used by every other step.

Every module in this app asks this file for a logger instead of
setting up its own. That way all logs (from document loading to the
final answer) end up in one place, in one consistent format.
"""

import logging
import os
from datetime import datetime


LOGS_DIR = "hr_logs"
_run_started_at = datetime.now()
_date_folder = _run_started_at.strftime("%Y-%m-%d")
_day_dir = os.path.join(LOGS_DIR, _date_folder)
os.makedirs(_day_dir, exist_ok=True)

# One log file per run, named with the time the run started.
RUN_LOG_FILE = os.path.join(
    _day_dir,
    f"run_{_run_started_at.strftime('%Y-%m-%d_%H-%M-%S')}.log",
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(RUN_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def mask_secret(value: str | None, visible: int = 4) -> str:
    """Return a safe-to-log form of a secret (e.g. abcd...wxyz).

    Use this whenever a log line needs to show that a key exists without
    dumping the full value. Empty/missing values become '<empty>'.
    """
    if not value:
        return "<empty>"

    if len(value) <= visible * 2:
        return "*" * len(value)

    return f"{value[:visible]}...{value[-visible:]}"
