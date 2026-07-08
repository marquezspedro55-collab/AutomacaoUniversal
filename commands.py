"""
commands.py — Ações do menu interativo.

Cada opção do menu vira uma função pequena e focada. O main.py apenas
mapeia a escolha do usuário para a função correspondente (padrão
Command simplificado, usando dicionário de funções).
"""

from __future__ import annotations

from history import search_history, show_history, show_statistics
from launcher import launch
from parser import parse
from utils import clear_screen, print_header, print_result


def _open_generic(prompt: str) -> None:
    """Fluxo comum: pede um alvo, interpreta e executa."""
    alvo = input(prompt).strip()
    if not alvo:
        print("Nada informado.\n")
        return
    result = launch(parse(alvo))
    print_result(result.success, result.message)


def open_app() -> None:
    """Opção 1 — abrir aplicativo pelo nome."""
    _open_generic("Nome do aplicativo (ex.: chrome, vscode, calculadora): ")


def open_folder() -> None:
    """Opção 2 — abrir pasta (especial ou caminho completo)."""
    _open_generic("Pasta (ex.: downloads, desktop ou /caminho/completo): ")


def open_file() -> None:
    """Opção 3 — abrir arquivo pelo caminho."""
    _open_generic("Caminho do arquivo: ")


def open_url() -> None:
    """Opção 4 — abrir URL ou site conhecido."""
    _open_generic("URL ou site (ex.: google, youtube, https://...): ")


def free_command(texto: str) -> None:
    """Comando livre digitado direto no menu (ex.: 'abrir chrome')."""
    result = launch(parse(texto))
    print_result(result.success, result.message)


def clear() -> None:
    """Opção 8 — limpar a tela e reexibir o cabeçalho."""
    clear_screen()
    print_header()


def show_help() -> None:
    """Opção 9 — exibe a ajuda do programa."""
    print(
        """
AJUDA — AUTOMAÇÃO UNIVERSAL
---------------------------------------------
Você pode usar as opções numeradas do menu OU
digitar comandos livres diretamente, como:

    abrir chrome
    abrir youtube
    abrir downloads
    abrir bloco de notas
    abrir https://github.com
    abrir C:/Users/voce/Documents/arquivo.pdf
    abrir /home/voce/projetos

O programa detecta sozinho se o alvo é um
aplicativo, pasta, arquivo ou URL, e usa o
mecanismo correto do seu sistema operacional
(Windows, Linux ou macOS).

Todos os comandos ficam registrados em
data/database.json (histórico, contadores e
estatísticas) e em logs/app.log.
"""
    )


# Mapeamento opção → função (usado pelo main.py).
MENU_ACTIONS: dict[str, callable] = {
    "1": open_app,
    "2": open_folder,
    "3": open_file,
    "4": open_url,
    "5": show_history,
    "6": show_statistics,
    "7": search_history,
    "8": clear,
    "9": show_help,
}
