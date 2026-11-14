"""Validacao do JSON de analise contra o schema versionado."""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = Path(__file__).resolve().parent / "schemas" / "analise_v1.json"


def carregar_schema() -> dict:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validar(dados: dict) -> None:
    from jsonschema import Draft202012Validator, FormatChecker

    schema = carregar_schema()
    Draft202012Validator.check_schema(schema)
    validador = Draft202012Validator(schema, format_checker=FormatChecker())
    erros = sorted(validador.iter_errors(dados), key=lambda e: list(e.path))
    if not erros:
        return
    linhas = []
    for erro in erros[:20]:
        caminho = ".".join(str(p) for p in erro.path) or "<raiz>"
        linhas.append(f"{caminho}: {erro.message}")
    raise ValueError("JSON invalido:\n" + "\n".join(linhas))
