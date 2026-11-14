"""Adaptador para o motor de bonecos de palito (stick-film).

Este modulo NAO reescreve o motor: ele le o motor em
`D:\\PROJETOS-IA\\stick-film\\stick-film`, gera um filme (film.json + scene.js +
characters/*.json) a partir do rastreamento do M2 e chama `render.mjs` para
produzir os quadros.

Regras do D023 (movimento translacao global):
  - a pose fica congelada (sem ciclo de caminhada, sem articulacao);
  - a translacao vem do trilho medido no video original;
  - squash, drag, blur e piscadas ficam desligados.

O que este modulo faz:
  1. `construir_filme`  -> escreve a pasta do filme;
  2. `renderizar_quadros` -> chama o motor e devolve os PNGs;
  3. `montar_audio` e `montar_previa` -> sincroniza o audio original e
     codifica o MP4 da previa.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import numpy as np

from pipeline import cache, video

RAIZ = cache.CONFIG["raiz"]
FFMPEG = cache.CONFIG["ffmpeg"]
FFPROBE = cache.CONFIG["ffprobe"]

CANDIDATOS_HOME = [
    Path(r"C:\Users\Pires\StickFilms"),
    Path(r"C:\Users\Pires\.claude\skills\stick-film"),
    Path(r"C:\Users\Pires\.codex\skills\stick-film"),
    Path(r"C:\Users\Pires\.opencode\skills\stick-film"),
]


def caminho_motor() -> Path:
    """Localiza a copia aprovada do motor (D016)."""
    configuracao = RAIZ / "config.json"
    if configuracao.is_file():
        dados = json.loads(configuracao.read_text(encoding="utf-8"))
        caminho = dados.get("caminhos", {}).get("motor_bonecos")
        if caminho and Path(caminho).is_dir():
            return Path(caminho)
    padrao = Path(r"D:\PROJETOS-IA\stick-film\stick-film")
    return padrao


def descobrir_home() -> Path:
    """Pasta que contem .tools/node_modules/playwright-core (usada pelo motor)."""
    ambiente = os.environ.get("STICKFILM_HOME")
    candidatos = ([Path(ambiente)] if ambiente else []) + CANDIDATOS_HOME
    for candidato in candidatos:
        if (candidato / ".tools" / "node_modules" / "playwright-core").is_dir():
            return candidato
    return candidatos[-1]


def _cor_fundo(caminho_video: Path, inicio: float, fim: float) -> str:
    """Cor predominante do fundo (para o papel do motor)."""
    tempos = video.tempos_amostra(max(0.1, fim - inicio), 4.0)
    tempos = [min(inicio + t, max(inicio, fim - 0.05)) for t in tempos][:4]
    amostras = [q for _, q in video.ler_quadros(caminho_video, tempos)]
    if not amostras:
        return "#1a1030"
    pilha = np.stack(amostras)
    mediana = np.median(pilha.reshape(-1, 3), axis=0)
    b, g, r = (int(max(0, min(255, v))) for v in mediana)
    return f"#{r:02x}{g:02x}{b:02x}"


def _interpolar_js(trilho: list[dict], inicio: float) -> str:
    """Serializa o trilho como constante JS com tempos relativos ao trecho."""
    pontos = []
    for ponto in trilho:
        t = round(float(ponto["t"]) - inicio, 4)
        if t < 0:
            continue
        pontos.append([t, round(float(ponto["x"]), 2), int(ponto["altura"])])
    if not pontos:
        pontos = [[0.0, 0.0, 320]]
    return json.dumps(pontos, ensure_ascii=False)


def _direcao_js(trilho: list[dict], inicio: float) -> str:
    """Serie de direcao (1 = direita, -1 = esquerda) derivada da velocidade."""
    pontos = []
    for indice, ponto in enumerate(trilho):
        t = round(float(ponto["t"]) - inicio, 4)
        if t < 0:
            continue
        anterior = trilho[indice - 1] if indice > 0 else ponto
        dx = float(ponto["x"]) - float(anterior["x"])
        if abs(dx) < 0.4:
            direcao = pontos[-1][1] if pontos else 1
        else:
            direcao = 1 if dx > 0 else -1
        pontos.append([t, direcao])
    return json.dumps(pontos, ensure_ascii=False)


def construir_filme(
    rastreio: dict,
    pasta_filme: Path,
    largura: int = 1280,
    altura: int = 720,
    fps: int = 30,
    duracao: float = 5.0,
    seed: int = 7,
    cor_fundo: str = "#1a1030",
) -> dict:
    """Escreve film.json, characters/*.json e scene.js. Devolve o resumo."""
    pasta_filme.mkdir(parents=True, exist_ok=True)
    inicio = float(rastreio["trecho"]["inicio_s"])
    atores = rastreio.get("atores", [])
    if not atores:
        raise RuntimeError("nenhum ator rastreado no trecho")

    gy = 0
    bases = []
    for indice, ator in enumerate(atores):
        alturas = [p["altura"] for p in ator["trilho"]]
        rodapes = [p["y"] + p["altura"] / 2.0 for p in ator["trilho"]]
        altura_corpo = int(np.clip(round(float(np.median(alturas))), 120, 900))
        rodape = float(np.median(rodapes))
        gy = max(gy, rodape)
        bases.append(
            {
                "id": ator["id"],
                "altura": altura_corpo,
                "rodape": round(rodape, 2),
                "cor": ator.get("cor_hex", "#d29e23"),
            }
        )
    gy = int(round(gy))

    pasta_personagens = pasta_filme / "characters"
    pasta_personagens.mkdir(parents=True, exist_ok=True)
    cast: dict[str, dict] = {}
    for indice, base in enumerate(bases):
        nome = base["id"]
        arquivo = pasta_personagens / f"{nome}.json"
        personagem = {
            "name": f"Ator {indice + 1}",
            "slug": nome,
            "style": "flat",
            "palette": {
                "body": base["cor"],
                "shirt": base["cor"],
                "head": base["cor"],
                "hand": base["cor"],
            },
            "body": {"height": base["altura"], "line": 0.0205},
            "face": {"eyes": "none", "brows": False, "mouth": "none"},
            "notes": "gerado pelo adaptador do M2 a partir do rastreamento",
        }
        arquivo.write_text(json.dumps(personagem, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        cast[nome] = {"character": str(arquivo), "override": {"palette": {"body": base["cor"]}}}

    linhas_atores = []
    for indice, ator in enumerate(atores):
        nome_ator = f"ator{indice + 1}"
        trilha = ator.get("trilho") or []
        if trilha:
            x_ini = round(float(trilha[0]["x"]) - (largura / 2.0), 1)
            x_fim = round(float(trilha[-1]["x"]) - (largura / 2.0), 1)
        else:
            x_ini = -180.0 if indice == 0 else 180.0
            x_fim = -40.0 if indice == 0 else 40.0

        # Facing inicial: olhando para o centro se parado, ou na direcao do movimento
        if abs(x_fim - x_ini) > 5:
            facing = 1 if x_fim > x_ini else -1
        else:
            facing = 1 if x_ini <= 0 else -1

        linha = f"""  const {nome_ator} = E.actor('{nome_ator}', {{ x: {x_ini}, facing: {facing}, noBlink: true }});
  {nome_ator}.pose(0, DURACAO, 'neutral');
  {nome_ator}.walk(0.2, Math.max(0.4, DURACAO - 0.2), {x_fim}, {{ steps: false }});"""
        linhas_atores.append(linha)

    codigo_atores = "\n\n".join(linhas_atores)
    cena = f"""// Gerado por pipeline/render_stick.py (M2). Nao editar a mao.
const DURACAO = {duracao};

SF.defineFilm((E) => {{
  E.set('ground');

{codigo_atores}

  E.camera([[0, {{ x: 0, z: 1.0 }}]]);
  return {{ duration: DURACAO }};
}});
"""
    (pasta_filme / "scene.js").write_text(cena, encoding="utf-8")

    filme = {
        "title": "Previa M2 - bonecos de palito",
        "width": largura,
        "height": altura,
        "fps": fps,
        "duration": duracao,
        "style": "flat",
        "palette": {
            "ink": "#f4f4f4",
            "paper": cor_fundo,
            "ground": cor_fundo,
            "accent": "#22d3ee",
        },
        "cast": cast,
        "look": {"squash": 0, "drag": 0, "blur": 0, "shade": False, "shadows": True},
        "cues": {},
    }
    (pasta_filme / "film.json").write_text(json.dumps(filme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "pasta": str(pasta_filme),
        "filme_json": str(pasta_filme / "film.json"),
        "scene_js": str(pasta_filme / "scene.js"),
        "atores": bases,
        "gy": gy,
        "mundo_x_inicial": 0.0,
    }


def renderizar_quadros(
    pasta_filme: Path,
    numero_quadros: int,
    saida: Path,
    workers: int = 2,
    timeout_s: int = 900,
) -> dict:
    """Chama o motor (render.mjs frames) e devolve os quadros gerados."""
    motor = caminho_motor()
    render = motor / "engine" / "render.mjs"
    if not render.is_file():
        raise FileNotFoundError(f"motor nao encontrado: {render}")
    saida.mkdir(parents=True, exist_ok=True)
    for antigo in saida.glob("f_*.png"):
        antigo.unlink()
    ambiente = os.environ.copy()
    ambiente["STICKFILM_HOME"] = str(descobrir_home())
    comando = [
        "node",
        str(render),
        "frames",
        str(pasta_filme),
        "--from",
        "0",
        "--to",
        str(numero_quadros),
        "--out",
        str(saida),
        "--workers",
        str(max(1, workers)),
    ]
    inicio = time.perf_counter()
    processo = subprocess.run(
        comando,
        cwd=str(pasta_filme),
        env=ambiente,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
    )
    duracao = time.perf_counter() - inicio
    quadros = sorted(saida.glob("f_*.png"))
    if processo.returncode != 0 or not quadros:
        raise RuntimeError(
            "motor falhou: "
            + (processo.stderr or processo.stdout or "sem saida")[-800:]
        )
    return {
        "quadros": len(quadros),
        "tempo_s": round(duracao, 3),
        "comando": " ".join(comando),
        "stderr": (processo.stderr or "").strip()[-600:],
    }


def _audio_tem_som(caminho_audio: Path) -> bool:
    """Verifica se o audio tem sinal real ou se e totalmente silencioso."""
    if not caminho_audio.is_file() or caminho_audio.stat().st_size < 1000:
        return False
    try:
        import re
        res = subprocess.run(
            [str(FFMPEG), "-i", str(caminho_audio), "-af", "volumedetect", "-f", "null", "-"],
            capture_output=True, text=True, errors="replace", timeout=10,
        )
        if "max_volume: -inf dB" in res.stderr:
            return False
        m = re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?)\s*dB", res.stderr)
        if m and float(m.group(1)) <= -75.0:
            return False
        return True
    except Exception:
        return False


def _gerar_som_ludico(destino: Path, duracao_s: float) -> Path:
    """Gera uma trilha harmonica infantil suave quando o video original e mudo."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    # Acordes de marimba/piano em Do maior com decaimento suave
    filtro = (
        f"aevalsrc='0.08*sin(2*PI*261.63*t)*exp(-3*mod(t,1.25)) + "
        f"0.07*sin(2*PI*329.63*t)*exp(-3*mod(t+0.3,1.25)) + "
        f"0.06*sin(2*PI*392.00*t)*exp(-3*mod(t+0.6,1.25)) + "
        f"0.05*sin(2*PI*523.25*t)*exp(-3*mod(t+0.9,1.25))':"
        f"sample_rate=48000:duration={duracao_s:.3f},afade=t=in:ss=0:d=0.3,afade=t=out:st={max(0.1, duracao_s - 0.5):.3f}:d=0.5"
    )
    comando = [
        str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", filtro,
        "-c:a", "pcm_s16le", str(destino),
    ]
    subprocess.run(comando, check=True)
    return destino


def montar_audio(
    video_origem: Path,
    destino: Path,
    inicio_s: float,
    duracao_s: float,
    tem_audio: bool = True,
) -> Path:
    """Extrai o trecho de audio original. Se for mudo, gera harmonia ludica."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if tem_audio:
        comando = [
            str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{inicio_s:.3f}", "-t", f"{duracao_s:.3f}",
            "-i", str(video_origem),
            "-vn", "-ac", "2", "-ar", "48000",
            "-c:a", "pcm_s16le", str(destino),
        ]
        try:
            subprocess.run(comando, check=True)
            if _audio_tem_som(destino):
                return destino
        except subprocess.SubprocessError:
            pass

    # Se o audio original e ausente ou 100% mudo, gera som ludico infantil
    return _gerar_som_ludico(destino, duracao_s)


def montar_previa(
    pasta_quadros: Path,
    audio: Path | None,
    destino: Path,
    fps: int = 30,
    duracao_s: float = 5.0,
    largura_saida: int = 854,
    altura_saida: int = 480,
    crf: int = 20,
) -> dict:
    """Codifica os quadros em MP4 e sincroniza o audio original."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    comando = [
        str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
        "-framerate", str(fps),
        "-i", str(pasta_quadros / "f_%05d.png"),
    ]
    if audio is not None and audio.is_file():
        comando += ["-i", str(audio)]
    comando += [
        "-t", f"{duracao_s:.3f}",
        "-vf", f"scale={largura_saida}:{altura_saida}:flags=lanczos",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-pix_fmt", "yuv420p",
    ]
    if audio is not None and audio.is_file():
        comando += ["-c:a", "aac", "-b:a", "160k", "-ar", "48000"]
    else:
        comando += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-c:a", "aac", "-b:a", "128k"]
    comando += ["-movflags", "+faststart", "-shortest", str(destino)]
    inicio = time.perf_counter()
    subprocess.run(comando, check=True)
    return {
        "arquivo": str(destino),
        "bytes": destino.stat().st_size if destino.is_file() else 0,
        "tempo_s": round(time.perf_counter() - inicio, 3),
        "comando": " ".join(comando),
    }


def extrair_miniatura(video_mp4: Path, destino: Path, posicao_s: float = 1.0) -> Path:
    """Gera a miniatura a partir do quadro da previa."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    comando = [
        str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{posicao_s:.3f}", "-i", str(video_mp4),
        "-frames:v", "1", str(destino),
    ]
    subprocess.run(comando, check=True)
    return destino


def limpar(pasta: Path) -> None:
    shutil.rmtree(pasta, ignore_errors=True)
