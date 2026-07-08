"""
main.py — Ponto de entrada da Automação Universal.

Responsável apenas por:
    1. Exibir o menu.
    2. Ler a escolha do usuário.
    3. Delegar para a função correta (commands.py).
    4. Tratar interrupções de teclado e erros inesperados.

Executar com:  python main.py
"""

from __future__ import annotations

import sys

from commands import MENU_ACTIONS, free_command
from config import ensure_directories
from logger import get_logger
from utils import LINE, print_header

logger = get_logger("main")

MENU = f"""{LINE}
 1 - Abrir aplicativo
 2 - Abrir pasta
 3 - Abrir arquivo
 4 - Abrir URL
 5 - Histórico
 6 - Estatísticas
 7 - Pesquisar comando
 8 - Limpar tela
 9 - Ajuda
 0 - Sair
{LINE}
Dica: você também pode digitar direto, ex.: abrir chrome
"""


def main() -> int:
    """Loop principal do programa.

    Returns:
        Código de saída do processo (0 = sucesso).
    """
    ensure_directories()
    print_header()
    logger.info("Aplicação iniciada.")

    while True:
        print(MENU)
        try:
            escolha = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C / Ctrl+D: encerra com elegância, sem traceback.
            print("\n\nEncerrando. Até logo!")
            logger.info("Aplicação encerrada pelo teclado.")
            return 0

        if escolha == "0" or escolha.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            logger.info("Aplicação encerrada pelo menu.")
            return 0

        try:
            if escolha in MENU_ACTIONS:
                MENU_ACTIONS[escolha]()
            elif escolha:
                # Qualquer outro texto é tratado como comando livre.
                free_command(escolha)
        except Exception as exc:  # noqa: BLE001 — barreira final de erros
            # Nenhum erro inesperado deve derrubar o programa.
            print(f"\n[ERRO INESPERADO] {exc}\n")
            logger.exception("Erro inesperado no loop principal.")


if __name__ == "__main__":
    sys.exit(main())
