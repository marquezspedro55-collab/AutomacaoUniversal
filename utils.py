"""
utils.py — Funções utilitárias de apoio à interface de terminal.

Aqui ficam pequenas funções reutilizáveis que não pertencem a nenhum
domínio específico (limpar tela, imprimir cabeçalhos, formatar tabelas).
"""

from __future__ import annotations

import os

from config import APP_NAME, APP_VERSION, CURRENT_OS, OperatingSystem

LINE = "=" * 46


def clear_screen() -> None:
    """Limpa o terminal usando o comando adequado ao SO."""
    os.system("cls" if CURRENT_OS is OperatingSystem.WINDOWS else "clear")


def print_header() -> None:
    """Imprime o cabeçalho padrão do programa."""
    print(LINE)
    print(f"{APP_NAME}  v{APP_VERSION}".center(46))
    print(f"Sistema: {CURRENT_OS.value}".center(46))
    print(LINE)


def print_result(success: bool, message: str) -> None:
    """Exibe o resultado de uma operação com prefixo visual."""
    prefix = "[OK]" if success else "[ERRO]"
    print(f"\n{prefix} {message}\n")


def format_history_row(item: dict) -> str:
    """Formata um registro de histórico em uma linha legível."""
    return (
        f"{item['data']} {item['hora']} | "
        f"{item['status'].upper():7} | "
        f"{item['tempo_execucao_ms']:>8.2f} ms | "
        f"{item['comando']}"
    )
