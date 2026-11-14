#!/usr/bin/env python3
"""Inventario somente leitura dos modelos instalados no ComfyUI.

Uso:
    py -3.12 descoberta/modelos.py --comfyui "D:\\Comfy\\ComfyUI" --salvar

Nao baixa, move ou altera modelos. Licencas ficam em docs/licencas.md.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TIPOS = (
    "checkpoints",
    "diffusion_models",
    "unet",
    "loras",
    "controlnet",
    "animatediff_models",
    "animatediff_motion_lora",
    "ipadapter",
    "vae",
    "clip",
    "clip_vision",
    "text_encoders",
    "upscale_models",
    "embeddings",
)
EXTENSOES = {".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf"}


def carregar_comfyui_do_config() -> str | None:
    config = RAIZ / "config.json"
    if not config.is_file():
        return None
    try:
        dados = json.loads(config.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    valor = (dados.get("caminhos") or {}).get("comfyui")
    return valor if isinstance(valor, str) and valor else None


def inventariar(comfyui: Path) -> dict:
    modelos: list[dict] = []
    resumo: dict[str, dict] = {}
    for tipo in TIPOS:
        pasta = comfyui / "models" / tipo
        itens = []
        if pasta.is_dir():
            for arquivo in pasta.rglob("*"):
                if not arquivo.is_file() or arquivo.suffix.lower() not in EXTENSOES:
                    continue
                try:
                    tamanho = arquivo.stat().st_size
                except OSError:
                    continue
                if tamanho <= 0:
                    continue
                itens.append(
                    {
                        "tipo": tipo,
                        "arquivo": arquivo.name,
                        "caminho": str(arquivo),
                        "tamanho_mb": round(tamanho / 1024**2, 1),
                        "licenca": "ver docs/licencas.md",
                        "sha256": None,
                    }
                )
        if itens:
            itens.sort(key=lambda item: (-item["tamanho_mb"], item["arquivo"].lower()))
            modelos.extend(itens)
            resumo[tipo] = {
                "quantidade": len(itens),
                "tamanho_mb": round(sum(item["tamanho_mb"] for item in itens), 1),
            }
    return {
        "versao": 1,
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "comfyui": str(comfyui),
        "modelos": modelos,
        "resumo": resumo,
        "total_modelos": len(modelos),
        "total_mb": round(sum(item["tamanho_mb"] for item in modelos), 1),
        "observacao": "sha256 deve ser calculado sob demanda para o receipt.json.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventario de modelos do ComfyUI (somente leitura).")
    parser.add_argument("--comfyui", type=Path, default=None)
    parser.add_argument("--salvar", action="store_true")
    parser.add_argument(
        "--saida",
        type=Path,
        default=RAIZ / "descoberta" / "modelos_encontrados.json",
    )
    args = parser.parse_args()

    caminho = args.comfyui
    if caminho is None:
        configurado = carregar_comfyui_do_config()
        if not configurado:
            raise SystemExit(
                "Informe --comfyui ou registre caminhos.comfyui em config.json"
            )
        caminho = Path(configurado)
    if not (caminho / "main.py").is_file():
        raise SystemExit(f"ComfyUI invalido (sem main.py): {caminho}")

    dados = inventariar(caminho)
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    if args.salvar:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto + "\n", encoding="utf-8")
        print(f"OK: {args.saida} ({dados['total_modelos']} modelos, {dados['total_mb']} MB)")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
