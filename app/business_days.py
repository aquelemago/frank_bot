from __future__ import annotations

import csv
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from app.csv_utils import CsvReadError, read_csv_rows, resolve_column


LOGGER = logging.getLogger(__name__)


class BusinessDayFilterError(RuntimeError):
    """Erro ao filtrar chamados por dias uteis sem interacao."""


def eh_dia_util(dia: date, feriados: set[date]) -> bool:
    return dia.weekday() < 5 and dia not in feriados


def contar_dias_uteis_sem_interacao(
    data_ultima_interacao,
    data_atual: date,
    feriados: set[date],
) -> int:
    if data_ultima_interacao is None:
        return 0

    if isinstance(data_ultima_interacao, datetime):
        data_ultima_interacao = data_ultima_interacao.date()

    if not isinstance(data_ultima_interacao, date):
        return 0

    contador = 0
    dia = data_ultima_interacao + timedelta(days=1)

    while dia <= data_atual:
        if eh_dia_util(dia, feriados):
            contador += 1
        dia += timedelta(days=1)

    return contador


def chamado_deve_ser_processado(
    data_ultima_interacao,
    data_atual: date,
    feriados: set[date],
    limite_dias_uteis: int = 3,
) -> bool:
    return (
        contar_dias_uteis_sem_interacao(
            data_ultima_interacao=data_ultima_interacao,
            data_atual=data_atual,
            feriados=feriados,
        )
        >= limite_dias_uteis
    )


def feriados_nacionais_brasil(ano: int) -> set[date]:
    pascoa = _calcular_pascoa(ano)
    return {
        date(ano, 1, 1),
        pascoa - timedelta(days=2),
        date(ano, 4, 21),
        date(ano, 5, 1),
        date(ano, 9, 7),
        date(ano, 10, 12),
        date(ano, 11, 2),
        date(ano, 11, 15),
        date(ano, 11, 20),
        date(ano, 12, 25),
    }


def montar_feriados(data_atual: date, feriados_adicionais: set[date]) -> set[date]:
    anos = {data_atual.year - 1, data_atual.year, data_atual.year + 1}
    feriados: set[date] = set()
    for ano in anos:
        feriados.update(feriados_nacionais_brasil(ano))
    feriados.update(feriados_adicionais)
    return feriados


def parse_feriados_adicionais(value: str) -> set[date]:
    feriados: set[date] = set()
    for item in value.replace(";", ",").split(","):
        text = item.strip()
        if not text:
            continue
        parsed = _parse_date_value(text)
        if parsed is None:
            raise BusinessDayFilterError(f"Feriado adicional invalido: {text}")
        feriados.add(parsed)
    return feriados


def filtrar_csv_por_dias_uteis_sem_interacao(
    source_csv: Path,
    data_atual: date,
    feriados: set[date],
    limite_dias_uteis: int,
    coluna_ultima_interacao: str,
) -> int:
    try:
        rows, fieldnames, dialect = read_csv_rows(source_csv)
    except CsvReadError as error:
        raise BusinessDayFilterError(str(error)) from error

    date_column = _resolve_optional_column(fieldnames, coluna_ultima_interacao, "ULTIMA INTERACAO")
    calendar_days_column = _resolve_optional_column(fieldnames, "Dias sem interacao", "DIAS SEM INTERACAO")

    if date_column:
        filtered_rows = _filter_by_last_interaction_date(
            rows=rows,
            date_column=date_column,
            data_atual=data_atual,
            feriados=feriados,
            limite_dias_uteis=limite_dias_uteis,
        )
    elif calendar_days_column:
        filtered_rows = _filter_by_calendar_days_fallback(
            rows=rows,
            calendar_days_column=calendar_days_column,
            data_atual=data_atual,
            feriados=feriados,
            limite_dias_uteis=limite_dias_uteis,
        )
    else:
        available = ", ".join(fieldnames)
        raise BusinessDayFilterError(
            "CSV sem coluna de ultima interacao ou dias sem interacao. "
            f"Configure CSV_COLUNA_ULTIMA_INTERACAO. Colunas: {available}"
        )

    _write_csv(source_csv, fieldnames, filtered_rows, dialect)
    LOGGER.info(
        "Filtro de dias uteis aplicado: %s de %s registro(s) mantido(s)",
        len(filtered_rows),
        len(rows),
    )
    return len(filtered_rows)


def _filter_by_last_interaction_date(
    rows: list[dict[str, str]],
    date_column: str,
    data_atual: date,
    feriados: set[date],
    limite_dias_uteis: int,
) -> list[dict[str, str]]:
    filtered: list[dict[str, str]] = []
    invalid = 0

    for row in rows:
        parsed = _parse_date_value(row.get(date_column))
        if parsed is None:
            invalid += 1
            continue
        if chamado_deve_ser_processado(parsed, data_atual, feriados, limite_dias_uteis):
            filtered.append(row)

    if invalid:
        LOGGER.warning("Registros ignorados por ultima interacao invalida/vazia: %s", invalid)
    return filtered


def _filter_by_calendar_days_fallback(
    rows: list[dict[str, str]],
    calendar_days_column: str,
    data_atual: date,
    feriados: set[date],
    limite_dias_uteis: int,
) -> list[dict[str, str]]:
    filtered: list[dict[str, str]] = []
    invalid = 0

    LOGGER.warning(
        "Coluna de ultima interacao nao encontrada; usando %s para inferir a data.",
        calendar_days_column,
    )
    for row in rows:
        days = _parse_int(row.get(calendar_days_column))
        if days is None:
            invalid += 1
            continue
        inferred_date = data_atual - timedelta(days=days)
        if chamado_deve_ser_processado(inferred_date, data_atual, feriados, limite_dias_uteis):
            filtered.append(row)

    if invalid:
        LOGGER.warning("Registros ignorados por dias sem interacao invalidos/vazios: %s", invalid)
    return filtered


def _resolve_optional_column(fieldnames: list[str], configured_name: str, fallback_contains: str) -> str | None:
    try:
        return resolve_column(fieldnames, configured_name, fallback_contains)
    except CsvReadError:
        return None


def _parse_date_value(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value

    text = str(value).strip().strip('"').strip("'")
    if not text:
        return None

    text = text.replace("T", " ")
    for suffix in ("Z", "+00:00"):
        if text.endswith(suffix):
            text = text[: -len(suffix)].strip()

    for fmt in (
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _calcular_pascoa(ano: int) -> date:
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]], dialect: csv.Dialect) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter=dialect.delimiter,
            quotechar=dialect.quotechar or '"',
            quoting=dialect.quoting,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
