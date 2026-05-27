from __future__ import annotations

import unittest
import sys
from pathlib import Path


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    suite = unittest.defaultTestLoader.discover("tests")
    raise SystemExit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
