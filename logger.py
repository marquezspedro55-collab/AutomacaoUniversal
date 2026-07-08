"""
logger.py — Configuração centralizada de logs.

Cria e configura um logger único para toda a aplicação, gravando em
logs/app.log com data, hora, nível e mensagem. Todos os módulos devem
obter o logger via get_logger() em vez de configurar o logging por
conta própria (padrão Singleton implícito do módulo logging).
"""

from __future__ import annotations

import logging

from config import LOG_FILE, ensure_directories

# Formato: 2026-07-07 14:32:11 | INFO | launcher | Aplicativo aberto: chrome
_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(module)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False  # Flag de módulo para configurar apenas uma vez.


def get_logger(name: str = "automacao") -> logging.Logger:
    """Retorna o logger da aplicação, configurando-o na primeira chamada.

    Args:
        name: nome do logger (aparece na hierarquia do logging).

    Returns:
        logging.Logger pronto para uso (logger.info, logger.error...).
    """
    global _configured
    if not _configured:
        ensure_directories()
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))

        root = logging.getLogger("automacao")
        root.setLevel(logging.INFO)
        root.addHandler(handler)
        _configured = True

    return logging.getLogger(name if name.startswith("automacao") else f"automacao.{name}")
