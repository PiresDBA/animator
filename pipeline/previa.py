"""Gerador de previa do pipeline (contrato M2, secao 3 e 4.1).

CLI:
    python -m pipeline.previa --projeto ID --estilo bonecos [--trecho-inicio S] [--trecho-fim S] [--seed N] [--resolucao 480p]

Saida no stdout:
    OK: projetos/<id>/previa.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline import cache, render_comfy, render_esqueleto, render_procedural, render_stick, roteador, seguranca, tracking

RAIZ = cache.CONFIG["raiz"]


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def resolucao_dimensoes(resolucao: str) -> tuple[int, int]:
    """Retorna (largura, altura) para a resolucao solicitada."""
    if resolucao == "720p":
        return 1280, 720
    return 854, 480


def proximo_indice_previa(saidas_dir: Path, estilo: str) -> int:
    """Calcula o proximo numero sequencial para a previa do estilo (ex: bonecos_001)."""
    maior = 0
    padrao = f"previa_{estilo}_*.mp4"
    for arq in saidas_dir.glob(padrao):
        nome = arq.stem  # previa_bonecos_001
        partes = nome.rsplit("_", 1)
        if len(partes) == 2 and partes[1].isdigit():
            num = int(partes[1])
            if num > maior:
                maior = num
    return maior + 1


def executar(
    projeto_id: str,
    estilo: str = "bonecos",
    trecho_inicio: float = 0.0,
    trecho_fim: float = 5.0,
    seed: int = 7,
    resolucao: str = "480p",
) -> Path:
    """Gera a previa para o projeto especificado."""
    inicio_total = time.perf_counter()
    pasta_projeto = RAIZ / "projetos" / projeto_id
    if not pasta_projeto.is_dir():
        raise FileNotFoundError(f"Projeto nao encontrado: {pasta_projeto}")

    caminho_meta = pasta_projeto / "meta.json"
    if not caminho_meta.is_file():
        raise FileNotFoundError(f"meta.json nao encontrado em {pasta_projeto}")

    meta = json.loads(caminho_meta.read_text(encoding="utf-8"))
    caminho_video_str = (meta.get("entrada") or {}).get("video")
    if not caminho_video_str:
        raise ValueError(f"Video de entrada nao informado no meta.json do projeto {projeto_id}")

    caminho_video = Path(caminho_video_str)
    if not caminho_video.is_file():
        raise FileNotFoundError(f"Video original nao encontrado: {caminho_video}")

    duracao_s = max(0.5, round(trecho_fim - trecho_inicio, 3))
    largura, altura = resolucao_dimensoes(resolucao)

    # 1. Roteador por cena (garante mapa_tecnicas.json)
    roteador.executar(projeto_id, estilo_padrao=estilo)
    caminho_mapa = pasta_projeto / "mapa_tecnicas.json"
    mapa_tecnicas_dados: dict[str, Any] = {}
    if caminho_mapa.is_file():
        try:
            mapa_tecnicas_dados = json.loads(caminho_mapa.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            mapa_tecnicas_dados = {"cenas": []}

    # 2. Rastreamento de atores no trecho (sem GPU)
    cenas_lista = mapa_tecnicas_dados.get("cenas") or []
    rastreio = tracking.rastrear(
        caminho_video,
        inicio_s=trecho_inicio,
        fim_s=trecho_fim,
        fps_amostra=15.0,
        cenas=cenas_lista,
    )

    # 3. Preparacao de pastas
    pasta_saidas = pasta_projeto / "saidas"
    pasta_filme = pasta_saidas / f"filme_{estilo}"
    pasta_frames = pasta_saidas / f"frames_{estilo}"
    pasta_saidas.mkdir(parents=True, exist_ok=True)
    pasta_filme.mkdir(parents=True, exist_ok=True)
    pasta_frames.mkdir(parents=True, exist_ok=True)

    # Indice e nomes de arquivos
    indice = proximo_indice_previa(pasta_saidas, estilo)
    previa_id = f"{estilo}_{indice:03d}"
    arquivo_mp4 = pasta_saidas / f"previa_{previa_id}.mp4"
    arquivo_miniatura = pasta_saidas / f"miniatura_{previa_id}.png"
    arquivo_audio = pasta_saidas / "audio_trecho.wav"

    gerou_via_comfy = False
    if estilo == "bonecos":
        # Renderizacao de rotoscopia esqueletica real (movimento anatomico 100% fluido)
        render_esqueleto.renderizar_rotoscopia_video(
            caminho_video=caminho_video,
            pasta_saida=pasta_frames,
            inicio_s=trecho_inicio,
            duracao_s=duracao_s,
            fps=30,
            largura=largura,
            altura=altura,
        )
    else:
        # Tenta renderizacao de alta fidelidade via ComfyUI (AnimateDiff + DreamShaper 8)
        if render_comfy.comfy_disponivel():
            try:
                gerou_via_comfy = render_comfy.renderizar_animacao_alta_qualidade(
                    caminho_video=caminho_video,
                    estilo=estilo,
                    destino_mp4=arquivo_mp4,
                    duracao_s=min(3.0, duracao_s),
                    seed=seed,
                )
            except Exception:
                gerou_via_comfy = False

        if not gerou_via_comfy:
            # Fallback procedural
            render_procedural.renderizar_estilo(
                caminho_video=caminho_video,
                estilo=estilo,
                pasta_saida=pasta_frames,
                inicio_s=trecho_inicio,
                duracao_s=duracao_s,
                fps=30,
                largura=largura,
                altura=altura,
            )

    # 6. Extracao de audio original e montagem da previa MP4
    render_stick.montar_audio(
        video_origem=caminho_video,
        destino=arquivo_audio,
        inicio_s=trecho_inicio,
        duracao_s=duracao_s,
    )

    if not gerou_via_comfy:
        render_stick.montar_previa(
            pasta_quadros=pasta_frames,
            audio=arquivo_audio if arquivo_audio.is_file() else None,
            destino=arquivo_mp4,
            fps=30,
            duracao_s=duracao_s,
            largura_saida=largura,
            altura_saida=altura,
        )
    else:
        # Adiciona o audio sincronizado ao video gerado pelo ComfyUI se necessario
        if arquivo_audio.is_file():
            arquivo_temp = arquivo_mp4.with_name(arquivo_mp4.stem + "_temp.mp4")
            import subprocess
            cmd = [
                str(cache.CONFIG["ffmpeg"]), "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(arquivo_mp4),
                "-i", str(arquivo_audio),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                "-shortest", str(arquivo_temp),
            ]
            try:
                subprocess.run(cmd, check=True)
                arquivo_temp.replace(arquivo_mp4)
            except Exception:
                if arquivo_temp.is_file():
                    arquivo_temp.unlink(missing_ok=True)

    # 7. Extracao de miniatura
    render_stick.extrair_miniatura(
        video_mp4=arquivo_mp4,
        destino=arquivo_miniatura,
        posicao_s=min(1.0, duracao_s / 2.0),
    )

    # 8. Verificacao de seguranca infantil
    laudo_seguranca = seguranca.checar(arquivo_mp4, descricao=meta.get("nome"))

    tempo_total = round(time.perf_counter() - inicio_total, 3)

    # 9. Formatacao de caminhos relativos para o contrato
    try:
        rel_mp4 = arquivo_mp4.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        rel_mp4 = arquivo_mp4.as_posix()

    try:
        rel_miniatura = arquivo_miniatura.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        rel_miniatura = arquivo_miniatura.as_posix()

    estilo_rotulos = {
        "bonecos": "Bonecos de palito",
        "lego": "Mosaico de blocos",
        "anime": "Anime",
        "cartoon": "Cartoon",
        "3d": "3D",
    }

    resultado_previa = {
        "versao": 1,
        "projeto": projeto_id,
        "previa_id": previa_id,
        "estilo": estilo,
        "estilo_rotulo": estilo_rotulos.get(estilo, estilo),
        "status": "pronto",
        "arquivo": rel_mp4,
        "miniatura": rel_miniatura,
        "trecho": {
            "inicio_s": round(trecho_inicio, 3),
            "fim_s": round(trecho_fim, 3),
            "duracao_s": duracao_s,
        },
        "resolucao": f"{largura}x{altura}",
        "fps": 30,
        "gerado_em": agora(),
        "tempo_geracao_s": tempo_total,
        "seguranca": {
            "veredito": laudo_seguranca.get("veredito", "verde"),
            "flashes": laudo_seguranca.get("flashes", {}),
            "volume": laudo_seguranca.get("volume", {}),
            "conteudo": laudo_seguranca.get("conteudo", {}),
            "mensagens": laudo_seguranca.get("mensagens", []),
        },
        "mapa_tecnicas": mapa_tecnicas_dados,
        "params": {
            "seed": seed,
            "resolucao": resolucao,
            "modo": "rapido",
            "versao_preset": 1,
        },
        "erro": None,
    }

    caminho_previa_json = pasta_projeto / "previa.json"
    caminho_previa_json.write_text(
        json.dumps(resultado_previa, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return caminho_previa_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Gerador de previa do pipeline.")
    parser.add_argument("--projeto", required=True, help="ID do projeto")
    parser.add_argument("--estilo", default="bonecos", help="Estilo da previa (padrao: bonecos)")
    parser.add_argument("--trecho-inicio", type=float, default=0.0, help="Inicio em segundos")
    parser.add_argument("--trecho-fim", type=float, default=5.0, help="Fim em segundos")
    parser.add_argument("--seed", type=int, default=7, help="Seed para reproducibilidade")
    parser.add_argument("--resolucao", default="480p", choices=["480p", "720p"], help="Resolucao")
    args = parser.parse_args()

    try:
        saida = executar(
            projeto_id=args.projeto,
            estilo=args.estilo,
            trecho_inicio=args.trecho_inicio,
            trecho_fim=args.trecho_fim,
            seed=args.seed,
            resolucao=args.resolucao,
        )
        try:
            relativo = saida.resolve().relative_to(RAIZ).as_posix()
        except ValueError:
            relativo = saida.as_posix()
        print(f"OK: {relativo}")
        sys.exit(0)
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
