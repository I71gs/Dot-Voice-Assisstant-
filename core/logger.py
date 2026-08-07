"""
core/logger.py — DOT Assistant Logging

Rotating file logger under logs/dot.log.
All modules use get_logger() to obtain a child logger.
Sensitive data (passwords, API keys) must never be passed to any logger call.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

_ROOT = Path(__file__).parent.parent.resolve()
_LOG_DIR = _ROOT / "logs"
_LOG_FILE = _LOG_DIR / "dot.log"

_initialized = False


def _init() -> None:
    global _initialized
    if _initialized:
        return
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("dot")
    root_logger.setLevel(logging.DEBUG)

    # Rotating file handler — max 2 MB, keep 5 backups
    fh = logging.handlers.RotatingFileHandler(
        _LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(fh)

    # Console handler — only WARNING and above
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root_logger.addHandler(ch)

    _initialized = True


def get_logger(name: str = "dot") -> logging.Logger:
    """Return a child logger under the 'dot' namespace."""
    _init()
    if name == "dot":
        return logging.getLogger("dot")
    return logging.getLogger(f"dot.{name}")
