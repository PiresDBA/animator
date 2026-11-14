"""Pose com YOLOv8n-pose."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np

from pipeline import cache, video


def _indices_previas(total: int) -> set[int]:
    if total <= 0:
        return set()
    return {0, total // 2, total - 1}


def _deteccoes(resultado) -> list[dict]:
    caixas = resultado.boxes
    if caixas is None or len(caixas) == 0:
        return []
    xyxy = caixas.xyxy.cpu().numpy()
    confiancas = caixas.conf.cpu().numpy()
    kps = resultado.keypoints
    if kps is not None and kps.xy is not None:
        pontos = kps.xy.cpu().numpy()
        pontos_conf = kps.conf.cpu().numpy() if kps.conf is not None else None
    else:
        pontos = None
        pontos_conf = None
    saida = []
    for indice in range(len(xyxy)):
        if pontos is not None and indice < len(pontos):
            lista_pontos = [
                [
                    round(float(pontos[indice, j, 0]), 2),
                    round(float(pontos[indice, j, 1]), 2),
                    round(float(pontos_conf[indice, j]), 4) if pontos_conf is not None else 0.0,
                ]
                for j in range(pontos.shape[1])
            ]
        else:
            lista_pontos = []
        saida.append(
            {
                "caixa": [round(float(v), 2) for v in xyxy[indice]],
                "conf": round(float(confiancas[indice]), 4),
                "pontos": lista_pontos,
            }
        )
    return saida


def analisar_pose(
    quadros: list[tuple[float, np.ndarray]],
    saida_previa: Path,
    pesos: Path,
    conf_min: float = 0.20,
    dispositivo: str = "cuda",
    salvar_previas: bool = True,
) -> dict:
    from ultralytics import YOLO

    inicio = time.perf_counter()
    modelo = YOLO(str(pesos))
    device = 0 if dispositivo == "cuda" else "cpu"
    previas: list[str] = []
    por_amostra: list[dict] = []
    total = 0
    indices = _indices_previas(len(quadros))
    for indice, (t, quadro_bgr) in enumerate(quadros):
        resultados = modelo.predict(
            quadro_bgr,
            imgsz=640,
            conf=float(conf_min),
            verbose=False,
            device=device,
        )
        deteccoes = _deteccoes(resultados[0]) if resultados else []
        total += len(deteccoes)
        por_amostra.append(
            {
                "t": round(float(t), 6),
                "pessoas": len(deteccoes),
                "deteccoes": deteccoes,
            }
        )
        if salvar_previas and indice in indices:
            if resultados:
                anotado = resultados[0].plot()
            else:
                anotado = quadro_bgr.copy()
                cv2.putText(
                    anotado,
                    "sem deteccao de pose",
                    (24, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
            destino = saida_previa / f"pose_{indice:03d}.jpg"
            video.salvar_previa(anotado, destino, largura_max=960)
            previas.append(video.caminho_relativo(destino))
    return {
        "modelo": "yolov8n-pose",
        "pesos": video.caminho_relativo(pesos),
        "conf_min": round(float(conf_min), 4),
        "por_amostra": por_amostra,
        "previas": previas,
        "total_deteccoes": total,
        "tempo_s": round(time.perf_counter() - inicio, 6),
        "erro": None,
        "licenca": "AGPL-3.0; uso pessoal/educacional",
    }


def pose_vazia(pesos: Path, conf_min: float, erro: str | None) -> dict:
    return {
        "modelo": "yolov8n-pose",
        "pesos": video.caminho_relativo(pesos),
        "conf_min": round(float(conf_min), 4),
        "por_amostra": [],
        "previas": [],
        "total_deteccoes": 0,
        "tempo_s": 0.0,
        "erro": erro,
        "licenca": "AGPL-3.0; uso pessoal/educacional",
    }
