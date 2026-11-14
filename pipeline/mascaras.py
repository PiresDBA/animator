"""Mascaras de primeiro plano com rembg/U2Net."""
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


def _analisar_mascara(mascara: np.ndarray) -> tuple[float, list[int] | None, int, list[int]]:
    if mascara.ndim == 3:
        mascara = mascara[..., 0]
    binaria = (mascara > 127).astype(np.uint8)
    area_ratio = float(binaria.mean())
    total_pixels = int(binaria.size)
    minimo = max(10, int(total_pixels * 0.0005))
    quantidade, rotulos, estatisticas, _ = cv2.connectedComponentsWithStats(
        binaria, connectivity=8
    )
    areas = []
    for indice in range(1, quantidade):
        area = int(estatisticas[indice, cv2.CC_STAT_AREA])
        if area >= minimo:
            areas.append((area, indice))
    areas.sort(reverse=True)
    if not areas:
        return area_ratio, None, 0, []
    _, maior = areas[0]
    x = int(estatisticas[maior, cv2.CC_STAT_LEFT])
    y = int(estatisticas[maior, cv2.CC_STAT_TOP])
    largura = int(estatisticas[maior, cv2.CC_STAT_WIDTH])
    altura = int(estatisticas[maior, cv2.CC_STAT_HEIGHT])
    return area_ratio, [x, y, largura, altura], len(areas), [a for a, _ in areas[:5]]


def analisar_mascaras(
    quadros: list[tuple[float, np.ndarray]],
    saida_previa: Path,
    modelo: str = "u2net",
    salvar_previas: bool = True,
) -> dict:
    from rembg import new_session, remove

    inicio = time.perf_counter()
    sessao = new_session(modelo)
    previas: list[str] = []
    por_amostra: list[dict] = []
    indices = _indices_previas(len(quadros))
    for indice, (t, quadro_bgr) in enumerate(quadros):
        rgb = cv2.cvtColor(quadro_bgr, cv2.COLOR_BGR2RGB)
        mascara = remove(Image.fromarray(rgb), session=sessao, only_mask=True)
        arr = np.asarray(mascara)
        area_ratio, bbox, componentes, areas = _analisar_mascara(arr)
        por_amostra.append(
            {
                "t": round(float(t), 6),
                "area_ratio": round(area_ratio, 6),
                "bbox": bbox,
                "componentes": componentes,
                "areas_px": areas,
            }
        )
        if salvar_previas and indice in indices:
            if arr.ndim == 3:
                arr = arr[..., 0]
            destino = saida_previa / f"mascara_{indice:03d}.png"
            video.salvar_previa(arr, destino)
            previas.append(video.caminho_relativo(destino))
    return {
        "modelo": f"rembg-{modelo}",
        "por_amostra": por_amostra,
        "previas": previas,
        "tempo_s": round(time.perf_counter() - inicio, 6),
        "erro": None,
    }


def mascaras_vazias(modelo: str, erro: str | None) -> dict:
    return {
        "modelo": f"rembg-{modelo}",
        "por_amostra": [],
        "previas": [],
        "tempo_s": 0.0,
        "erro": erro,
    }
