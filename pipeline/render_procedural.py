"""Renderizador procedural para os estilos LEGO, Anime, Cartoon 3D e 3D PBR.

Aplica as técnicas de transformação de imagem quadro a quadro a partir do vídeo
original, mantendo sincronia de áudio e 100% de processamento local sem GPU ou difusão.
"""
from __future__ import annotations

import concurrent.futures
import time
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from tecnicas import anime, cartoon, lego, tres_d

TECNICAS: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "lego": lego.estilizar,
    "anime": anime.estilizar,
    "cartoon": cartoon.estilizar,
    "3d": tres_d.estilizar,
}


def extrair_quadros(
    caminho_video: Path,
    inicio_s: float,
    duracao_s: float,
    fps: int = 30,
    largura: int = 854,
    altura: int = 480,
) -> list[np.ndarray]:
    """Extrai os quadros de um trecho do vídeo redimensionados para (largura, altura)."""
    cap = cv2.VideoCapture(str(caminho_video))
    if not cap.isOpened():
        raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho_video}")

    fps_orig = cap.get(cv2.CAP_PROP_FPS) or 30.0
    quadro_inicio = int(inicio_s * fps_orig)
    cap.set(cv2.CAP_PROP_POS_FRAMES, quadro_inicio)

    total_desejado = max(1, int(round(duracao_s * fps)))
    quadros: list[np.ndarray] = []

    # Passo temporal
    passo = fps_orig / float(fps)
    pos_float = float(quadro_inicio)

    for i in range(total_desejado):
        frame_idx = int(round(pos_float))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            # Se acabou o vídeo, repete o último ou cria tela neutra
            if quadros:
                frame = quadros[-1].copy()
            else:
                frame = np.zeros((altura, largura, 3), dtype=np.uint8)
        else:
            if frame.shape[1] != largura or frame.shape[0] != altura:
                frame = cv2.resize(frame, (largura, altura), interpolation=cv2.INTER_AREA)
        quadros.append(frame)
        pos_float += passo

    cap.release()
    return quadros


def processar_quadro(arg: tuple[int, np.ndarray, str, Path]) -> int:
    idx, quadro, estilo, pasta_saida = arg
    funcao = TECNICAS.get(estilo, lego.estilizar)
    resultado = funcao(quadro)
    caminho_frame = pasta_saida / f"f_{idx:05d}.png"
    cv2.imwrite(str(caminho_frame), resultado)
    return idx


def renderizar_estilo(
    caminho_video: Path,
    estilo: str,
    pasta_saida: Path,
    inicio_s: float = 0.0,
    duracao_s: float = 5.0,
    fps: int = 30,
    largura: int = 854,
    altura: int = 480,
    max_workers: int = 4,
) -> int:
    """Renderiza todos os quadros do trecho no estilo procedural escolhido."""
    pasta_saida.mkdir(parents=True, exist_ok=True)
    quadros = extrair_quadros(caminho_video, inicio_s, duracao_s, fps, largura, altura)

    tarefas = [
        (i, quadros[i], estilo, pasta_saida)
        for i in range(len(quadros))
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(processar_quadro, tarefas))

    return len(quadros)
