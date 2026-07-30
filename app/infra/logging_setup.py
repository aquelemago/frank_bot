from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.infra.fs import PROJECT_ROOT


def setup_logging(log_dir: Path | None = None) -> Path:
    target_dir = log_dir or PROJECT_ROOT / "logs"
    target_dir.mkdir(parents=True, exist_ok=True)
    log_path = target_dir / "frank_bot.log"

    logging.addLevelName(logging.ERROR, "ERRO")
    logging.addLevelName(logging.WARNING, "AVISO")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(getattr(handler, "_frank_bot_handler", False) for handler in root_logger.handlers):
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        setattr(stream_handler, "_frank_bot_handler", True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        setattr(file_handler, "_frank_bot_handler", True)

        root_logger.addHandler(stream_handler)
        root_logger.addHandler(file_handler)

    return log_path
