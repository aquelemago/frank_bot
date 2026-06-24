from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.mailer import EmailSendError, send_test_email
from app.settings import ConfigError, load_email_settings, setup_logging


DEFAULT_RECIPIENT = "lucas.silva@mainhardt.com.br"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Envia um e-mail de teste usando as configuracoes SMTP do projeto.",
    )
    parser.add_argument(
        "--to",
        default=DEFAULT_RECIPIENT,
        help=f"Destinatario do teste. Padrao: {DEFAULT_RECIPIENT}",
    )
    args = parser.parse_args(argv)

    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Iniciando envio de email de teste para %s", args.to)

    try:
        settings = load_email_settings()
        send_test_email(settings=settings, recipient=args.to)
    except ConfigError as error:
        logger.error("Falha de configuracao SMTP: %s", error)
        return 2
    except EmailSendError as error:
        logger.error("%s", error)
        return 1
    except Exception:
        logger.exception("Falha inesperada no envio de email de teste")
        return 1

    logger.info("Envio de email de teste finalizado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
