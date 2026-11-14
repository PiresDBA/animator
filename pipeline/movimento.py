"""Metricas de movimento entre quadros amostrados."""
from __future__ import annotations

import cv2
import numpy as np

LARGURA_ANALISE = 320


def _cinza(quadro_bgr: np.ndarray) -> np.ndarray:
    altura, largura = quadro_bgr.shape[:2]
    if largura > LARGURA_ANALISE:
        escala = LARGURA_ANALISE / float(largura)
        quadro_bgr = cv2.resize(
            quadro_bgr,
            (LARGURA_ANALISE, max(1, int(round(altura * escala)))),
            interpolation=cv2.INTER_AREA,
        )
    return cv2.cvtColor(quadro_bgr, cv2.COLOR_BGR2GRAY)


def _vazio(t: float) -> dict:
    return {"t": round(float(t), 6), "dif_media": None, "fluxo_medio": None, "fluxo_p95": None}


def resumo_movimento(entradas: list[dict]) -> dict:
    difs = [e["dif_media"] for e in entradas if e.get("dif_media") is not None]
    fluxos = [e["fluxo_medio"] for e in entradas if e.get("fluxo_medio") is not None]

    def media(valores: list[float]) -> float:
        return round(float(np.mean(valores)), 6) if valores else 0.0

    def pico(valores: list[float]) -> float:
        return round(float(np.max(valores)), 6) if valores else 0.0

    return {
        "dif_media_media": media(difs),
        "dif_media_pico": pico(difs),
        "fluxo_medio_media": media(fluxos),
        "fluxo_medio_pico": pico(fluxos),
    }


def analisar_movimento(quadros: list[tuple[float, np.ndarray]]) -> dict:
    entradas: list[dict] = []
    anterior = None
    for t, quadro in quadros:
        atual = _cinza(quadro)
        if anterior is None or anterior.shape != atual.shape:
            entradas.append(_vazio(t))
            anterior = atual
            continue
        diff = np.abs(anterior.astype(np.float32) - atual.astype(np.float32))
        dif_media = float(diff.mean() / 255.0)
        fluxo = cv2.calcOpticalFlowFarneback(
            anterior, atual, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        fluxo = np.nan_to_num(fluxo, nan=0.0, posinf=0.0, neginf=0.0)
        magnitude = np.linalg.norm(fluxo, axis=2)
        entradas.append(
            {
                "t": round(float(t), 6),
                "dif_media": round(dif_media, 6),
                "fluxo_medio": round(float(magnitude.mean()), 6),
                "fluxo_p95": round(float(np.percentile(magnitude, 95)), 6),
            }
        )
        anterior = atual
    return {"por_amostra": entradas, "resumo": resumo_movimento(entradas)}
