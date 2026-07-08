"""
json_manager.py — Camada de acesso ao arquivo JSON único.

Responsabilidade ÚNICA (princípio S do SOLID): ler e gravar o arquivo
data/database.json de forma segura, tratando corrupção e criando a
estrutura inicial quando o arquivo não existe.

Nenhum outro módulo deve abrir o JSON diretamente — todos passam por aqui.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from typing import Any

from config import DATABASE_FILE, ensure_directories
from logger import get_logger

logger = get_logger("json_manager")

# Estrutura inicial (esquema) do banco de dados JSON.
DEFAULT_STRUCTURE: dict[str, Any] = {
    "meta": {
        "criado_em": None,          # preenchido na criação
        "ultima_atualizacao": None,
        "versao_esquema": "1.0",
    },
    "historico": [],                # lista de registros de execução
    "contadores": {},               # comando → quantidade de usos
    "ultimo_acesso": {},            # comando → data/hora do último uso
}


def _now() -> str:
    """Retorna a data/hora atual em formato ISO legível."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _create_default_file() -> dict[str, Any]:
    """Cria o database.json com a estrutura padrão e o retorna."""
    data = json.loads(json.dumps(DEFAULT_STRUCTURE))  # cópia profunda simples
    data["meta"]["criado_em"] = _now()
    data["meta"]["ultima_atualizacao"] = _now()
    save_data(data)
    logger.info("database.json criado com estrutura padrão.")
    return data


def load_data() -> dict[str, Any]:
    """Carrega o banco de dados JSON.

    Tratamentos:
        - Arquivo inexistente  → cria estrutura padrão.
        - JSON corrompido      → faz backup do corrompido e recria.

    Returns:
        dict com todo o conteúdo do banco.
    """
    ensure_directories()

    if not DATABASE_FILE.exists():
        return _create_default_file()

    try:
        with DATABASE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Arquivo corrompido: preserva uma cópia para auditoria
        # e recria o banco (nunca perder dados silenciosamente).
        backup = DATABASE_FILE.with_suffix(".corrompido.bak")
        shutil.copy2(DATABASE_FILE, backup)
        logger.error("JSON corrompido. Backup salvo em %s. Recriando banco.", backup)
        return _create_default_file()
    except PermissionError:
        logger.error("Permissão negada ao ler %s.", DATABASE_FILE)
        raise


def save_data(data: dict[str, Any]) -> None:
    """Grava o banco inteiro em disco, atualizando o carimbo de tempo.

    A escrita é feita primeiro em arquivo temporário e depois movida
    (escrita atômica): se o programa cair no meio da gravação, o JSON
    original não fica corrompido.
    """
    ensure_directories()
    data.setdefault("meta", {})["ultima_atualizacao"] = _now()

    tmp_file = DATABASE_FILE.with_suffix(".tmp")
    try:
        with tmp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        tmp_file.replace(DATABASE_FILE)
    except PermissionError:
        logger.error("Permissão negada ao gravar %s.", DATABASE_FILE)
        raise
