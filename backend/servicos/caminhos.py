"""Caminhos compartilhados pelo backend do M2.

Todos os caminhos sao absolutos e derivados da raiz do projeto de forma
estatica, para que o backend funcione com qualquer diretorio de trabalho.
"""
from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
RAIZ = BACKEND_DIR.parent

PROJETOS_DIR = RAIZ / "projetos"
DESCOBERTA_DIR = RAIZ / "descoberta"
DOCS_DIR = RAIZ / "docs"

CONFIG_JSON = RAIZ / "config.json"
PERFIL_HARDWARE = RAIZ / "perfil_hardware.json"
RESULTADO_VARREDURA = DESCOBERTA_DIR / "resultado_varredura.json"
MODELOS_ENCONTRADOS = DESCOBERTA_DIR / "modelos_encontrados.json"

FRONTEND_DIST = RAIZ / "frontend" / "dist"

BANCO_FILA = BACKEND_DIR / "fila.sqlite3"

VENV_PYTHON = RAIZ / ".venv" / "Scripts" / "python.exe"
FFMPEG = RAIZ / "tools" / "ffmpeg" / "ffmpeg.exe"
FFPROBE = RAIZ / "tools" / "ffmpeg" / "ffprobe.exe"


def projeto_dir(projeto_id: str) -> Path:
    """Pasta do projeto dentro de ``projetos/``."""
    return PROJETOS_DIR / projeto_id


def caminho_relativo(caminho: Path) -> str:
    """Caminho relativo a raiz do projeto, com ``/`` (regra do contrato M2)."""
    try:
        return caminho.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return caminho.as_posix()
