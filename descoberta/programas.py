#!/usr/bin/env python3
"""CLI de descoberta de programas. Somente leitura.

Uso:
    py -3.12 descoberta/programas.py
    py -3.12 descoberta/programas.py --sem-varredura
    py -3.12 descoberta/programas.py --salvar

A gravacao de resultado_varredura.json exige --salvar. O proprio arquivo fica
marcado com confirmado_pelo_usuario=false ate a revisao humana.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent
RAIZ = DIR.parent
sys.path.insert(0, str(DIR))

import varredura  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Descoberta local de programas (somente leitura).")
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=180.0,
        help="prazo maximo da varredura de disco (padrao: 180 s)",
    )
    parser.add_argument(
        "--sem-varredura",
        action="store_true",
        help="nao varre o disco; usa config, PATH, registro e pastas comuns",
    )
    parser.add_argument("--salvar", action="store_true", help="grava descoberta/resultado_varredura.json")
    parser.add_argument(
        "--confirmado",
        action="store_true",
        help="marca o resultado como confirmado pelo usuario (exige --salvar)",
    )
    parser.add_argument("--json", action="store_true", help="imprime JSON em vez de tabela")
    args = parser.parse_args()
    if args.confirmado and not args.salvar:
        parser.error("--confirmado exige --salvar")

    dados = varredura.descobrir_tudo(
        raiz_projeto=RAIZ,
        max_seconds=args.max_seconds,
        fazer_varredura=not args.sem_varredura,
    )

    if args.json:
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    else:
        print(varredura.formatar_tabela(dados["resultados"]))
        stats = dados["estatisticas"]
        print()
        print(
            "Pastas varridas: {pastas} | erros de acesso: {erros} | "
            "duracao: {duracao_total_s}s | concluida no prazo: {concluida}".format(**stats)
        )
        if args.salvar:
            destino = DIR / "resultado_varredura.json"
            varredura.salvar_resultado(dados, destino, confirmado=args.confirmado)
            print(
                f"OK: {destino} "
                f"(confirmado_pelo_usuario={'true' if args.confirmado else 'false'})"
            )
        else:
            print("NAO SALVO: revise a tabela e rode com --salvar apos confirmar.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
