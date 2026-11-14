"""Configuracao de cache e DLLs do pipeline M1."""
from __future__ import annotations

import gc
import importlib.util
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CACHE = RAIZ / ".cache"
MODELOS = CACHE / "modelos"
FFMPEG = RAIZ / "tools" / "ffmpeg" / "ffmpeg.exe"
FFPROBE = RAIZ / "tools" / "ffmpeg" / "ffprobe.exe"

_DLL_HANDLES = []


def _preparar(nome: str, caminho: Path) -> Path:
    caminho.mkdir(parents=True, exist_ok=True)
    os.environ[nome] = str(caminho)
    return caminho


def configurar() -> dict[str, Path]:
    for pasta in (CACHE, MODELOS, CACHE / "huggingface" / "hub", CACHE / "torch",
                  CACHE / "whisper", CACHE / "ultralytics", CACHE / "rembg",
                  CACHE / "matplotlib", CACHE / "numba", CACHE / "pip"):
        pasta.mkdir(parents=True, exist_ok=True)

    _preparar("HF_HOME", CACHE / "huggingface")
    _preparar("HF_HUB_CACHE", CACHE / "huggingface" / "hub")
    _preparar("TORCH_HOME", CACHE / "torch")
    _preparar("YOLO_CONFIG_DIR", CACHE / "ultralytics")
    _preparar("U2NET_HOME", CACHE / "rembg")
    _preparar("XDG_CACHE_HOME", CACHE)
    _preparar("MPLCONFIGDIR", CACHE / "matplotlib")
    _preparar("NUMBA_CACHE_DIR", CACHE / "numba")
    _preparar("PIP_CACHE_DIR", CACHE / "pip")
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

    spec = importlib.util.find_spec("torch")
    if spec and spec.submodule_search_locations:
        torch_lib = Path(next(iter(spec.submodule_search_locations))) / "lib"
        if torch_lib.is_dir():
            atual = os.environ.get("PATH", "")
            if str(torch_lib) not in atual.split(os.pathsep):
                os.environ["PATH"] = str(torch_lib) + os.pathsep + atual
            if hasattr(os, "add_dll_directory"):
                try:
                    _DLL_HANDLES.append(os.add_dll_directory(str(torch_lib)))
                except OSError:
                    pass

    return {
        "raiz": RAIZ,
        "cache": CACHE,
        "modelos": MODELOS,
        "ffmpeg": FFMPEG,
        "ffprobe": FFPROBE,
        "huggingface": CACHE / "huggingface",
        "whisper": CACHE / "whisper",
        "ultralytics": CACHE / "ultralytics",
        "rembg": CACHE / "rembg",
    }


CONFIG = configurar()


def liberar_gpu() -> None:
    gc.collect()
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except Exception:
        pass
