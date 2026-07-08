"""
database.py — Operações de alto nível sobre o banco JSON.

Enquanto json_manager.py sabe LER/GRAVAR o arquivo, este módulo sabe
O QUE gravar: registros de histórico, contadores de uso e último acesso.

Usa dataclasses para representar um registro de execução de forma
tipada e autodocumentada.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

from json_manager import load_data, save_data
from logger import get_logger

logger = get_logger("database")


@dataclass
class ExecutionRecord:
    """Representa UMA execução de comando pelo usuário.

    dataclass gera automaticamente __init__, __repr__ e __eq__,
    eliminando código repetitivo (boilerplate).
    """

    comando: str            # texto digitado, ex.: "abrir chrome"
    tipo: str               # app | pasta | arquivo | url
    alvo: str               # o que foi efetivamente aberto
    status: str             # sucesso | erro
    resultado: str          # mensagem descritiva
    data: str               # AAAA-MM-DD
    hora: str               # HH:MM:SS
    tempo_execucao_ms: float


def register_execution(
    comando: str,
    tipo: str,
    alvo: str,
    status: str,
    resultado: str,
    tempo_execucao_ms: float,
) -> None:
    """Registra uma execução no histórico e atualiza contadores.

    Fluxo:
        1. Carrega o JSON atual (sem apagar nada).
        2. Anexa o novo registro ao histórico.
        3. Incrementa o contador do comando.
        4. Atualiza o último acesso do comando.
        5. Grava tudo de volta.
    """
    now = datetime.now()
    record = ExecutionRecord(
        comando=comando,
        tipo=tipo,
        alvo=alvo,
        status=status,
        resultado=resultado,
        data=now.strftime("%Y-%m-%d"),
        hora=now.strftime("%H:%M:%S"),
        tempo_execucao_ms=round(tempo_execucao_ms, 2),
    )

    data = load_data()
    data["historico"].append(asdict(record))

    key = comando.strip().lower()
    contadores: dict[str, int] = data["contadores"]
    contadores[key] = contadores.get(key, 0) + 1
    data["ultimo_acesso"][key] = f"{record.data} {record.hora}"

    save_data(data)
    logger.info("Execução registrada: %s (%s)", comando, status)


def get_history(limit: int | None = None) -> list[dict[str, Any]]:
    """Retorna o histórico (mais recentes primeiro).

    Args:
        limit: quantidade máxima de registros; None = todos.
    """
    historico = list(reversed(load_data()["historico"]))
    return historico[:limit] if limit else historico


def get_statistics() -> dict[str, Any]:
    """Calcula estatísticas de uso a partir do JSON.

    Returns:
        dict com total de execuções, sucessos, erros, comandos mais
        usados e último acesso de cada comando.
    """
    data = load_data()
    historico = data["historico"]

    sucessos = sum(1 for item in historico if item["status"] == "sucesso")
    erros = len(historico) - sucessos

    # sorted() com lambda ordena os comandos pelo contador, decrescente.
    mais_usados = sorted(
        data["contadores"].items(), key=lambda par: par[1], reverse=True
    )[:10]

    return {
        "total_execucoes": len(historico),
        "sucessos": sucessos,
        "erros": erros,
        "mais_usados": mais_usados,
        "ultimo_acesso": data["ultimo_acesso"],
        "criado_em": data["meta"].get("criado_em"),
    }


def search_commands(term: str) -> list[dict[str, Any]]:
    """Pesquisa registros do histórico que contenham o termo informado."""
    term = term.strip().lower()
    return [
        item
        for item in get_history()
        if term in item["comando"].lower() or term in item["alvo"].lower()
    ]
