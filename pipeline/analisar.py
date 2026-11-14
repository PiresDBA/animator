#!/usr/bin/env python3
"""Analisa um video e grava JSON versionado do M1."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline import (  # noqa: E402
    cache,
    cenas,
    fala,
    mascaras,
    medidas,
    movimento,
    pose,
    profundidade,
    validar,
    video,
)

MODELO_DEPTH = "depth-anything/Depth-Anything-V2-Small-hf"
MODELO_POSE = str(cache.CONFIG["modelos"] / "yolov8n-pose.pt")


def resolver_dispositivo(pedido: str) -> str:
    if pedido == "cpu":
        return "cpu"
    try:
        import torch

        disponivel = torch.cuda.is_available()
    except Exception:
        disponivel = False
    if pedido == "cuda" and not disponivel:
        raise RuntimeError("CUDA foi pedido, mas torch.cuda.is_available() e False")
    return "cuda" if disponivel else "cpu"


def _zeros_movimento() -> dict:
    return {
        "por_amostra": [],
        "resumo": {
            "dif_media_media": 0.0,
            "dif_media_pico": 0.0,
            "fluxo_medio_media": 0.0,
            "fluxo_medio_pico": 0.0,
        },
    }


def _fala_desativada(modelo: str, dispositivo: str, motivo: str) -> dict:
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
        "aviso": motivo,
    }


def _fala_erro(modelo: str, dispositivo: str, erro: str, tempo_s: float) -> dict:
    return {
        "modelo": f"faster-whisper-{modelo}",
        "dispositivo": dispositivo,
        "compute_type": None,
        "idioma": None,
        "prob_idioma": None,
        "fala_presente": False,
        "texto": "",
        "segmentos": [],
        "tempo_s": round(tempo_s, 6),
        "erro": erro,
        "aviso": None,
    }


def _adicionar(avisos: list[str], mensagem: str) -> None:
    if mensagem not in avisos:
        avisos.append(mensagem)


def _medir_etapa(por_etapa: dict, nome: str, inicio: float) -> None:
    por_etapa[nome] = round(time.perf_counter() - inicio, 6)


def analisar(args: argparse.Namespace) -> tuple[dict, Path, Path]:
    inicio_total = time.perf_counter()
    caminho = Path(args.video).expanduser().resolve()
    if not caminho.is_file():
        raise FileNotFoundError(caminho)

    if args.saida:
        saida = Path(args.saida).expanduser().resolve()
    else:
        saida = (
            cache.CONFIG["raiz"] / "saidas" / "analise" / f"{caminho.stem}.json"
        )
    if args.previa_dir:
        previa_dir = Path(args.previa_dir).expanduser().resolve()
    else:
        previa_dir = saida.with_name(f"{saida.stem}_previa")
    saida.parent.mkdir(parents=True, exist_ok=True)
    salvar_previas = not args.sem_previas
    if salvar_previas:
        previa_dir.mkdir(parents=True, exist_ok=True)

    info = video.probe(caminho)
    tempos = video.tempos_amostra(info["duracao_s"], args.fps_amostra)
    quadros = list(video.ler_quadros(caminho, tempos))
    if not quadros:
        raise RuntimeError("nenhum quadro amostrado")
    dispositivo = resolver_dispositivo(args.device)
    modelo_pose = Path(args.modelo_pose).expanduser().resolve()

    por_etapa = {
        "cenas": 0.0,
        "movimento": 0.0,
        "profundidade": 0.0,
        "mascaras": 0.0,
        "pose": 0.0,
        "fala": 0.0,
    }
    erros: list[dict] = []
    avisos: list[str] = []
    monitor = medidas.MonitorGPU(intervalo_s=0.5)
    monitor.start()

    inicio = time.perf_counter()
    try:
        lista_cenas, _ = cenas.detectar_cenas(
            caminho,
            info["duracao_s"],
            limiar=args.limiar_cena,
            min_cena_frames=args.min_cena_frames,
        )
    except Exception as exc:
        lista_cenas = [
            {
                "indice": 0,
                "inicio_s": 0.0,
                "fim_s": round(float(info["duracao_s"]), 3),
                "duracao_s": round(float(info["duracao_s"]), 3),
            }
        ]
        erros.append({"etapa": "cenas", "mensagem": str(exc)})
    _medir_etapa(por_etapa, "cenas", inicio)

    inicio = time.perf_counter()
    try:
        resultado_movimento = movimento.analisar_movimento(quadros)
    except Exception as exc:
        resultado_movimento = _zeros_movimento()
        erros.append({"etapa": "movimento", "mensagem": str(exc)})
    _medir_etapa(por_etapa, "movimento", inicio)

    if args.sem_profundidade:
        resultado_profundidade = profundidade.profundidade_vazia(
            args.modelo_profundidade, dispositivo, None
        )
        _adicionar(avisos, "profundidade desativada por --sem-profundidade")
    else:
        inicio = time.perf_counter()
        try:
            resultado_profundidade = profundidade.analisar_profundidade(
                quadros,
                previa_dir,
                modelo=args.modelo_profundidade,
                dispositivo=dispositivo,
                salvar_previas=salvar_previas,
            )
        except Exception as exc:
            resultado_profundidade = profundidade.profundidade_vazia(
                args.modelo_profundidade, dispositivo, str(exc)
            )
        _medir_etapa(por_etapa, "profundidade", inicio)
        cache.liberar_gpu()

    if args.sem_mascara:
        resultado_mascaras = mascaras.mascaras_vazias(
            args.modelo_mascara, None
        )
        _adicionar(avisos, "mascaras desativadas por --sem-mascara")
    else:
        inicio = time.perf_counter()
        try:
            resultado_mascaras = mascaras.analisar_mascaras(
                quadros,
                previa_dir,
                modelo=args.modelo_mascara,
                salvar_previas=salvar_previas,
            )
        except Exception as exc:
            resultado_mascaras = mascaras.mascaras_vazias(args.modelo_mascara, str(exc))
        _medir_etapa(por_etapa, "mascaras", inicio)

    if args.sem_pose:
        resultado_pose = pose.pose_vazia(
            modelo_pose, args.conf_pose, None
        )
        _adicionar(avisos, "pose desativada por --sem-pose")
    else:
        inicio = time.perf_counter()
        try:
            resultado_pose = pose.analisar_pose(
                quadros,
                previa_dir,
                pesos=modelo_pose,
                conf_min=args.conf_pose,
                dispositivo=dispositivo,
                salvar_previas=salvar_previas,
            )
        except Exception as exc:
            resultado_pose = pose.pose_vazia(modelo_pose, args.conf_pose, str(exc))
        _medir_etapa(por_etapa, "pose", inicio)
        cache.liberar_gpu()

    inicio = time.perf_counter()
    if args.sem_fala:
        resultado_fala = _fala_desativada(
            args.modelo_whisper, dispositivo, "desativado por --sem-fala"
        )
        _adicionar(avisos, "fala desativada por --sem-fala")
    elif not info["audio_presente"]:
        resultado_fala = fala.sem_audio(args.modelo_whisper, dispositivo)
        _adicionar(avisos, "video sem faixa de audio; fala nao analisada")
    else:
        try:
            with tempfile.TemporaryDirectory(
                dir=cache.CONFIG["cache"], prefix="audio_"
            ) as tmp:
                audio = video.extrair_audio(
                    caminho, Path(tmp) / "audio.wav", info
                )
                if audio is None:
                    resultado_fala = fala.sem_audio(args.modelo_whisper, dispositivo)
                    _adicionar(avisos, "video sem faixa de audio; fala nao analisada")
                else:
                    resultado_fala = fala.transcrever(
                        audio,
                        modelo=args.modelo_whisper,
                        dispositivo=dispositivo,
                        idioma=args.idioma,
                    )
        except Exception as exc:
            resultado_fala = _fala_erro(
                args.modelo_whisper, dispositivo, str(exc),
                time.perf_counter() - inicio,
            )
    _medir_etapa(por_etapa, "fala", inicio)
    cache.liberar_gpu()

    gpu = monitor.parar()
    if not args.sem_pose and resultado_pose["total_deteccoes"] == 0:
        _adicionar(
            avisos,
            "pose: 0 deteccoes; resultado registrado como ausencia, sem inventar pontos",
        )
    if not args.sem_fala and info["audio_presente"] and not resultado_fala["fala_presente"]:
        if resultado_fala["erro"] is None:
            _adicionar(avisos, "fala: nenhum segmento de fala detectado")
    if resultado_fala.get("aviso"):
        _adicionar(avisos, f"fala: {resultado_fala['aviso']}")
    for nome, resultado in (
        ("profundidade", resultado_profundidade),
        ("mascaras", resultado_mascaras),
        ("pose", resultado_pose),
        ("fala", resultado_fala),
    ):
        if resultado.get("erro"):
            erros.append({"etapa": nome, "mensagem": str(resultado["erro"])})

    video_json = dict(info)
    video_json["arquivo"] = video.caminho_relativo(caminho)
    tempo_total = round(time.perf_counter() - inicio_total, 6)
    resultado = {
        "versao": 1,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "ok" if not erros else "parcial",
        "video": video_json,
        "config": {
            "fps_amostra": round(float(args.fps_amostra), 6),
            "limiar_cena": round(float(args.limiar_cena), 6),
            "min_cena_frames": int(args.min_cena_frames),
            "dispositivo": dispositivo,
            "modelos": {
                "profundidade": args.modelo_profundidade,
                "mascaras": f"rembg-{args.modelo_mascara}",
                "pose": video.caminho_relativo(modelo_pose),
                "fala": f"faster-whisper-{args.modelo_whisper}",
            },
            "etapas_ativas": {
                "profundidade": not args.sem_profundidade,
                "mascaras": not args.sem_mascara,
                "pose": not args.sem_pose,
                "fala": not args.sem_fala,
            },
        },
        "cenas": lista_cenas,
        "movimento": resultado_movimento,
        "profundidade": resultado_profundidade,
        "mascaras": resultado_mascaras,
        "pose": resultado_pose,
        "fala": resultado_fala,
        "medidas": {
            "tempo_total_s": tempo_total,
            "por_etapa_s": por_etapa,
            "gpu": gpu,
        },
        "avisos": avisos,
        "erros": erros,
    }
    return resultado, saida, previa_dir


def _escrever_json(dados: dict, saida: Path) -> None:
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    temporario = saida.with_name(saida.name + ".tmp")
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(saida)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analisa um video local e grava JSON versionado (M1)."
    )
    parser.add_argument("--video", required=True, help="arquivo de video de entrada")
    parser.add_argument("--saida", help="arquivo JSON de saida")
    parser.add_argument("--previa-dir", help="pasta das imagens de previa")
    parser.add_argument("--fps-amostra", type=float, default=2.0)
    parser.add_argument("--limiar-cena", type=float, default=27.0)
    parser.add_argument("--min-cena-frames", type=int, default=15)
    parser.add_argument("--modelo-profundidade", default=MODELO_DEPTH)
    parser.add_argument("--modelo-pose", default=MODELO_POSE)
    parser.add_argument("--modelo-whisper", default="small")
    parser.add_argument("--modelo-mascara", default="u2net")
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument("--conf-pose", type=float, default=0.20)
    parser.add_argument("--idioma", default="pt")
    parser.add_argument("--sem-profundidade", action="store_true")
    parser.add_argument("--sem-mascara", action="store_true")
    parser.add_argument("--sem-pose", action="store_true")
    parser.add_argument("--sem-fala", action="store_true")
    parser.add_argument("--sem-previas", action="store_true")
    args = parser.parse_args(argv)

    try:
        resultado, saida, previa_dir = analisar(args)
        validar.validar(resultado)
        _escrever_json(resultado, saida)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    gpu = resultado["medidas"]["gpu"]
    previas = str(previa_dir) if not args.sem_previas else "desativadas"
    print(f"{resultado['status'].upper()}: {saida}")
    print(
        "cenas={} pose={} fala={} tempo={:.2f}s gpu_pico={}MB previas={}".format(
            len(resultado["cenas"]),
            resultado["pose"]["total_deteccoes"],
            resultado["fala"]["fala_presente"],
            resultado["medidas"]["tempo_total_s"],
            gpu.get("vram_pico_mb"),
            previas,
        )
    )
    for erro in resultado["erros"]:
        print(f"  erro {erro['etapa']}: {erro['mensagem']}", file=sys.stderr)
    for aviso in resultado["avisos"]:
        print(f"  aviso: {aviso}")
    return 0 if resultado["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
