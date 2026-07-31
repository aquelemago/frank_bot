from __future__ import annotations

import argparse
import sys
from typing import Sequence

from app.orchestrator.run import run


sys.dont_write_bytecode = True


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Exporta a fila Soft4 e envia os CSVs por e-mail.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Baixa e processa o CSV, mas nao envia e-mails.",
    )
    args = parser.parse_args(argv)
    return run(dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
