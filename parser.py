"""
parser.py — Interpretação dos comandos digitados pelo usuário.

Transforma texto livre ("abrir chrome", "abrir C:/Users/x/doc.pdf",
"abrir https://github.com") em uma intenção estruturada (ParsedCommand),
que o launcher sabe executar.

Este módulo NÃO abre nada — apenas interpreta (separação de responsabilidades).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from config import KNOWN_SITES, SPECIAL_FOLDERS, get_apps_map


class TargetType(Enum):
    """Tipo de alvo identificado no comando do usuário."""

    APP = "app"
    FOLDER = "pasta"
    FILE = "arquivo"
    URL = "url"
    UNKNOWN = "desconhecido"


@dataclass
class ParsedCommand:
    """Resultado da interpretação de um comando.

    Attributes:
        raw:    texto original digitado.
        target: alvo resolvido (executável, caminho ou URL).
        type:   tipo do alvo (Enum TargetType).
    """

    raw: str
    target: str
    type: TargetType


def _looks_like_url(text: str) -> bool:
    """Heurística simples para identificar URLs."""
    lowered = text.lower()
    return lowered.startswith(("http://", "https://", "www.")) or (
        "." in lowered and " " not in lowered and lowered.endswith(
            (".com", ".com.br", ".org", ".net", ".ai", ".io", ".gov.br", ".dev")
        )
    )


def parse(raw_input: str) -> ParsedCommand:
    """Interpreta o texto do usuário e devolve um ParsedCommand.

    Ordem de resolução (da mais específica para a mais genérica):
        1. Caminho absoluto existente (pasta ou arquivo).
        2. URL explícita.
        3. Pasta especial do usuário (downloads, desktop...).
        4. Site conhecido (google, youtube, claude...).
        5. Aplicativo conhecido do SO atual.
        6. Caminho relativo existente.
        7. Desconhecido (tentativa genérica pelo launcher).
    """
    text = raw_input.strip()

    # Remove o verbo "abrir" (com ou sem acento em variações comuns).
    lowered = text.lower()
    if lowered.startswith("abrir "):
        text = text[6:].strip()
        lowered = text.lower()

    if not text:
        return ParsedCommand(raw_input, "", TargetType.UNKNOWN)

    # 1) Caminho absoluto informado pelo usuário
    path = Path(text).expanduser()
    if path.is_absolute() and path.exists():
        kind = TargetType.FOLDER if path.is_dir() else TargetType.FILE
        return ParsedCommand(raw_input, str(path), kind)

    # 2) URL explícita
    if _looks_like_url(lowered):
        url = text if lowered.startswith("http") else f"https://{text}"
        return ParsedCommand(raw_input, url, TargetType.URL)

    # 3) Pastas especiais (Downloads, Desktop, Documentos...)
    if lowered in SPECIAL_FOLDERS:
        return ParsedCommand(raw_input, str(SPECIAL_FOLDERS[lowered]), TargetType.FOLDER)
    if lowered.startswith("pasta "):
        nome = lowered[6:].strip()
        if nome in SPECIAL_FOLDERS:
            return ParsedCommand(raw_input, str(SPECIAL_FOLDERS[nome]), TargetType.FOLDER)

    # 4) Sites conhecidos
    if lowered in KNOWN_SITES:
        return ParsedCommand(raw_input, KNOWN_SITES[lowered], TargetType.URL)

    # 5) Aplicativos conhecidos do SO atual
    apps = get_apps_map()
    if lowered in apps:
        return ParsedCommand(raw_input, apps[lowered], TargetType.APP)

    # 6) Caminho relativo existente (ex.: "abrir relatorio.pdf")
    if path.exists():
        kind = TargetType.FOLDER if path.is_dir() else TargetType.FILE
        return ParsedCommand(raw_input, str(path.resolve()), kind)

    # 7) Não reconhecido: o launcher tentará abrir como aplicativo genérico.
    return ParsedCommand(raw_input, text, TargetType.UNKNOWN)
