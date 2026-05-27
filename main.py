from __future__ import annotations

import sys


sys.dont_write_bytecode = True

from app.main import run


if __name__ == "__main__":
    raise SystemExit(run())
