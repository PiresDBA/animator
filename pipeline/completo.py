"""Gerador de video completo do pipeline (Fase B, liberada apenas apos portao M3).

CLI:
    python -m pipeline.completo --projeto ID [--estilo bonecos] [--resolucao 480p] [--formato 16:9]

Saida no stdout:
    OK: projetos/<id>/receipt.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline import cache, render_esqueleto, render_procedural, render_stick, roteador, seguranca, tracking, video

RAIZ = cache.CONFIG["raiz"]
FFMPEG = cache.CONFIG["ffmpeg"]
FFPROBE = cache.CONFIG["ffprobe"]


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_arquivo(caminho: Path) -> str:
    digest = hashlib.sha256()
    with caminho.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duracao_video(caminho: Path) -> float:
    if not Path(FFPROBE).is_file():
        return 0.0
    try:
        cmd = [
            str(FFPROBE), "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(caminho),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
        return float(res.stdout.strip())
    except Exception:
        return 0.0


def resolucao_dimensoes(resolucao: str, formato: str = "16:9") -> tuple[int, int]:
    if formato == "9:16":
        return (480, 854) if resolucao == "480p" else (720, 1280)
    return (854, 480) if resolucao == "480p" else (1280, 720)


def executar(
    projeto_id: str,
    estilo: str = "bonecos",
    resolucao: str = "480p",
    formato: str = "16:9",
    seed: int = 7,
) -> Path:
    """Executa a geracao da Fase B (video completo) apos validacao do portao."""
    inicio_total = time.perf_counter()
    pasta_projeto = RAIZ / "projetos" / projeto_id
    if not pasta_projeto.is_dir():
        raise FileNotFoundError(f"Projeto nao encontrado: {pasta_projeto}")

    # 1. Validacao do portao de aprovacao humana (Regra 1 e 4 do Contrato)
    caminho_avaliacoes = pasta_projeto / "avaliacoes.json"
    if not caminho_avaliacoes.is_file():
        raise RuntimeError("Portao M3 bloqueado: nenhuma avaliacao humana registrada para este projeto.")

    dados_av = json.loads(caminho_avaliacoes.read_text(encoding="utf-8"))
    lista_av = dados_av.get("avaliacoes") if isinstance(dados_av, dict) else dados_av
    if not isinstance(lista_av, list):
        lista_av = []

    aprovacoes = [
        item for item in lista_av
        if isinstance(item, dict)
        and item.get("decisao") == "aprovar"
        and (item.get("estilo") == estilo or not item.get("estilo"))
    ]
    if not aprovacoes:
        raise RuntimeError(
            f"Portao M3 bloqueado: o estilo '{estilo}' nao possui aprovacao humana formal ('aprovar') em avaliacoes.json."
        )
    ultima_aprovacao = aprovacoes[-1]

    # 2. Informacoes do video original
    caminho_meta = pasta_projeto / "meta.json"
    if not caminho_meta.is_file():
        raise FileNotFoundError(f"meta.json nao encontrado em {pasta_projeto}")
    meta = json.loads(caminho_meta.read_text(encoding="utf-8"))
    caminho_video_str = (meta.get("entrada") or {}).get("video")
    if not caminho_video_str:
        raise ValueError(f"Video original nao informado no meta.json do projeto {projeto_id}")
    caminho_video = Path(caminho_video_str)
    if not caminho_video.is_file():
        raise FileNotFoundError(f"Video de entrada nao encontrado: {caminho_video}")

    duracao_total = duracao_video(caminho_video)
    if duracao_total <= 0:
        duracao_total = float((meta.get("entrada") or {}).get("duracao_s") or 5.0)

    largura, altura = resolucao_dimensoes(resolucao, formato)

    pasta_saidas = pasta_projeto / "saidas"
    pasta_filme = pasta_saidas / f"filme_completo_{estilo}"
    pasta_frames = pasta_saidas / f"frames_completo_{estilo}"
    pasta_saidas.mkdir(parents=True, exist_ok=True)
    pasta_filme.mkdir(parents=True, exist_ok=True)
    pasta_frames.mkdir(parents=True, exist_ok=True)

    arquivo_mp4 = pasta_saidas / f"completo_{estilo}.mp4"
    arquivo_miniatura = pasta_saidas / f"miniatura_completo_{estilo}.png"
    arquivo_audio = pasta_saidas / f"audio_completo_{estilo}.wav"
    arquivo_receipt = pasta_saidas / "receipt.json"

    # 3. Roteamento e rastreamento para o video completo
    roteador.executar(projeto_id, estilo_padrao=estilo)
    caminho_mapa = pasta_projeto / "mapa_tecnicas.json"
    cenas_lista = []
    if caminho_mapa.is_file():
        try:
            cenas_lista = json.loads(caminho_mapa.read_text(encoding="utf-8")).get("cenas") or []
        except Exception:
            cenas_lista = []

    rastreio = tracking.rastrear(
        caminho_video,
        inicio_s=0.0,
        fim_s=duracao_total,
        fps_amostra=15.0,
        cenas=cenas_lista,
    )

    if estilo == "bonecos":
        # Renderizacao de rotoscopia esqueletica real (movimento anatomico 100% fluido)
        render_esqueleto.renderizar_rotoscopia_video(
            caminho_video=caminho_video,
            pasta_saida=pasta_frames,
            inicio_s=0.0,
            duracao_s=duracao_total,
            fps=30,
            largura=largura,
            altura=altura,
        )
    else:
        # Estilos procedurais (lego, anime, cartoon, 3d)
        render_procedural.renderizar_estilo(
            caminho_video=caminho_video,
            estilo=estilo,
            pasta_saida=pasta_frames,
            inicio_s=0.0,
            duracao_s=duracao_total,
            fps=30,
            largura=largura,
            altura=altura,
        )

    # 6. Audio e MP4
    render_stick.montar_audio(
        video_origem=caminho_video,
        destino=arquivo_audio,
        inicio_s=0.0,
        duracao_s=duracao_total,
    )

    render_stick.montar_previa(
        pasta_quadros=pasta_frames,
        audio=arquivo_audio if arquivo_audio.is_file() else None,
        destino=arquivo_mp4,
        fps=30,
        duracao_s=duracao_total,
        largura_saida=largura,
        altura_saida=altura,
    )

    render_stick.extrair_miniatura(
        video_mp4=arquivo_mp4,
        destino=arquivo_miniatura,
        posicao_s=min(1.0, duracao_total / 2.0),
    )

    # 7. Laudo de seguranca do video final completo
    laudo_seguranca = seguranca.checar(arquivo_mp4, descricao=meta.get("nome"))
    if laudo_seguranca.get("veredito") == "vermelho":
        raise RuntimeError(
            "Video completo reprovado na checagem final de seguranca infantil (WCAG/volume). "
            + "; ".join(laudo_seguranca.get("mensagens") or [])
        )

    tempo_total = round(time.perf_counter() - inicio_total, 3)

    # 8. Geracao do receipt.json formal (Contrato Seção 5)
    receipt = {
        "versao": 1,
        "projeto": projeto_id,
        "estilo": estilo,
        "gerado_em": agora(),
        "tempo_geracao_s": tempo_total,
        "portao_m3": {
            "aprovado": True,
            "avaliacao_id": ultima_aprovacao.get("id"),
            "data_aprovacao": ultima_aprovacao.get("data"),
            "notas": ultima_aprovacao.get("notas"),
        },
        "entrada": {
            "arquivo": str(caminho_video),
            "sha256": sha256_arquivo(caminho_video),
            "duracao_s": round(duracao_total, 3),
        },
        "saida": {
            "arquivo": str(arquivo_mp4),
            "sha256": sha256_arquivo(arquivo_mp4),
            "tamanho_bytes": arquivo_mp4.stat().st_size if arquivo_mp4.is_file() else 0,
            "formato": formato,
            "resolucao": f"{largura}x{altura}",
            "fps": 30,
            "miniatura": str(arquivo_miniatura),
        },
        "seguranca": laudo_seguranca,
        "software": {
            "os": platform.system() + " " + platform.release(),
            "python": sys.version.split()[0],
            "ffmpeg": "8.1-local",
            "motor_bonecos": "stick-film-1.0",
        },
        "params": {
            "seed": seed,
            "resolucao": resolucao,
            "formato": formato,
        },
    }
    arquivo_receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 9. Atualizacao de meta.json do projeto
    meta["status"] = "concluido"
    meta["completo"] = {
        "estilo": estilo,
        "arquivo": f"projetos/{projeto_id}/saidas/completo_{estilo}.mp4",
        "miniatura": f"projetos/{projeto_id}/saidas/miniatura_completo_{estilo}.png",
        "receipt": f"projetos/{projeto_id}/saidas/receipt.json",
        "duracao_s": round(duracao_total, 3),
        "gerado_em": agora(),
    }
    caminho_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return arquivo_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gerador de video completo (Fase B)")
    parser.add_argument("--projeto", required=True)
    parser.add_argument("--estilo", default="bonecos")
    parser.add_argument("--resolucao", default="480p")
    parser.add_argument("--formato", default="16:9")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)

    try:
        receipt = executar(
            projeto_id=args.projeto,
            estilo=args.estilo,
            resolucao=args.resolucao,
            formato=args.formato,
            seed=args.seed,
        )
        print(f"OK: {receipt.as_posix()}")
        return 0
    except Exception as erro:
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
