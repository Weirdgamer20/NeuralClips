"""Structured logging configuration for NeuralClips."""

import logging
import os
import re
import sys
from typing import Optional

# Regex pattern for sanitizing potential tokens/keys from logs
SECRET_PATTERNS = [
    re.compile(r'(AIza[0-9A-Za-z-_]{35})'),
    re.compile(r'(EAAB[0-9A-Za-z]+)'),
    re.compile(r'(1//[0-9A-Za-z-_]+)'),
    re.compile(r'(bearer\s+)([A-Za-z0-9\-._~+/]+=*)', re.IGNORECASE),
    re.compile(r'(client_secret[\'\"]?\s*[:=]\s*[\'\"]?)([^\'\"\s]+)', re.IGNORECASE),
    re.compile(r'(access_token[\'\"]?\s*[:=]\s*[\'\"]?)([^\'\"\s]+)', re.IGNORECASE),
]


class SanitizedFormatter(logging.Formatter):
    """Logging formatter that redacts secrets and sensitive tokens."""

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern in SECRET_PATTERNS:
            msg = pattern.sub(r'[REDACTED_SECRET]', msg)
        return msg


def setup_logger(
    name: str = "neuralclips",
    log_file: Optional[str] = None,
    level: str = "INFO",
) -> logging.Logger:
    """Configures and returns a sanitized logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, os.getenv("LOG_LEVEL", level).upper(), logging.INFO)
    logger.setLevel(log_level)

    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s:%(funcName)s] %(message)s"
    formatter = SanitizedFormatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(log_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Optional File Handler
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    logger.propagate = False
    return logger
