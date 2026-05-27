from __future__ import annotations

import logging
import os
import shutil
import stat
from pathlib import Path


LOGGER = logging.getLogger(__name__)


def cleanup_runtime_residue(project_root: Path) -> None:
    """Remove artefatos locais que podem sobrar entre execucoes."""
    _remove_pycache(project_root)


def _remove_pycache(project_root: Path) -> None:
    removed = 0
    for path in project_root.rglob("__pycache__"):
        if ".venv" in path.parts or "perfil_soft4" in path.parts:
            continue
        if path.is_dir():
            shutil.rmtree(path, onerror=_remove_readonly)
            removed += 1
    if removed:
        LOGGER.info("Caches Python removidos: %s", removed)


def _remove_readonly(function, path, exc_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        function(path)
    except Exception:
        raise exc_info[1]
