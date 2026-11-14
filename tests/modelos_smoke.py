#!/usr/bin/env python3
"""Smoke test dos modelos do M1. Nao faz parte do unittest discover.

Uso:
    .venv\\Scripts\\python.exe tests\\modelos_smoke.py
    .venv\\Scripts\\python.exe tests\\modelos_smoke.py --sem-pose
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / ".cache"
for nome, valor in {
    "HF_HOME": CACHE / "huggingface",
    "HF_HUB_CACHE": CACHE / "huggingface" / "hub",
    "TRANSFORMERS_CACHE": CACHE / "huggingface" / "transformers",
    "TORCH_HOME": CACHE / "torch",
    "YOLO_CONFIG_DIR": CACHE / "ultralytics",
    "U2NET_HOME": CACHE / "rembg",
    "XDG_CACHE_HOME": CACHE,
}.items():
    Path(valor).mkdir(parents=True, exist_ok=True)
    os.environ[nome] = str(valor)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

GOLDEN = RAIZ / "tests" / "golden"
MODELOS = CACHE / "modelos"
MODELOS.mkdir(parents=True, exist_ok=True)
YOLO_POSE = MODELOS / "yolov8n-pose.pt"


def quadro(video: Path, t: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(video))
    try:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"nao foi possivel ler {video} em {t}s")
        return frame
    finally:
        cap.release()


def tempo(nome: str, fn):
    inicio = time.perf_counter()
    resultado = fn()
    print(f"{nome}: {time.perf_counter() - inicio:.3f}s")
    return resultado


def testar_cenas() -> None:
    from scenedetect import SceneManager, open_video
    from scenedetect.detectors import ContentDetector

    video = open_video(str(GOLDEN / "clipe_02_acao.mp4"))
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=27.0, min_scene_len=15))
    manager.detect_scenes(video)
    cenas = manager.get_scene_list(start_in_scene=True)
    print("cenas:", [(round(a.get_seconds(), 2), round(b.get_seconds(), 2)) for a, b in cenas])


def testar_pose() -> None:
    from ultralytics import YOLO

    modelo = YOLO(str(YOLO_POSE))
    for nome in ("clipe_01_estatico.mp4", "clipe_02_acao.mp4"):
        frame = quadro(GOLDEN / nome, 4.0)
        resultados = modelo.predict(frame, imgsz=640, conf=0.20, verbose=False)
        total = sum(len(r.boxes) for r in resultados)
        print(f"pose {nome}: {total} pessoa(s)")
        for r in resultados:
            if r.keypoints is not None and len(r.keypoints.xy):
                print("  keypoints:", r.keypoints.xy.shape, "conf media:",
                      float(r.keypoints.conf.mean()) if r.keypoints.conf is not None else None)


def testar_profundidade() -> None:
    from PIL import Image
    from transformers import pipeline

    pipe = pipeline(
        "depth-estimation",
        model="depth-anything/Depth-Anything-V2-Small-hf",
        device=0,
    )
    frame = cv2.cvtColor(quadro(GOLDEN / "clipe_01_estatico.mp4", 4.0), cv2.COLOR_BGR2RGB)
    resultado = pipe(Image.fromarray(frame))
    prof = resultado["predicted_depth"]
    arr = prof.detach().cpu().numpy() if hasattr(prof, "detach") else np.asarray(prof)
    print("profundidade:", resultado["depth"].size, "min", float(arr.min()), "max", float(arr.max()),
          "media", float(arr.mean()))


def testar_mascara() -> None:
    from PIL import Image
    from rembg import new_session, remove

    sessao = new_session("u2net")
    frame = cv2.cvtColor(quadro(GOLDEN / "clipe_01_estatico.mp4", 4.0), cv2.COLOR_BGR2RGB)
    mascara = remove(Image.fromarray(frame), session=sessao, only_mask=True)
    arr = np.asarray(mascara)
    print("mascara:", arr.shape, "area", float((arr > 127).mean()), "max", int(arr.max()))


def extrair_audio(video: Path, destino: Path) -> None:
    ffmpeg = RAIZ / "tools" / "ffmpeg" / "ffmpeg.exe"
    subprocess.run(
        [str(ffmpeg), "-y", "-hide_banner", "-loglevel", "error", "-i", str(video),
         "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(destino)],
        check=True,
    )


def testar_fala() -> None:
    from faster_whisper import WhisperModel

    modelo = WhisperModel(
        "small",
        device="cuda",
        compute_type="int8_float32",
        download_root=str(CACHE / "whisper"),
    )
    for nome in ("clipe_01_estatico.mp4", "clipe_02_acao.mp4", "clipe_03_texto.mp4"):
        wav = CACHE / f"smoke_{Path(nome).stem}.wav"
        extrair_audio(GOLDEN / nome, wav)
        segmentos, info = modelo.transcribe(
            str(wav), language="pt", vad_filter=True, beam_size=5,
            condition_on_previous_text=False,
        )
        textos = [s.text.strip() for s in segmentos]
        print(f"fala {nome}: idioma={info.language} prob={info.language_probability:.2f} segmentos={textos}")


def gpu() -> dict:
    try:
        saida = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu",
             "--format=csv,noheader,nounits"],
            text=True, timeout=5,
        ).strip()
        usado, total, temp, util = [float(x.strip()) for x in saida.split(",")]
        return {"vram_usada_mb": usado, "vram_total_mb": total, "temp_c": temp, "util_pct": util}
    except Exception as exc:  # noqa: BLE001
        return {"erro": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-pose", action="store_true")
    parser.add_argument("--sem-profundidade", action="store_true")
    parser.add_argument("--sem-mascara", action="store_true")
    parser.add_argument("--sem-fala", action="store_true")
    args = parser.parse_args()
    print("gpu antes:", json.dumps(gpu(), ensure_ascii=False))
    tempo("cenas", testar_cenas)
    if not args.sem_pose:
        tempo("pose", testar_pose)
    if not args.sem_profundidade:
        tempo("profundidade", testar_profundidade)
    if not args.sem_mascara:
        tempo("mascara", testar_mascara)
    if not args.sem_fala:
        tempo("fala", testar_fala)
    print("gpu depois:", json.dumps(gpu(), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
