"""Leitura, probe e amostragem de video."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path

import cv2
import numpy as np

from pipeline import cache

FFMPEG = cache.CONFIG["ffmpeg"]
FFPROBE = cache.CONFIG["ffprobe"]
RAIZ = cache.CONFIG["raiz"]


def parse_fps(valor: str | None, padrao: float = 30.0) -> float:
    if not valor:
        return padrao
    try:
        numero, denominador = valor.split("/")
        den = float(denominador)
        if den == 0:
            return padrao
        taxa = float(numero) / den
        return taxa if taxa > 0 else padrao
    except (ValueError, ZeroDivisionError):
        try:
            taxa = float(valor)
            return taxa if taxa > 0 else padrao
        except ValueError:
            return padrao


def sha256_arquivo(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def probe(caminho: Path) -> dict:
    if not caminho.is_file():
        raise FileNotFoundError(caminho)
    if not FFPROBE.is_file():
        raise FileNotFoundError(FFPROBE)
    saida = subprocess.check_output(
        [
            str(FFPROBE),
            "-v", "error",
            "-show_entries", "format=duration,size",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,channels,sample_rate",
            "-of", "json", str(caminho),
        ],
        text=True,
        encoding="utf-8",
    )
    dados = json.loads(saida)
    streams = dados.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if video is None:
        raise ValueError(f"sem faixa de video: {caminho}")
    duracao = float(dados.get("format", {}).get("duration") or 0.0)
    if duracao <= 0:
        raise ValueError(f"duracao invalida: {duracao}")
    fps = parse_fps(video.get("avg_frame_rate") or video.get("r_frame_rate"))
    return {
        "arquivo": str(caminho),
        "sha256": sha256_arquivo(caminho),
        "duracao_s": round(duracao, 6),
        "fps": round(fps, 6),
        "largura": int(video.get("width") or 0),
        "altura": int(video.get("height") or 0),
        "tamanho_bytes": caminho.stat().st_size,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "audio_presente": audio is not None,
        "audio_canais": int(audio.get("channels") or 0) if audio else None,
        "audio_taxa": int(audio.get("sample_rate") or 0) if audio else None,
    }


def tempos_amostra(duracao_s: float, fps_amostra: float) -> list[float]:
    if duracao_s <= 0 or fps_amostra <= 0:
        raise ValueError("duracao e fps de amostragem devem ser positivos")
    passo = 1.0 / fps_amostra
    total = int(math.floor(duracao_s / passo + 1e-9))
    tempos = [round(i * passo, 6) for i in range(max(0, total))]
    return [t for t in tempos if t < duracao_s]


def ler_quadros(caminho: Path, tempos: list[float]):
    if not tempos:
        return
    cap = cv2.VideoCapture(str(caminho))
    if not cap.isOpened():
        raise RuntimeError(f"nao foi possivel abrir {caminho}")
    try:
        fps_video = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total <= 0:
            total = int(max(tempos) * fps_video) + 2
        pares = sorted(
            (min(int(round(t * fps_video)), total - 1), t)
            for t in tempos
        )
        alvo: dict[int, float] = {}
        for indice, t in pares:
            alvo.setdefault(indice, t)
        ultimo = max(alvo)
        for indice in range(ultimo + 1):
            ok, quadro = cap.read()
            if not ok:
                break
            if indice in alvo:
                yield alvo[indice], quadro
    finally:
        cap.release()


def extrair_audio(caminho: Path, destino: Path, info: dict | None = None) -> Path | None:
    if info is not None and not info.get("audio_presente"):
        return None
    if not FFMPEG.is_file():
        raise FileNotFoundError(FFMPEG)
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(caminho), "-vn", "-ac", "1", "-ar", "16000",
            "-c:a", "pcm_s16le", str(destino),
        ],
        check=True,
    )
    return destino if destino.is_file() and destino.stat().st_size > 44 else None


def redimensionar(imagem: np.ndarray, largura_max: int = 640) -> np.ndarray:
    altura, largura = imagem.shape[:2]
    if largura <= largura_max:
        return imagem
    escala = largura_max / float(largura)
    return cv2.resize(
        imagem,
        (largura_max, max(1, int(round(altura * escala)))),
        interpolation=cv2.INTER_AREA,
    )


def salvar_previa(imagem: np.ndarray, destino: Path, largura_max: int = 640) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    imagem = redimensionar(imagem, largura_max)
    parametros = [cv2.IMWRITE_JPEG_QUALITY, 85] if destino.suffix.lower() in {".jpg", ".jpeg"} else []
    if not cv2.imwrite(str(destino), imagem, parametros):
        raise RuntimeError(f"falha ao salvar previa: {destino}")
    return destino


def caminho_relativo(caminho: Path) -> str:
    try:
        return str(caminho.resolve().relative_to(RAIZ))
    except ValueError:
        return str(caminho.resolve())
