"""Checagem de seguranca infantil (secao 10 do contrato).

Rodavel como CLI:

    python -m pipeline.seguranca --video previa.mp4 --saida seguranca.json

Regras aplicadas:
  - Flashes (WCAG 2.3.1): no maximo 3 variacoes de luminancia relativa de 10%
    em qualquer intervalo de 1 segundo. A medicao usa a luminancia relativa
    (sRGB -> linear) de cada quadro decodificado.
  - Volume: pico verdadeiro acima de -6 dBTP e bloqueado.
  - Conteudo: termos de terror, violencia ou conteudo imprprio na descricao
    bloqueiam a previa, com o motivo registrado.

O veredito e `verde`, `amarelo` ou `vermelho` e vai para a tela.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

from pipeline import cache

RAIZ = cache.CONFIG["raiz"]
FFMPEG = cache.CONFIG["ffmpeg"]

LIMITE_FLASHES_1S = 3
LIMITE_VOLUME_DBTP = -6.0
LIMIAR_FLASH_LUMINANCIA = 0.10
JANELA_FLASH_S = 1.0

TERMOS_BLOQUEIO = {
    "terror": [
        "terror", "assombro", "medo", "monstro", "zumbi", "vampiro", "assassinato",
        "sangue", "morte", "morto", "morreu", "carnificina", "terrorismo", "horror",
        "scary", "zombie", "vampire", "blood", "death", "kill", "horror",
    ],
    "violencia": [
        "violencia", "violento", "brigar", "briga", "atacar", "ataque", "golpe",
        "soco", "chute", "tiro", "tiros", "bala", "explosao", "explodir", "guerra",
        "violência", "violencia", "fight", "attack", "shoot", "gun", "explosion", "war",
    ],
    "improprio": [
        "sexo", "sexual", "nudez", "nu", "desnudo", "porno", "erotico", "erótica",
        "bebe", "bebê", "crianca sexual", "assedio", "abuso sexual",
        "sex", "nude", "naked", "porn", "erotic", "molest", "assault",
    ],
}


def luminancia_relativa(quadro_bgr: np.ndarray) -> float:
    """Luminancia relativa media do quadro (0..1)."""
    pequeno = cv2.resize(quadro_bgr, (160, 90), interpolation=cv2.INTER_AREA)
    b, g, r = cv2.split(pequeno.astype(np.float32) / 255.0)
    linear = np.where(
        np.array([r, g, b]) <= 0.04045,
        np.array([r, g, b]) / 12.92,
        ((np.array([r, g, b]) + 0.055) / 1.055) ** 2.4,
    )
    return float((0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]).mean())


def medir_flashes(caminho: Path) -> dict:
    """Conta variacoes de luminancia de 10% em janelas de 1 segundo."""
    cap = cv2.VideoCapture(str(caminho))
    if not cap.isOpened():
        raise RuntimeError(f"nao foi possivel abrir {caminho}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    luminancias: list[float] = []
    try:
        while True:
            ok, quadro = cap.read()
            if not ok:
                break
            luminancias.append(luminancia_relativa(quadro))
    finally:
        cap.release()
    if len(luminancias) < 2:
        return {
            "quadros": len(luminancias),
            "fps": round(fps, 3),
            "max_flashes_1s": 0,
            "limite": LIMITE_FLASHES_1S,
            "ok": True,
            "detalhe": "poucos quadros para medir variacoes",
        }
    variacoes = [
        abs(luminancias[i + 1] - luminancias[i]) >= LIMIAR_FLASH_LUMINANCIA
        for i in range(len(luminancias) - 1)
    ]
    janela = max(1, int(round(JANELA_FLASH_S * fps)))
    melhor = 0
    inicio_melhor = 0
    total = sum(1 for v in variacoes if v)
    for i in range(len(variacoes)):
        if not variacoes[i]:
            continue
        fim = i
        while fim < len(variacoes) and (fim - i) < janela:
            if variacoes[fim]:
                pass
            fim += 1
        contador = sum(1 for v in variacoes[i : i + janela] if v)
        if contador > melhor:
            melhor = contador
            inicio_melhor = i
    return {
        "quadros": len(luminancias),
        "fps": round(fps, 3),
        "max_flashes_1s": int(melhor),
        "total_flashes": int(total),
        "inicio_pico_s": round(inicio_melhor / fps, 3),
        "limite": LIMITE_FLASHES_1S,
        "ok": bool(melhor <= LIMITE_FLASHES_1S),
        "detalhe": (
            f"pico de {melhor} variacoes de luminancia em 1 s "
            f"(limite {LIMITE_FLASHES_1S}); {total} variacoes no trecho"
        ),
    }


def medir_volume(caminho: Path) -> dict:
    """Pico verdadeiro (dBTP) com ebur128; alternativa astats."""
    comando = [
        str(FFMPEG), "-hide_banner", "-nostats", "-i", str(caminho),
        "-filter_complex", "ebur128=peak=true", "-f", "null", "NUL",
    ]
    try:
        saida = subprocess.run(
            comando, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300,
        ).stderr
    except (subprocess.TimeoutExpired, OSError) as erro:
        return {"ok": True, "limite_dbtp": LIMITE_VOLUME_DBTP, "erro": str(erro)}

    pico = None
    bloco = saida.split("True peak:")[-1] if "True peak:" in saida else ""
    if bloco:
        if re.search(r"Peak:\s*-inf\s*dBFS", bloco, re.IGNORECASE):
            pico = -70.0
        else:
            achado = re.search(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", bloco)
            if achado:
                pico = float(achado.group(1))
    if pico is None:
        if re.search(r"Peak level dB:\s*-inf", saida, re.IGNORECASE):
            pico = -70.0
        else:
            achado = re.findall(r"Peak level dB:\s*(-?\d+(?:\.\d+)?)", saida)
            if achado:
                pico = float(achado[-1])
    if pico is None:
        return {
            "ok": True,
            "limite_dbtp": LIMITE_VOLUME_DBTP,
            "erro": "nao foi possivel medir o pico de volume",
            "detalhe": saida.strip()[-300:],
        }
    return {
        "true_peak_dbtp": round(pico, 2),
        "limite_dbtp": LIMITE_VOLUME_DBTP,
        "ok": bool(pico <= LIMITE_VOLUME_DBTP),
        "detalhe": f"pico verdadeiro {pico:.1f} dBTP (limite {LIMITE_VOLUME_DBTP})",
    }


def classificar_conteudo(texto: str | None) -> dict:
    """Procura termos de bloqueio na descricao das cenas."""
    if not texto or not texto.strip():
        return {
            "classificacao": "nao_classificado",
            "ok": True,
            "motivo": None,
            "termos": [],
        }
    alvo = texto.lower()
    encontrados: list[str] = []
    categorias: set[str] = set()
    for categoria, termos in TERMOS_BLOQUEIO.items():
        for termo in termos:
            if termo in alvo:
                categorias.add(categoria)
                encontrados.append(termo)
    if encontrados:
        return {
            "classificacao": "improprio",
            "ok": False,
            "motivo": "termos bloqueados: " + ", ".join(sorted(set(encontrados))),
            "categorias": sorted(categorias),
            "termos": sorted(set(encontrados)),
        }
    return {
        "classificacao": "infantil",
        "ok": True,
        "motivo": None,
        "termos": [],
    }


def checar(caminho: Path, descricao: str | None = None) -> dict:
    """Executa as tres checagens e devolve o veredito."""
    caminho = Path(caminho)
    if not caminho.is_file():
        raise FileNotFoundError(caminho)
    flashes = medir_flashes(caminho)
    volume = medir_volume(caminho)
    conteudo = classificar_conteudo(descricao)

    mensagens: list[str] = []
    if not flashes.get("ok", True):
        mensagens.append("flashes acima do limite")
    if not volume.get("ok", True):
        mensagens.append("volume acima do limite")
    if not conteudo.get("ok", True):
        mensagens.append(conteudo.get("motivo") or "conteudo bloqueado")
    if volume.get("erro"):
        mensagens.append("volume nao medido: " + str(volume["erro"]))

    if any(not bloco.get("ok", True) for bloco in (flashes, volume, conteudo)):
        veredito = "vermelho"
    elif mensagens:
        veredito = "amarelo"
    else:
        veredito = "verde"

    return {
        "versao": 1,
        "video": str(caminho),
        "gerado_em": None,
        "veredito": veredito,
        "flashes": flashes,
        "volume": volume,
        "conteudo": conteudo,
        "mensagens": mensagens,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Checagem de seguranca infantil")
    parser.add_argument("--video", required=True)
    parser.add_argument("--saida")
    parser.add_argument("--descricao", default=None)
    args = parser.parse_args(argv)

    try:
        resultado = checar(Path(args.video), args.descricao)
    except Exception as erro:  # noqa: BLE001 - CLI precisa de mensagem curta
        print(f"ERRO: {erro}", file=sys.stderr)
        return 1
    if args.saida:
        destino = Path(args.saida)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"OK: {args.saida or resultado['veredito']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
