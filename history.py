"""
history.py — Apresentação de histórico e estatísticas.

database.py CALCULA os dados; este módulo APRESENTA os dados no
terminal. Separar cálculo de exibição facilita testes e reuso
(princípio da responsabilidade única).
"""

from __future__ import annotations

from database import get_history, get_statistics, search_commands
from utils import LINE, format_history_row


def show_history(limit: int = 20) -> None:
    """Exibe os últimos registros do histórico."""
    registros = get_history(limit)
    print(f"\n{LINE}\nHISTÓRICO (últimos {limit})\n{LINE}")

    if not registros:
        print("Nenhum comando registrado ainda.")
        return

    for item in registros:
        print(format_history_row(item))
    print()


def show_statistics() -> None:
    """Exibe estatísticas de uso calculadas a partir do JSON."""
    stats = get_statistics()
    print(f"\n{LINE}\nESTATÍSTICAS\n{LINE}")
    print(f"Banco criado em....: {stats['criado_em']}")
    print(f"Total de execuções.: {stats['total_execucoes']}")
    print(f"Sucessos...........: {stats['sucessos']}")
    print(f"Erros..............: {stats['erros']}")

    print("\nComandos mais usados:")
    if not stats["mais_usados"]:
        print("  (nenhum ainda)")
    for comando, quantidade in stats["mais_usados"]:
        ultimo = stats["ultimo_acesso"].get(comando, "-")
        print(f"  {quantidade:>3}x  {comando:<30} último uso: {ultimo}")
    print()


def search_history() -> None:
    """Solicita um termo e exibe os registros correspondentes."""
    termo = input("Termo a pesquisar: ").strip()
    if not termo:
        print("Pesquisa vazia.\n")
        return

    resultados = search_commands(termo)
    print(f"\n{len(resultados)} resultado(s) para '{termo}':\n")
    for item in resultados[:30]:
        print(format_history_row(item))
    print()
