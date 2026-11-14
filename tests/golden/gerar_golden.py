#!/usr/bin/env python3
"""Gera o golden set sintetico do M1 (3 clipes de 10 s).

Requisitos:
  - VoiceCraft rodando em http://127.0.0.1:8090 (provider piper local).
  - FFmpeg local em tools/ffmpeg/ffmpeg.exe.
  - Pillow e numpy no .venv do projeto.

Nada de terceiros e baixado: os quadros sao desenhados localmente e a voz e
sintetizada pelo VoiceCraft com o provedor Piper offline.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
GOLDEN = Path(__file__).resolve().parent
FFMPEG = RAIZ / "tools" / "ffmpeg" / "ffmpeg.exe"
FFPROBE = RAIZ / "tools" / "ffmpeg" / "ffprobe.exe"
W, H, FPS, DUR = 1280, 720, 30, 10

FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")
FONT_REG = Path(r"C:\Windows\Fonts\arial.ttf")


def fonte(caminho: Path, tamanho: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(caminho), tamanho)
    except OSError:
        return ImageFont.load_default()


F_TITULO = fonte(FONT_BOLD, 44)
F_GRANDE = fonte(FONT_BOLD, 120)
F_SUB = fonte(FONT_REG, 40)
F_PEQUENA = fonte(FONT_REG, 26)


def gradiente(cor_a: tuple[int, int, int], cor_b: tuple[int, int, int]) -> Image.Image:
    t = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    a = np.array(cor_a, dtype=np.float32)[None, :]
    b = np.array(cor_b, dtype=np.float32)[None, :]
    linhas = (a * (1.0 - t) + b * t).astype(np.uint8)
    return Image.fromarray(np.repeat(linhas[:, None, :], W, axis=1), mode="RGB")


def desenhar_pessoa(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    escala: float,
    cor: tuple[int, int, int],
    contorno: tuple[int, int, int] = (255, 255, 255),
) -> None:
    lw = max(3, int(10 * escala))
    raio = 26 * escala
    ombro_y = cy - 82 * escala
    quadril_y = cy + 18 * escala
    mao_y = cy + 8 * escala
    pe_y = cy + 126 * escala
    draw.ellipse(
        [cx - raio, cy - 132 * escala - raio, cx + raio, cy - 132 * escala + raio],
        fill=cor,
        outline=contorno,
        width=max(2, int(3 * escala)),
    )
    draw.rounded_rectangle(
        [cx - 30 * escala, ombro_y, cx + 30 * escala, quadril_y],
        radius=14 * escala,
        fill=cor,
        outline=contorno,
        width=max(2, int(3 * escala)),
    )
    for lado in (-1, 1):
        draw.line(
            [
                (cx + lado * 24 * escala, ombro_y + 8 * escala),
                (cx + lado * 74 * escala, mao_y),
            ],
            fill=cor,
            width=lw,
        )
        draw.line(
            [
                (cx + lado * 16 * escala, quadril_y),
                (cx + lado * 42 * escala, pe_y),
            ],
            fill=cor,
            width=lw,
        )
        draw.ellipse(
            [
                cx + lado * 74 * escala - 7 * escala,
                mao_y - 7 * escala,
                cx + lado * 74 * escala + 7 * escala,
                mao_y + 7 * escala,
            ],
            fill=cor,
        )
        draw.ellipse(
            [
                cx + lado * 42 * escala - 10 * escala,
                pe_y - 7 * escala,
                cx + lado * 42 * escala + 10 * escala,
                pe_y + 7 * escala,
            ],
            fill=cor,
        )


def texto_centro(draw: ImageDraw.ImageDraw, y: int, texto: str, font: ImageFont.FreeTypeFont,
                 fill: tuple[int, int, int, int] = (255, 255, 255, 255)) -> None:
    caixa = draw.textbbox((0, 0), texto, font=font)
    x = (W - (caixa[2] - caixa[0])) // 2 - caixa[0]
    draw.text((x, y), texto, font=font, fill=fill)


def quadro_estatico(indice: int) -> Image.Image:
    img = gradiente((10, 16, 32), (18, 58, 74))
    draw = ImageDraw.Draw(img)
    draw.line([(80, 600), (W - 80, 600)], fill=(90, 130, 140), width=4)
    desenhar_pessoa(draw, W / 2, 420, 1.45, (240, 190, 80))
    texto_centro(draw, 40, "CENA 1 - PERSONAGEM ESTÁTICO", F_TITULO)
    texto_centro(draw, 650, "golden set sintetico | 10 s | 30 fps", F_PEQUENA, (190, 210, 220, 255))
    return img


def quadro_acao(indice: int) -> Image.Image:
    t = indice / FPS
    if t < 3.0:
        img = gradiente((26, 11, 46), (58, 18, 80))
    elif t < 6.0:
        img = gradiente((46, 11, 11), (90, 26, 26))
    else:
        img = gradiente((11, 46, 26), (26, 90, 58))
    draw = ImageDraw.Draw(img)
    draw.line([(60, 610), (W - 60, 610)], fill=(180, 200, 205), width=4)
    if t <= 5.0:
        p = t / 5.0
    else:
        p = 1.0
    x1 = 200 + 340 * p
    x2 = 1080 - 340 * p
    if t > 5.0:
        q = (t - 5.0) / 5.0
        x1 -= 150 * q
        x2 += 150 * q
    desenhar_pessoa(draw, x1, 420, 1.15, (255, 90, 90))
    desenhar_pessoa(draw, x2, 420, 1.15, (90, 170, 255))
    texto_centro(draw, 40, "CENA 2 - AÇÃO", F_TITULO)
    texto_centro(draw, 650, "duas figuras | cortes em 3 s e 6 s", F_PEQUENA, (220, 220, 220, 255))
    return img


def quadro_texto(indice: int) -> Image.Image:
    t = indice / FPS
    base = gradiente((16, 24, 32), (30, 58, 95)).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    alpha_titulo = int(255 * max(0.0, min(1.0, (t - 0.3) / 1.7)))
    alpha_sub = int(255 * max(0.0, min(1.0, (t - 1.2) / 1.8)))
    texto_centro(draw, 260, "GOLDEN SET", F_GRANDE, (255, 255, 255, alpha_titulo))
    texto_centro(draw, 425, "Teste local de análise", F_SUB, (120, 220, 235, alpha_sub))
    largura = int(420 * max(0.0, min(1.0, (t - 2.0) / 2.0)))
    if largura > 0:
        x0 = (W - largura) // 2
        draw.rounded_rectangle([x0, 505, x0 + largura, 515], radius=5, fill=(120, 220, 235, 220))
    texto_centro(draw, 650, "clipe 3 de 3 | voz Craft Voice / Piper", F_PEQUENA, (200, 215, 225, 255))
    return Image.alpha_composite(base, overlay).convert("RGB")


def sintetizar_voz(texto: str, destino: Path) -> dict:
    corpo = json.dumps(
        {
            "text": texto,
            "language": "pt-BR",
            "provider": "piper",
            "profile": "infantil",
            "format": "wav",
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8090/api/tts",
        data=corpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = r.read()
        if r.status != 200:
            raise RuntimeError(f"VoiceCraft retornou {r.status}")
        destino.write_bytes(dados)
        return {
            "provider": r.headers.get("X-TTS-Provider", "piper"),
            "voice": r.headers.get("X-TTS-Voice", "pt_BR-faber-medium"),
            "elapsed_s": float(r.headers.get("X-TTS-Elapsed", "0") or 0),
        }


def codificar(nome: str, gerar_quadro, audio: Path | None) -> Path:
    destino = GOLDEN / nome
    with tempfile.TemporaryDirectory(dir=GOLDEN, prefix=".frames_") as tmp:
        pasta = Path(tmp)
        for i in range(DUR * FPS):
            gerar_quadro(i).save(pasta / f"{i:05d}.png")
        cmd = [
            str(FFMPEG), "-y", "-hide_banner", "-loglevel", "error",
            "-framerate", str(FPS), "-i", str(pasta / "%05d.png"),
        ]
        if audio is not None:
            cmd += ["-i", str(audio), "-af", "apad"]
        else:
            cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        cmd += [
            "-t", str(DUR),
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
            "-movflags", "+faststart", "-shortest", str(destino),
        ]
        subprocess.run(cmd, check=True)
    return destino


def ffprobe(caminho: Path) -> dict:
    saida = subprocess.check_output(
        [
            str(FFPROBE), "-v", "error",
            "-show_entries", "format=duration,size",
            "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-of", "json", str(caminho),
        ],
        text=True,
    )
    return json.loads(saida)


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def main() -> int:
    if not FFMPEG.is_file():
        raise SystemExit(f"FFmpeg nao encontrado: {FFMPEG}")
    GOLDEN.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=GOLDEN, prefix=".audio_") as tmp:
        pasta = Path(tmp)
        voz1 = pasta / "voz1.wav"
        voz3 = pasta / "voz3.wav"
        info1 = sintetizar_voz(
            "Esta é a primeira cena do conjunto de testes. O personagem está parado no centro da tela.",
            voz1,
        )
        info3 = sintetizar_voz(
            "Este é o terceiro clipe. O texto aparece na tela e a análise local começa agora.",
            voz3,
        )
        clipes = [
            (
                "clipe_01_estatico.mp4",
                quadro_estatico,
                voz1,
                {
                    "id": "clipe_01_estatico",
                    "descricao": "Personagem sintético parado; uma cena; fala presente.",
                    "cenas_esperadas": 1,
                    "fala_esperada": True,
                },
            ),
            (
                "clipe_02_acao.mp4",
                quadro_acao,
                None,
                {
                    "id": "clipe_02_acao",
                    "descricao": "Duas figuras em movimento; cortes de fundo em 3 s e 6 s; sem fala.",
                    "cenas_esperadas": 3,
                    "fala_esperada": False,
                },
            ),
            (
                "clipe_03_texto.mp4",
                quadro_texto,
                voz3,
                {
                    "id": "clipe_03_texto",
                    "descricao": "Cartela de texto com fade; uma cena; fala presente.",
                    "cenas_esperadas": 1,
                    "fala_esperada": True,
                },
            ),
        ]
        manifest = {
            "versao": 1,
            "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fonte": "sintetica",
            "gerado_por": "tests/golden/gerar_golden.py",
            "voz": {
                "ferramenta": "craft_voice",
                "provider": info1["provider"],
                "voice": info1["voice"],
                "profile": "infantil",
                "elapsed_s": [info1["elapsed_s"], info3["elapsed_s"]],
            },
            "licenca": "gerado localmente; sem material de terceiros",
            "clipes": [],
        }
        for nome, gerar, audio, meta in clipes:
            caminho = codificar(nome, gerar, audio)
            probe = ffprobe(caminho)
            video = next(s for s in probe["streams"] if s["codec_type"] == "video")
            audio_stream = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
            meta.update(
                {
                    "arquivo": nome,
                    "duracao_s": round(float(probe["format"]["duration"]), 3),
                    "bytes": int(probe["format"]["size"]),
                    "sha256": sha256(caminho),
                    "resolucao": [video["width"], video["height"]],
                    "fps": video["r_frame_rate"],
                    "video_codec": video["codec_name"],
                    "audio_codec": audio_stream["codec_name"] if audio_stream else None,
                    "audio_presente": audio_stream is not None,
                }
            )
            manifest["clipes"].append(meta)
            print(f"OK: {caminho} ({meta['duracao_s']} s, {meta['bytes']} bytes)")

    (GOLDEN / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: {GOLDEN / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
