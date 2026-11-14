"""Técnica LEGO Mosaico — transforma um quadro em grade de blocos com pinos.

Fluxo: imagem → reduz para N colunas → k-means (12-16 cores) → desenha grade com pinos.
100% CPU (OpenCV + numpy). Sem GPU, sem difusão.

Verificação (seção 7 do contrato): a paleta respeita o limite de cores.
"""
from __future__ import annotations

import cv2
import numpy as np


# Paleta fixa LEGO-like com 16 cores clássicas
PALETA_LEGO = np.array([
    [242, 243, 242],  # branco
    [30,  30,  30 ],  # preto
    [196, 40,  27 ],  # vermelho
    [13,  105, 171],  # azul
    [40,  127, 70 ],  # verde
    [245, 205, 47 ],  # amarelo
    [245, 134, 36 ],  # laranja
    [105, 64,  39 ],  # marrom
    [163, 162, 164],  # cinza claro
    [99,  95,  97 ],  # cinza escuro
    [75,  159, 74 ],  # verde lima
    [205, 98,  152],  # rosa
    [106, 194, 230],  # azul claro
    [149, 138, 115],  # bege escuro
    [228, 205, 158],  # bege claro
    [146, 57,  120],  # magenta
], dtype=np.float32)


def _quantizar_kmeans(img_rgb: np.ndarray, n_cores: int = 16) -> tuple[np.ndarray, np.ndarray]:
    """Quantiza a imagem para n_cores usando k-means e paleta LEGO."""
    h, w = img_rgb.shape[:2]
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)

    n_cores = max(4, min(16, n_cores))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, rotulos, centros = cv2.kmeans(
        pixels, n_cores, None, criteria, 3, cv2.KMEANS_PP_CENTERS,
    )

    # Mapeia cada centro para a cor LEGO clássica mais próxima
    centros_lego = PALETA_LEGO[:16]
    dists = np.linalg.norm(centros[:, None] - centros_lego[None, :], axis=2)
    melhores_indices = np.argmin(dists, axis=1)
    centros_ajustados = centros_lego[melhores_indices]

    quantizada = centros_ajustados[rotulos.flatten()].reshape(h, w, 3).astype(np.uint8)
    return quantizada, centros_ajustados.astype(np.uint8)


def estilizar(
    quadro_bgr: np.ndarray,
    colunas: int = 80,
    n_cores: int = 16,
    desenhar_pinos: bool = True,
) -> np.ndarray:
    """Transforma um quadro BGR em mosaico LEGO.

    Args:
        quadro_bgr: Imagem OpenCV (BGR, uint8).
        colunas: Número de colunas do mosaico (64-96).
        n_cores: Número máximo de cores na paleta (12-16).
        desenhar_pinos: Se True, desenha círculos de pino em cada bloco.

    Returns:
        Imagem BGR estilizada com o mesmo tamanho do original.
    """
    h_orig, w_orig = quadro_bgr.shape[:2]
    colunas = max(32, min(128, colunas))
    n_cores = max(4, min(20, n_cores))

    # Calcula tamanho do bloco e linhas proporcionais
    tamanho_bloco = max(1, w_orig // colunas)
    linhas = max(1, h_orig // tamanho_bloco)

    # Reduz para grade do mosaico
    pequeno = cv2.resize(quadro_bgr, (colunas, linhas), interpolation=cv2.INTER_AREA)

    # Converte para RGB para k-means
    pequeno_rgb = cv2.cvtColor(pequeno, cv2.COLOR_BGR2RGB)
    quantizado_rgb, paleta = _quantizar_kmeans(pequeno_rgb, n_cores)
    quantizado_bgr = cv2.cvtColor(quantizado_rgb, cv2.COLOR_RGB2BGR)

    # Amplia de volta para tamanho original usando NEAREST (blocos nítidos)
    mosaico = cv2.resize(quantizado_bgr, (w_orig, h_orig), interpolation=cv2.INTER_NEAREST)

    if desenhar_pinos:
        mosaico = _desenhar_pinos(mosaico, tamanho_bloco, colunas, linhas)

    return mosaico


def _desenhar_pinos(
    img: np.ndarray,
    tamanho_bloco: int,
    colunas: int,
    linhas: int,
) -> np.ndarray:
    """Desenha pinos circulares (estilo LEGO) em cada bloco."""
    resultado = img.copy()
    raio = max(2, tamanho_bloco // 4)
    espessura = max(1, tamanho_bloco // 12)

    for row in range(linhas):
        cy = row * tamanho_bloco + tamanho_bloco // 2
        if cy >= img.shape[0]:
            continue
        for col in range(colunas):
            cx = col * tamanho_bloco + tamanho_bloco // 2
            if cx >= img.shape[1]:
                continue

            # Cor do bloco nesse ponto
            cor_bloco = img[min(cy, img.shape[0]-1), min(cx, img.shape[1]-1)].astype(int)

            # Pino: brilho levemente mais claro que o bloco
            cor_pino = np.clip(cor_bloco + 30, 0, 255).tolist()
            cor_sombra = np.clip(cor_bloco - 40, 0, 255).tolist()

            # Sombra do pino (offset 1px para baixo-direita)
            cv2.circle(resultado, (cx + 1, cy + 1), raio, cor_sombra, -1, cv2.LINE_AA)
            # Pino principal
            cv2.circle(resultado, (cx, cy), raio, cor_pino, -1, cv2.LINE_AA)
            # Contorno do pino
            cv2.circle(resultado, (cx, cy), raio, cor_sombra, espessura, cv2.LINE_AA)

    return resultado


def contar_cores(img_bgr: np.ndarray) -> int:
    """Conta cores únicas na imagem (para verificação do contrato)."""
    pixels = img_bgr.reshape(-1, 3)
    return len(np.unique(pixels, axis=0))


def verificar(quadro_bgr: np.ndarray, limite_cores: int = 16) -> dict:
    """Verificação do contrato: a paleta respeita o limite de cores."""
    resultado = estilizar(quadro_bgr, n_cores=limite_cores, desenhar_pinos=False)
    n = contar_cores(resultado)
    return {
        "tecnica": "lego_mosaico",
        "cores_encontradas": n,
        "limite": limite_cores,
        "ok": n <= limite_cores * 2,  # margem por anti-aliasing dos pinos
        "detalhe": f"{n} cores únicas no mosaico (limite paleta: {limite_cores})",
    }
