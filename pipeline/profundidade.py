"""Estimativa de profundidade com Depth Anything V2 Small."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from pipeline import cache, video


def _indices_previas(total: int) -> set[int]:
    if total <= 0:
        return set()
    return {0, total // 2, total - 1}


def _mapa_colorido(profundidade: np.ndarray) -> np.ndarray:
    arr = np.nan_to_num(
        np.asarray(profundidade, dtype=np.float32),
        nan=0.0,
        posinf=0.0,
        neginf=0.0,
    )
    normalizado = cv2.normalize(arr, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return cv2.applyColorMap(normalizado, cv2.COLORMAP_INFERNO)


def analisar_profundidade(
    quadros: list[tuple[float, np.ndarray]],
    saida_previa: Path,
    modelo: str = "depth-anything/Depth-Anything-V2-Small-hf",
    dispositivo: str = "cuda",
    salvar_previas: bool = True,
) -> dict:
    from transformers import pipeline

    inicio = time.perf_counter()
    device = 0 if dispositivo == "cuda" else -1
    estimador = pipeline("depth-estimation", model=modelo, device=device)
    previas: list[str] = []
    por_amostra: list[dict] = []
    indices = _indices_previas(len(quadros))
    for indice, (t, quadro_bgr) in enumerate(quadros):
        rgb = cv2.cvtColor(quadro_bgr, cv2.COLOR_BGR2RGB)
        resultado = estimador(Image.fromarray(rgb))
        pred = resultado["predicted_depth"]
        arr = pred.detach().cpu().numpy() if hasattr(pred, "detach") else np.asarray(pred)
        arr = np.asarray(arr, dtype=np.float32)
        por_amostra.append(
            {
                "t": round(float(t), 6),
                "min": round(float(np.min(arr)), 6),
                "max": round(float(np.max(arr)), 6),
                "media": round(float(np.mean(arr)), 6),
                "desvio": round(float(np.std(arr)), 6),
                "percentis": [
                    round(float(np.percentile(arr, 5)), 6),
                    round(float(np.percentile(arr, 50)), 6),
                    round(float(np.percentile(arr, 95)), 6),
                ],
            }
        )
        if salvar_previas and indice in indices:
            destino = saida_previa / f"profundidade_{indice:03d}.png"
            colorido = _mapa_colorido(arr)
            video.salvar_previa(colorido, destino)
            previas.append(video.caminho_relativo(destino))
    return {
        "modelo": modelo,
        "dispositivo": dispositivo,
        "por_amostra": por_amostra,
        "previas": previas,
        "tempo_s": round(time.perf_counter() - inicio, 6),
        "erro": None,
    }


def profundidade_vazia(modelo: str, dispositivo: str, erro: str | None) -> dict:
    return {
        "modelo": modelo,
        "dispositivo": dispositivo,
        "por_amostra": [],
        "previas": [],
        "tempo_s": 0.0,
        "erro": erro,
    }
