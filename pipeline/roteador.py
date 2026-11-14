"""Roteador de tecnicas por cena (secao 8 do prompt mestre).

Analisa cada cena de um projeto e define a tecnica indicada e o motivo.
No Marco M2, para o estilo de bonecos de palito, direciona para a tecnica 'bonecos'.

CLI:
    python -m pipeline.roteador --projeto ID
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pipeline import cache

RAIZ = cache.CONFIG["raiz"]


def rotear_cenas(cenas: list[dict[str, Any]], estilo_padrao: str = "bonecos") -> list[dict[str, Any]]:
    """Gera o mapa de tecnicas para cada cena."""
    mapa: list[dict[str, Any]] = []
    for idx, c in enumerate(cenas):
        cena_id = c.get("id") or f"c{idx + 1:02d}"
        pessoas = c.get("pessoas", 0)
        movimento = c.get("movimento") or "suave"

        if estilo_padrao == "bonecos":
            tecnica = "bonecos"
            motivo = (
                f"Cena {cena_id}: estilo bonecos de palito selecionado com "
                f"movimento '{movimento}' e {pessoas} ator(es)."
            )
        else:
            if movimento == "suave":
                tecnica = "2.5d"
                motivo = "Movimento suave com profundidade util."
            else:
                tecnica = "rapido"
                motivo = "Acao moderada direcionada para modo rapido."

        mapa.append({
            "id": cena_id,
            "tecnica": tecnica,
            "motivo": motivo,
        })

    if not mapa:
        mapa.append({
            "id": "c01",
            "tecnica": estilo_padrao,
            "motivo": f"Cena unica direcionada para {estilo_padrao}.",
        })
    return mapa


def executar(projeto_id: str, estilo_padrao: str = "bonecos") -> Path:
    """Executa o roteador no projeto e grava mapa_tecnicas.json."""
    pasta_projeto = RAIZ / "projetos" / projeto_id
    if not pasta_projeto.is_dir():
        raise FileNotFoundError(f"Pasta do projeto nao encontrada: {pasta_projeto}")

    caminho_cenas = pasta_projeto / "cenas.json"
    cenas: list[dict[str, Any]] = []
    if caminho_cenas.is_file():
        try:
            dados = json.loads(caminho_cenas.read_text(encoding="utf-8"))
            if isinstance(dados, dict):
                cenas = dados.get("cenas") or []
            elif isinstance(dados, list):
                cenas = dados
        except (json.JSONDecodeError, OSError):
            cenas = []

    cenas_roteadas = rotear_cenas(cenas, estilo_padrao)
    resultado = {
        "versao": 1,
        "projeto": projeto_id,
        "cenas": cenas_roteadas,
    }

    caminho_saida = pasta_projeto / "mapa_tecnicas.json"
    caminho_saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return caminho_saida


def main() -> None:
    parser = argparse.ArgumentParser(description="Roteador de tecnicas por cena.")
    parser.add_argument("--projeto", required=True, help="ID do projeto")
    parser.add_argument("--estilo", default="bonecos", help="Estilo alvo (padrao: bonecos)")
    args = parser.parse_args()

    try:
        saida = executar(args.projeto, args.estilo)
        try:
            relativo = saida.resolve().relative_to(RAIZ).as_posix()
        except ValueError:
            relativo = saida.as_posix()
        print(f"OK: {relativo}")
        sys.exit(0)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
