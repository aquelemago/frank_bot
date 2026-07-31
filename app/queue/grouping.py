from __future__ import annotations


def group_by_attendant(
    rows: list[dict[str, str]],
    attendant_column: str,
) -> dict[str, list[dict[str, str]]]:
    """Agrupa linhas de CSV por atendente.

    Linhas sem atendente (coluna vazia) sao descartadas, preservando o
    comportamento historico do `email_queue`.
    """
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        attendant = (row.get(attendant_column) or "").strip()
        if not attendant:
            continue
        grouped.setdefault(attendant, []).append(row)
    return grouped
