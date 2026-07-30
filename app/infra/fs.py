from __future__ import annotations

import os
import stat
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def remove_readonly(function, path, exc_info) -> None:
    try:
        os.chmod(path, stat.S_IWRITE)
        function(path)
    except Exception:
        raise exc_info[1]
