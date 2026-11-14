"""Leitura (somente leitura) do hardware e dos programas descobertos.

Fontes:
- ``perfil_hardware.json`` (raiz do projeto)
- ``descoberta/resultado_varredura.json``
- ``descoberta/modelos_encontrados.json``
- ``config.json`` (caminhos configurados)

Nenhum arquivo e escrito por este modulo.
"""
from __future__ import annotations

from typing import Any

from . import projetos
from .caminhos import (
    CONFIG_JSON,
    MODELOS_ENCONTRADOS,
    PERFIL_HARDWARE,
    RESULTADO_VARREDURA,
)

ROTULOS = {
    "comfyui": "ComfyUI",
    "motor_bonecos": "Motor de bonecos de palito",
    "effectcraft": "EffectCraft",
    "videofactoryai": "VideoFactoryAI",
    "ffmpeg": "FFmpeg",
    "remotion": "Remotion",
}


def perfil() -> dict[str, Any]:
    """Conteudo de ``perfil_hardware.json``."""
    dados = projetos.ler_json(PERFIL_HARDWARE)
    return dados if isinstance(dados, dict) else {}


def varredura() -> dict[str, Any]:
    """Conteudo de ``descoberta/resultado_varredura.json``."""
    dados = projetos.ler_json(RESULTADO_VARREDURA)
    return dados if isinstance(dados, dict) else {}


def modelos() -> dict[str, Any]:
    """Conteudo de ``descoberta/modelos_encontrados.json``."""
    dados = projetos.ler_json(MODELOS_ENCONTRADOS)
    return dados if isinstance(dados, dict) else {}


def config() -> dict[str, Any]:
    """Conteudo de ``config.json``."""
    dados = projetos.ler_json(CONFIG_JSON)
    return dados if isinstance(dados, dict) else {}


def programas() -> dict[str, Any]:
    """Resumo por tipo de programa encontrado na varredura."""
    dados = varredura()
    resultados = dados.get("resultados")
    agrupado: dict[str, dict[str, Any]] = {}
    if isinstance(resultados, list):
        for item in resultados:
            if not isinstance(item, dict):
                continue
            tipo = str(item.get("tipo") or "outros")
            entrada = agrupado.setdefault(
                tipo,
                {
                    "tipo": tipo,
                    "rotulo": ROTULOS.get(tipo, tipo),
                    "disponivel": False,
                    "caminhos": [],
                },
            )
            caminho = item.get("caminho")
            if caminho:
                entrada["caminhos"].append(str(caminho))
            entrada["disponivel"] = True

    caminhos_config = (config().get("caminhos") or {})
    for tipo, caminho in caminhos_config.items():
        entrada = agrupado.setdefault(
            str(tipo),
            {
                "tipo": str(tipo),
                "rotulo": ROTULOS.get(str(tipo), str(tipo)),
                "disponivel": False,
                "caminhos": [],
            },
        )
        if caminho and str(caminho) not in entrada["caminhos"]:
            entrada["caminhos"].append(str(caminho))
            entrada["disponivel"] = True

    return {
        "varredura_confirmada": bool(dados.get("confirmado_pelo_usuario")),
        "gerado_em": dados.get("gerado_em"),
        "estatisticas": dados.get("estatisticas") or {},
        "itens": sorted(agrupado.values(), key=lambda item: item["tipo"]),
        "modelos": modelos().get("resumo") or {},
    }


def resumo() -> dict[str, Any]:
    """Resumo compacto do hardware para a barra superior e ``/api/estado``."""
    dados = perfil()
    computador = dados.get("computador") or {}
    cpu = dados.get("cpu") or {}
    gpu = dados.get("gpu") or {}
    gpus = gpu.get("gpus") or []
    principal = gpus[0] if gpus else {}
    discos = dados.get("discos") or []
    return {
        "coletado_em": dados.get("coletado_em"),
        "sistema": dados.get("sistema") or {},
        "computador": {
            "fabricante": computador.get("fabricante"),
            "modelo": computador.get("modelo"),
            "ram_gb": computador.get("ram_gb"),
        },
        "cpu": {"nome": cpu.get("nome"), "nucleos": cpu.get("nucleos")},
        "gpu": {
            "disponivel": bool(gpu.get("disponivel")),
            "nome": principal.get("nome"),
            "vram_total_mib": principal.get("vram_total_mib"),
            "vram_usada_mib": principal.get("vram_usada_mib"),
            "temperatura_c": principal.get("temperatura_c"),
            "utilizacao_pct": principal.get("utilizacao_pct"),
        },
        "discos": discos,
        "ferramentas": dados.get("ferramentas") or {},
    }
