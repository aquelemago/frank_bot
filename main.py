from __future__ import annotations

import sys


sys.dont_write_bytecode = True

from app.main import main


if __name__ == "__main__":
    raise SystemExit(main())
