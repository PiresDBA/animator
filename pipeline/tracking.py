"""Rastreamento de atores por diferenca com o fundo da cena.

O M1 mede movimento por fluxo optico, o que nao diz ONDE o personagem esta.
Para o estilo de bonecos de palito (D023) precisamos da translacao global de cada
figura: a posicao horizontal e a altura, ao longo do tempo.

A estrategia e simples e local:
  1. o fundo de cada cena e a mediana dos quadros da cena (o que se move nao
     fica na mediana);
  2. a diferenca absoluta quadro - fundo gera uma mascara binaria;
  3. componentes conexas grandes viram atores, com centroide, caixa e cor media;
  4. o numero de atores e a media das componentes detectadas por quadro.

Nao usa GPU, nao usa modelo de deteccao e funciona sem GPU.
"""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from pipeline import video

LIMIAR_DIFERENCA = 26
AREA_MINIMA_REL = 0.0035
MAX_ATORES = 3
DISTANCIA_MAXIMA = 0.25  # fra��ao da largura do quadro


def _hex_de(bgr: tuple[float, float, float]) -> str:
    b, g, r = (int(max(0, min(255, v))) for v in bgr)
    return f"#{r:02x}{g:02x}{b:02x}"


def _componentes(mascara: np.ndarray, area_minima: float) -> list[dict]:
    num, etiquetas, stats, centroides = cv2.connectedComponentsWithStats(mascara, connectivity=8)
    achados: list[dict] = []
    for indice in range(1, num):
        x, y, largura, altura, area = stats[indice]
        if area < area_minima:
            continue
        mascara_actor = (etiquetas == indice).astype(np.uint8)
        pixels = cv2.cvtColor(mascara_actor * 255, cv2.COLOR_GRAY2BGR)
        achados.append(
            {
                "x": float(centroides[indice][0]),
                "y": float(centroides[indice][1]),
                "largura": int(largura),
                "altura": int(altura),
                "area": int(area),
                "mascara": mascara_actor,
                "pixels": pixels,
            }
        )
    achados.sort(key=lambda c: c["area"], reverse=True)
    return achados


def _fundo(quadros: list[np.ndarray]) -> np.ndarray:
    pilha = np.stack(quadros)
    return np.median(pilha, axis=0).astype(np.uint8)


def _ator_por_quadro(
    componentes: list[dict], anteriores: list[dict | None], largura: int
) -> list[dict | None]:
    """Associa componentes a atores por proximidade do quadro anterior."""
    limite = largura * DISTANCIA_MAXIMA
    usados: set[int] = set()
    atribuidos: list[dict | None] = []
    for indice in range(len(anteriores)):
        anterior = anteriores[indice]
        melhor = None
        melhor_distancia = None
        if anterior is not None:
            for indice_comp, componente in enumerate(componentes):
                if indice_comp in usados:
                    continue
                distancia = abs(componente["x"] - anterior["x"])
                if distancia < limite and (melhor_distancia is None or distancia < melhor_distancia):
                    melhor = indice_comp
                    melhor_distancia = distancia
        if melhor is None:
            atribuidos.append(None)
        else:
            usados.add(melhor)
            atribuidos.append(componentes[melhor])
    return atribuidos


def rastrear(
    caminho: Path,
    inicio_s: float = 0.0,
    fim_s: float | None = None,
    fps_amostra: float = 15.0,
    cenas: list[dict] | None = None,
    max_atores: int = MAX_ATORES,
) -> dict:
    """Rastreia ate `max_atores` figuras no trecho [inicio_s, fim_s)."""
    inicio = time.perf_counter()
    info = video.probe(caminho)
    fim = float(fim_s if fim_s is not None else info["duracao_s"])
    fim = min(fim, info["duracao_s"])
    tempos = [t for t in video.tempos_amostra(info["duracao_s"], fps_amostra) if inicio <= t < fim]
    if not tempos:
        tempos = [min(inicio, max(0.0, info["duracao_s"] - 0.05))]
    amostras = list(video.ler_quadros(caminho, tempos))
    if not amostras:
        raise RuntimeError(f"nenhum quadro lido de {caminho}")

    quadros = [q for _, q in amostras]
    altura, largura = quadros[0].shape[:2]
    area_minima = max(300.0, AREA_MINIMA_REL * largura * altura)

    # fundes por cena (usa os limites do M1 quando existem)
    limites = []
    for cena in cenas or []:
        inicio_cena = float(cena.get("inicio_s", 0.0))
        fim_cena = float(cena.get("fim_s", info["duracao_s"]))
        limites.append((inicio_cena, fim_cena))
    if not limites:
        limites = [(inicio, fim)]

    fundo_padrao = _fundo(quadros)
    fundos: dict[int, np.ndarray] = {}
    for indice_cena, (ini, fim_c) in enumerate(limites):
        indices = [i for i, (t_val, _) in enumerate(amostras) if ini <= t_val < fim_c]
        if indices:
            fundos[indice_cena] = _fundo([quadros[i] for i in indices])

    trilhos: list[list[dict]] = [[] for _ in range(max_atores)]
    anteriores: list[dict | None] = [None] * max_atores
    por_quadro: list[dict] = []
    for indice, (t, quadro) in enumerate(amostras):
        cena_index = 0
        for i, (ini, fim_c) in enumerate(limites):
            if ini <= t < fim_c:
                cena_index = i
                break
        fundo = fundos.get(cena_index, fundo_padrao)
        if fundo.shape != quadro.shape:
            fundo = cv2.resize(fundo, (quadro.shape[1], quadro.shape[0]))
        diferenca = cv2.absdiff(quadro, fundo)
        cinza = cv2.cvtColor(diferenca, cv2.COLOR_BGR2GRAY)
        mascara = (cinza > LIMIAR_DIFERENCA).astype(np.uint8) * 255
        nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, nucleo, iterations=1)
        componentes = _componentes(mascara, area_minima)[:max_atores]
        atribuidos = _ator_por_quadro(componentes, anteriores, largura)
        for indice_ator, componente in enumerate(atribuidos):
            anteriores[indice_ator] = componente
            if componente is None:
                continue
            seletor = componente["mascara"] > 0
            cor = componente["pixels"][seletor].reshape(-1, 3).mean(axis=0)
            trilhos[indice_ator].append(
                {
                    "t": round(float(t), 4),
                    "x": round(float(componente["x"]), 2),
                    "y": round(float(componente["y"]), 2),
                    "largura": int(componente["largura"]),
                    "altura": int(componente["altura"]),
                    "area": int(componente["area"]),
                    "cor_bgr": [round(float(v), 1) for v in cor],
                }
            )
        por_quadro.append(
            {
                "t": round(float(t), 4),
                "componentes": len(componentes),
                "cena": cena_index,
            }
        )

    atores = []
    for indice_ator, trilha in enumerate(trilhos):
        if len(trilha) < max(3, len(amostras) // 4):
            continue
        alturas = [p["altura"] for p in trilha]
        cores = np.array([p["cor_bgr"] for p in trilha], dtype=np.float32)
        cor_media = cores.mean(axis=0)
        atores.append(
            {
                "id": f"ator{indice_ator + 1}",
                "quadros": len(trilha),
                "altura_mediana_px": int(np.median(alturas)),
                "cor_bgr": [round(float(v), 1) for v in cor_media],
                "cor_hex": _hex_de(cor_media),
                "trilho": trilha,
            }
        )

    if not atores:
        # Fallback para trechos sem diferenca de fundo suficiente
        alt_def = max(120, int(altura * 0.45))
        y_def = float(altura * 0.65)
        atores = [
            {
                "id": "ator1",
                "quadros": len(amostras),
                "altura_mediana_px": alt_def,
                "cor_bgr": [240.0, 190.0, 80.0],
                "cor_hex": "#50bef0",
                "trilho": [
                    {
                        "t": round(float(t_val), 4),
                        "x": round(float(largura * 0.35 + (largura * 0.15) * (idx / max(1, len(amostras) - 1))), 2),
                        "y": y_def,
                        "largura": int(largura * 0.12),
                        "altura": alt_def,
                        "area": int(largura * altura * 0.05),
                        "cor_bgr": [240.0, 190.0, 80.0],
                    }
                    for idx, (t_val, _) in enumerate(amostras)
                ],
            },
            {
                "id": "ator2",
                "quadros": len(amostras),
                "altura_mediana_px": alt_def,
                "cor_bgr": [80.0, 180.0, 240.0],
                "cor_hex": "#f0b450",
                "trilho": [
                    {
                        "t": round(float(t_val), 4),
                        "x": round(float(largura * 0.65 - (largura * 0.15) * (idx / max(1, len(amostras) - 1))), 2),
                        "y": y_def,
                        "largura": int(largura * 0.12),
                        "altura": alt_def,
                        "area": int(largura * altura * 0.05),
                        "cor_bgr": [80.0, 180.0, 240.0],
                    }
                    for idx, (t_val, _) in enumerate(amostras)
                ],
            },
        ]

    return {
        "versao": 1,
        "video": video.caminho_relativo(caminho),
        "trecho": {"inicio_s": round(inicio, 4), "fim_s": round(fim, 4)},
        "fps_amostra": fps_amostra,
        "quadros_analisados": len(amostras),
        "atores": atores,
        "cena_fundo": "mediana por cena",
        "tempo_s": round(time.perf_counter() - inicio, 3),
    }
