"""Transcricao local com faster-whisper."""
from __future__ import annotations

import time
from pathlib import Path

from pipeline import cache


def _segmento(segmento) -> dict:
    avg = getattr(segmento, "avg_logprob", None)
    sem_fala = getattr(segmento, "no_speech_prob", None)
    return {
        "inicio_s": round(float(segmento.start), 3),
        "fim_s": round(float(segmento.end), 3),
        "texto": segmento.text.strip(),
        "avg_logprob": round(float(avg), 4) if avg is not None else None,
        "no_speech_prob": round(float(sem_fala), 4) if sem_fala is not None else None,
    }


def sem_audio(modelo: str, dispositivo: str) -> dict:
    return {
        "modelo": f"faster-whisper-{modelo}",
        "dispositivo": dispositivo,
        "compute_type": None,
        "idioma": None,
        "prob_idioma": None,
        "fala_presente": False,
        "texto": "",
        "segmentos": [],
        "tempo_s": 0.0,
        "erro": None,
        "aviso": "sem faixa de audio",
    }


def transcrever(
    audio: Path,
    modelo: str = "small",
    dispositivo: str = "cuda",
    idioma: str = "pt",
) -> dict:
    from faster_whisper import WhisperModel

    inicio = time.perf_counter()
    tentativas = (
        [(dispositivo, "int8_float32"), ("cpu", "int8")]
        if dispositivo == "cuda"
        else [("cpu", "int8")]
    )
    avisos: list[str] = []
    erro_final = ""
    for disp, compute_type in tentativas:
        objeto = None
        try:
            objeto = WhisperModel(
                modelo,
                device=disp,
                compute_type=compute_type,
                download_root=str(cache.CONFIG["whisper"]),
            )
            segmentos_brutos, info = objeto.transcribe(
                str(audio),
                language=idioma or None,
                vad_filter=True,
                beam_size=5,
                condition_on_previous_text=False,
            )
            segmentos = [_segmento(s) for s in segmentos_brutos if s.text.strip()]
            return {
                "modelo": f"faster-whisper-{modelo}",
                "dispositivo": disp,
                "compute_type": compute_type,
                "idioma": info.language,
                "prob_idioma": (
                    round(float(info.language_probability), 4)
                    if info.language_probability is not None
                    else None
                ),
                "fala_presente": bool(segmentos),
                "texto": " ".join(s["texto"] for s in segmentos),
                "segmentos": segmentos,
                "tempo_s": round(time.perf_counter() - inicio, 6),
                "erro": None,
                "aviso": "; ".join(avisos) if avisos else None,
            }
        except Exception as exc:
            avisos.append(f"{disp}/{compute_type}: {exc}")
            erro_final = str(exc)
            del objeto
            cache.liberar_gpu()
    return {
        "modelo": f"faster-whisper-{modelo}",
        "dispositivo": dispositivo,
        "compute_type": None,
        "idioma": None,
        "prob_idioma": None,
        "fala_presente": False,
        "texto": "",
        "segmentos": [],
        "tempo_s": round(time.perf_counter() - inicio, 6),
        "erro": "; ".join(avisos) if avisos else erro_final or "falha desconhecida",
        "aviso": None,
    }
