"""
launcher.py — Execução real dos comandos (abrir coisas).

Recebe um ParsedCommand e efetivamente abre o alvo usando o mecanismo
correto de cada sistema operacional:

    Windows → os.startfile / start
    macOS   → open / open -a
    Linux   → xdg-open

Bibliotecas usadas:
    subprocess  → executar programas externos sem bloquear o terminal
    webbrowser  → abrir URLs no navegador padrão do usuário
    shutil.which→ verificar se um executável existe no PATH
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path

from config import CURRENT_OS, OperatingSystem
from database import register_execution
from logger import get_logger
from parser import ParsedCommand, TargetType

logger = get_logger("launcher")


@dataclass
class LaunchResult:
    """Resultado de uma tentativa de abertura."""

    success: bool
    message: str


# --------------------------------------------------------------------------
# Aberturas específicas por tipo
# --------------------------------------------------------------------------

def _open_url(url: str) -> LaunchResult:
    """Abre uma URL no navegador padrão do usuário."""
    try:
        ok = webbrowser.open(url)
        if ok:
            return LaunchResult(True, f"URL aberta no navegador: {url}")
        return LaunchResult(False, f"Nenhum navegador conseguiu abrir: {url}")
    except webbrowser.Error as exc:
        return LaunchResult(False, f"Erro do navegador: {exc}")


def _open_path(path_str: str) -> LaunchResult:
    """Abre uma pasta ou arquivo com o aplicativo padrão do SO."""
    path = Path(path_str)
    if not path.exists():
        return LaunchResult(False, f"Caminho inexistente: {path}")

    try:
        match CURRENT_OS:
            case OperatingSystem.WINDOWS:
                os.startfile(str(path))  # type: ignore[attr-defined]
            case OperatingSystem.MACOS:
                subprocess.Popen(["open", str(path)])
            case OperatingSystem.LINUX:
                subprocess.Popen(["xdg-open", str(path)])
            case _:
                return LaunchResult(False, "Sistema operacional não suportado.")
        msg = "Pasta aberta" if path.is_dir() else "Arquivo aberto"
        return LaunchResult(True, f"{msg}: {path}")
    except PermissionError:
        return LaunchResult(False, f"Permissão negada para abrir: {path}")
    except OSError as exc:
        return LaunchResult(False, f"Erro do sistema ao abrir {path}: {exc}")


def _open_app(app: str) -> LaunchResult:
    """Abre um aplicativo pelo nome/executável, conforme o SO."""
    try:
        match CURRENT_OS:
            case OperatingSystem.WINDOWS:
                # 'start' resolve apps registrados, atalhos e URIs especiais.
                subprocess.Popen(f'start "" "{app}"', shell=True)
            case OperatingSystem.MACOS:
                # 'open -a' abre aplicativos da pasta /Applications pelo nome.
                subprocess.Popen(["open", "-a", app])
            case OperatingSystem.LINUX:
                if shutil.which(app) is None:
                    return LaunchResult(
                        False, f"Aplicativo '{app}' não encontrado no PATH."
                    )
                subprocess.Popen(
                    [app],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            case _:
                return LaunchResult(False, "Sistema operacional não suportado.")
        return LaunchResult(True, f"Aplicativo iniciado: {app}")
    except FileNotFoundError:
        return LaunchResult(False, f"Aplicativo não encontrado: {app}")
    except PermissionError:
        return LaunchResult(False, f"Permissão negada para executar: {app}")
    except OSError as exc:
        return LaunchResult(False, f"Erro ao iniciar '{app}': {exc}")


# --------------------------------------------------------------------------
# Ponto de entrada do launcher
# --------------------------------------------------------------------------

def launch(command: ParsedCommand) -> LaunchResult:
    """Executa um ParsedCommand, mede o tempo e registra no banco JSON.

    O registro acontece SEMPRE — sucesso ou erro — para que o histórico
    e as estatísticas reflitam a realidade de uso.
    """
    start = time.perf_counter()  # relógio de alta precisão para medir duração

    match command.type:
        case TargetType.URL:
            result = _open_url(command.target)
        case TargetType.FOLDER | TargetType.FILE:
            result = _open_path(command.target)
        case TargetType.APP:
            result = _open_app(command.target)
        case TargetType.UNKNOWN:
            if not command.target:
                result = LaunchResult(False, "Nenhum alvo informado.")
            else:
                # Última tentativa: tratar como aplicativo genérico.
                result = _open_app(command.target)
                if not result.success:
                    result = LaunchResult(
                        False,
                        f"Não consegui encontrar '{command.target}'. "
                        "Verifique o nome, o caminho ou a URL e tente novamente.",
                    )
        case _:
            result = LaunchResult(False, "Tipo de comando não reconhecido.")

    elapsed_ms = (time.perf_counter() - start) * 1000

    status = "sucesso" if result.success else "erro"
    register_execution(
        comando=command.raw,
        tipo=command.type.value,
        alvo=command.target,
        status=status,
        resultado=result.message,
        tempo_execucao_ms=elapsed_ms,
    )

    log = logger.info if result.success else logger.error
    log("%s | %.2f ms | %s", command.raw, elapsed_ms, result.message)

    return result
