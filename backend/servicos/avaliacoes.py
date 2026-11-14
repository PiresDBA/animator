"""Avaliacoes humanas (contrato M2, secao 4.2).

``decisao`` em ``aprovar | ajustar | reprovar``.
``notas`` com cinco chaves inteiras de 1 a 5.
Ids sequenciais ``av_001``, ``av_002``, ...
"""
from __future__ import annotations

from typing import Any

from . import projetos
from .caminhos import projeto_dir
from .eventos import agora

DECISOES = ("aprovar", "ajustar", "reprovar")
CHAVES_NOTAS = (
    "fidelidade",
    "identidade_visual",
    "fluidez",
    "adequacao_infantil",
    "clareza_historia",
)

ALIAS_CRITERIOS = {
    "atencao_infantil": "adequacao_infantil",
    "clareza_cenas": "clareza_historia",
    "estilo_consistente": "identidade_visual",
    "ausencia_artefatos": "fluidez",
}


class ErroAvaliacao(Exception):
    """Dados de avaliacao invalidos."""


def ler(projeto_id: str) -> list[dict[str, Any]]:
    """Lista de avaliacoes de um projeto."""
    dados = projetos.ler_json(projeto_dir(projeto_id) / "avaliacoes.json")
    if isinstance(dados, dict):
        lista = dados.get("avaliacoes")
        if isinstance(lista, list):
            return [item for item in lista if isinstance(item, dict)]
    if isinstance(dados, list):
        return [item for item in dados if isinstance(item, dict)]
    return []


def _proximo_id(avaliacoes: list[dict[str, Any]]) -> str:
    maior = 0
    for item in avaliacoes:
        identificador = str(item.get("id") or "")
        if identificador.startswith("av_"):
            try:
                maior = max(maior, int(identificador[3:]))
            except ValueError:
                continue
    return f"av_{maior + 1:03d}"


def validar(dados: dict[str, Any]) -> dict[str, Any]:
    """Valida e normaliza uma avaliacao (sem gravar)."""
    decisao = str(dados.get("decisao") or "").strip().lower()
    if decisao not in DECISOES:
        raise ErroAvaliacao(
            "Decisao invalida. Valores aceitos: "
            + ", ".join(DECISOES)
            + "."
        )

    notas = dados.get("notas")
    if not isinstance(notas, dict):
        raise ErroAvaliacao(
            "Informe as notas de 1 a 5 para: " + ", ".join(CHAVES_NOTAS) + "."
        )

    # Mapeia aliases para as chaves canonicas
    notas_normalizadas: dict[str, Any] = {}
    for chave, valor in notas.items():
        chave_canonica = ALIAS_CRITERIOS.get(chave, chave)
        notas_normalizadas[chave_canonica] = valor

    notas_limpas: dict[str, int] = {}
    for chave in CHAVES_NOTAS:
        if chave not in notas_normalizadas:
            raise ErroAvaliacao(f"A nota '{chave}' e obrigatoria (valores de 1 a 5).")
        valor = notas_normalizadas[chave]
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ErroAvaliacao(f"A nota '{chave}' deve ser um numero inteiro de 1 a 5.")
        if float(valor) != int(valor):
            raise ErroAvaliacao(f"A nota '{chave}' deve ser um numero inteiro de 1 a 5.")
        inteiro = int(valor)
        if inteiro < 1 or inteiro > 5:
            raise ErroAvaliacao(f"A nota '{chave}' deve estar entre 1 e 5.")
        notas_limpas[chave] = inteiro
    for chave in notas_normalizadas:
        if chave not in CHAVES_NOTAS:
            raise ErroAvaliacao(
                f"Nota desconhecida '{chave}'. Use apenas: " + ", ".join(CHAVES_NOTAS) + "."
            )

    return notas_limpas


def salvar(projeto_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    """Grava uma avaliacao e devolve o registro salvo."""
    if not projetos.existe(projeto_id):
        raise ErroAvaliacao(f"Projeto nao encontrado: {projeto_id}")

    notas = validar(dados)
    avaliacoes = ler(projeto_id)

    raw_params = dados.get("params") if isinstance(dados.get("params"), dict) else {}
    params = {
        "seed": raw_params.get("seed", 7),
        "resolucao": raw_params.get("resolucao", "480p"),
        "modo": raw_params.get("modo", "rapido"),
        "versao_preset": raw_params.get("versao_preset", 1),
        "trecho_inicio": raw_params.get("trecho_inicio", 0.0),
        "trecho_fim": raw_params.get("trecho_fim", 5.0),
    }

    registro: dict[str, Any] = {
        "id": _proximo_id(avaliacoes),
        "previa_id": dados.get("previa_id") or dados.get("preview_id"),
        "estilo": dados.get("estilo"),
        "data": agora(),
        "decisao": str(dados.get("decisao") or "").strip().lower(),
        "notas": notas,
        "comentario": dados.get("comentario"),
        "params": params,
        "observacao_responsavel": dados.get("observacao_responsavel"),
    }

    avaliacoes.append(registro)
    projetos.gravar_json(
        projeto_dir(projeto_id) / "avaliacoes.json",
        {"versao": 1, "avaliacoes": avaliacoes},
    )

    if registro["decisao"] == "aprovar":
        meta = projetos.meta(projeto_id) or {}
        meta["aprovado"] = True
        meta["aprovacao"] = {
            "avaliacao_id": registro["id"],
            "estilo": registro["estilo"],
            "previa_id": registro["previa_id"],
            "data": registro["data"],
        }
        meta["status"] = "aprovado"
        projetos.salvar_meta(projeto_id, meta)

    return registro


def tem_aprovacao(projeto_id: str) -> dict[str, Any] | None:
    """Devolve a avaliacao de aprovacao mais recente (ou ``None``)."""
    aprovacoes = [item for item in ler(projeto_id) if item.get("decisao") == "aprovar"]
    if not aprovacoes:
        return None
    return aprovacoes[-1]
