"""Deteccao de cenas com PySceneDetect."""
from __future__ import annotations

import time
from pathlib import Path


def detectar_cenas(
    caminho: Path,
    duracao_s: float,
    limiar: float = 27.0,
    min_cena_frames: int = 15,
) -> tuple[list[dict], float]:
    from scenedetect import SceneManager, open_video
    from scenedetect.detectors import ContentDetector

    inicio = time.perf_counter()
    video = open_video(str(caminho))
    manager = SceneManager()
    manager.add_detector(
        ContentDetector(threshold=float(limiar), min_scene_len=int(min_cena_frames))
    )
    manager.detect_scenes(video)
    brutas = manager.get_scene_list(start_in_scene=True)
    cenas = []
    for indice, (inicio_tc, fim_tc) in enumerate(brutas):
        ini = round(float(inicio_tc.seconds), 3)
        fim = round(float(fim_tc.seconds), 3)
        if fim <= ini:
            continue
        cenas.append(
            {
                "indice": indice,
                "inicio_s": ini,
                "fim_s": fim,
                "duracao_s": round(fim - ini, 3),
            }
        )
    if not cenas:
        cenas = [
            {
                "indice": 0,
                "inicio_s": 0.0,
                "fim_s": round(float(duracao_s), 3),
                "duracao_s": round(float(duracao_s), 3),
            }
        ]
    return cenas, round(time.perf_counter() - inicio, 6)
