"""
config.py — Configurações centrais do projeto Automação Universal.

Este módulo concentra TODAS as constantes, caminhos e mapeamentos de
aplicativos do sistema. Centralizar configuração em um único módulo é
uma boa prática de Clean Code: se algo precisa mudar (um caminho, um
alias de aplicativo), muda-se em UM lugar só.

Conceitos utilizados:
    - pathlib.Path  → manipulação de caminhos independente de SO
    - enum.Enum     → tipos enumerados seguros (sistema operacional)
    - platform      → detecção do sistema operacional em execução
"""

from __future__ import annotations

import platform
from enum import Enum
from pathlib import Path

# --------------------------------------------------------------------------
# Diretórios base do projeto
# --------------------------------------------------------------------------

# Path(__file__) é o caminho deste arquivo; .parent é a pasta do projeto.
BASE_DIR: Path = Path(__file__).resolve().parent

DATA_DIR: Path = BASE_DIR / "data"
LOGS_DIR: Path = BASE_DIR / "logs"
ASSETS_DIR: Path = BASE_DIR / "assets"

# Arquivo ÚNICO de banco de dados JSON (requisito do projeto).
DATABASE_FILE: Path = DATA_DIR / "database.json"

# Arquivo único de log.
LOG_FILE: Path = LOGS_DIR / "app.log"

APP_NAME: str = "AUTOMAÇÃO UNIVERSAL"
APP_VERSION: str = "1.0.0"


# --------------------------------------------------------------------------
# Sistema operacional
# --------------------------------------------------------------------------

class OperatingSystem(Enum):
    """Enumeração dos sistemas operacionais suportados.

    Usar Enum evita "strings mágicas" espalhadas pelo código
    (ex.: comparar com "windows" escrito de formas diferentes).
    """

    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "Darwin"  # platform.system() retorna "Darwin" no macOS
    UNKNOWN = "Unknown"


def detect_os() -> OperatingSystem:
    """Detecta o sistema operacional atual.

    Returns:
        OperatingSystem: membro do Enum correspondente ao SO em execução.
    """
    system = platform.system()
    for os_member in OperatingSystem:
        if os_member.value == system:
            return os_member
    return OperatingSystem.UNKNOWN


CURRENT_OS: OperatingSystem = detect_os()


# --------------------------------------------------------------------------
# Pastas especiais do usuário (multiplataforma)
# --------------------------------------------------------------------------

HOME: Path = Path.home()

SPECIAL_FOLDERS: dict[str, Path] = {
    "downloads": HOME / "Downloads",
    "desktop": HOME / "Desktop",
    "documentos": HOME / "Documents",
    "documents": HOME / "Documents",
    "imagens": HOME / "Pictures",
    "pictures": HOME / "Pictures",
    "videos": HOME / "Videos",
    "musicas": HOME / "Music",
    "músicas": HOME / "Music",
    "music": HOME / "Music",
    "home": HOME,
    "pasta pessoal": HOME,
}


# --------------------------------------------------------------------------
# Sites conhecidos (abertos no navegador padrão)
# --------------------------------------------------------------------------

KNOWN_SITES: dict[str, str] = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "claude": "https://claude.ai",
    "chatgpt": "https://chat.openai.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "whatsapp web": "https://web.whatsapp.com",
    "linkedin": "https://www.linkedin.com",
    "stackoverflow": "https://stackoverflow.com",
    "openai": "https://openai.com",
    "python docs": "https://docs.python.org/pt-br/3/",
}


# --------------------------------------------------------------------------
# Aplicativos conhecidos por sistema operacional
# --------------------------------------------------------------------------
# A estrutura é: alias digitado pelo usuário → comando/executável real.
# Cada SO tem seu próprio dicionário porque os nomes dos executáveis mudam.

APPS_WINDOWS: dict[str, str] = {
    "chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "opera": "opera",
    "vscode": "code",
    "visual studio": "devenv",
    "spotify": "spotify",
    "steam": "steam",
    "discord": "discord",
    "whatsapp": "whatsapp",
    "calculadora": "calc",
    "bloco de notas": "notepad",
    "notepad": "notepad",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "cmd": "cmd",
    "terminal": "wt",
    "powershell": "powershell",
    "explorador": "explorer",
    "explorer": "explorer",
    "python": "python",
    "lixeira": "shell:RecycleBinFolder",
}

APPS_LINUX: dict[str, str] = {
    "chrome": "google-chrome",
    "firefox": "firefox",
    "edge": "microsoft-edge",
    "opera": "opera",
    "vscode": "code",
    "spotify": "spotify",
    "steam": "steam",
    "discord": "discord",
    "calculadora": "gnome-calculator",
    "bloco de notas": "gedit",
    "terminal": "gnome-terminal",
    "explorador": "nautilus",
    "explorer": "nautilus",
    "python": "python3",
    "lixeira": "trash:///",
}

APPS_MACOS: dict[str, str] = {
    "chrome": "Google Chrome",
    "firefox": "Firefox",
    "edge": "Microsoft Edge",
    "opera": "Opera",
    "vscode": "Visual Studio Code",
    "spotify": "Spotify",
    "steam": "Steam",
    "discord": "Discord",
    "whatsapp": "WhatsApp",
    "calculadora": "Calculator",
    "bloco de notas": "TextEdit",
    "word": "Microsoft Word",
    "excel": "Microsoft Excel",
    "powerpoint": "Microsoft PowerPoint",
    "terminal": "Terminal",
    "finder": "Finder",
    "explorador": "Finder",
    "python": "python3",
}


def get_apps_map() -> dict[str, str]:
    """Retorna o dicionário de aplicativos do SO atual.

    Usa a estrutura match/case (Python 3.10+), equivalente moderno
    de uma cadeia de if/elif, porém mais legível.
    """
    match CURRENT_OS:
        case OperatingSystem.WINDOWS:
            return APPS_WINDOWS
        case OperatingSystem.MACOS:
            return APPS_MACOS
        case OperatingSystem.LINUX:
            return APPS_LINUX
        case _:
            return {}


def ensure_directories() -> None:
    """Garante que as pastas data/, logs/ e assets/ existam.

    parents=True cria pastas intermediárias; exist_ok=True evita erro
    se a pasta já existir (idempotência).
    """
    for directory in (DATA_DIR, LOGS_DIR, ASSETS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
