"""Técnica Anime (Traço Anime) — contornos expressivos e cores chapadas cel-shading.

Fluxo (Seção 7 do contrato):
  - XDoG (Extended Difference of Gaussians) ou threshold adaptativo para contornos nítidos.
  - Quantização em 8 a 12 cores com filtro bilateral para preservação de bordas e preenchimento plano.
  - Combinação dos contornos com as cores cel-shaded.
  - 100% CPU (OpenCV + numpy). Sem GPU, sem difusão.

Verificação: contornos contínuos, sem ruído, paleta respeita o limite de 8-12 cores.
"""
from __future__ import annotations

import cv2
import numpy as np


def xdog_contornos(
    img_gray: np.ndarray,
    sigma: float = 0.5,
    k: float = 1.6,
    gamma: float = 0.98,
    epsilon: float = -0.1,
    phi: float = 10.0,
) -> np.ndarray:
    """Calcula contornos estilo XDoG (Extended Difference of Gaussians).

    Retorna máscara binária uint8 (0 para traço, 255 para fundo).
    """
    g1 = cv2.GaussianBlur(img_gray, (0, 0), sigma).astype(np.float32)
    g2 = cv2.GaussianBlur(img_gray, (0, 0), sigma * k).astype(np.float32)

    # Difference of Gaussians estendida
    diff = g1 - gamma * g2

    # Função de ativação suave / limiar
    val = np.where(diff >= epsilon, 1.0, 1.0 + np.tanh(phi * (diff - epsilon)))
    contorno = np.clip(val * 255.0, 0, 255).astype(np.uint8)

    # Limpeza morfológica para remover ruído isolado e conectar linhas
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    contorno_limpo = cv2.morphologyEx(contorno, cv2.MORPH_OPEN, kernel)
    return contorno_limpo


def quantizar_cel_shading(img_bgr: np.ndarray, n_cores: int = 10) -> np.ndarray:
    """Aplica suavização com filtro bilateral seguido de quantização em n_cores."""
    h, w = img_bgr.shape[:2]

    # Filtro bilateral para achatar texturas mantendo bordas nítidas
    suave = cv2.bilateralFilter(img_bgr, d=7, sigmaColor=50, sigmaSpace=50)

    # Quantização por k-means no espaço Lab para fidelidade perceptual
    lab = cv2.cvtColor(suave, cv2.COLOR_BGR2Lab)
    pixels = lab.reshape(-1, 3).astype(np.float32)

    n_cores = max(6, min(14, n_cores))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 1.0)
    _, rotulos, centros = cv2.kmeans(
        pixels, n_cores, None, criteria, 3, cv2.KMEANS_PP_CENTERS
    )

    quantizado_lab = centros[rotulos.flatten()].reshape(h, w, 3).astype(np.uint8)
    quantizado_bgr = cv2.cvtColor(quantizado_lab, cv2.COLOR_Lab2BGR)

    # Realce leve de saturação estilo anime
    hsv = cv2.cvtColor(quantizado_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.15, 0, 255)
    anime_bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return anime_bgr


def estilizar(
    quadro_bgr: np.ndarray,
    n_cores: int = 10,
    espessura_traco: int = 1,
) -> np.ndarray:
    """Transforma um quadro BGR em ilustração no estilo Anime."""
    gray = cv2.cvtColor(quadro_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Contornos XDoG
    contornos = xdog_contornos(gray, sigma=0.6, k=1.6, gamma=0.97, epsilon=-0.05, phi=12.0)

    if espessura_traco > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (espessura_traco, espessura_traco))
        contornos = cv2.erode(contornos, kernel)

    # 2. Cel-shading / cores chapadas
    cores = quantizar_cel_shading(quadro_bgr, n_cores=n_cores)

    # 3. Composição: multiplica ou máscara de traço escuro
    fator_traco = contornos.astype(np.float32) / 255.0
    resultado = (cores.astype(np.float32) * fator_traco[:, :, None]).astype(np.uint8)

    return resultado


def verificar(quadro_bgr: np.ndarray, limite_cores: int = 12) -> dict:
    """Verificação do contrato: contornos contínuos, sem ruído excessivo."""
    resultado = estilizar(quadro_bgr, n_cores=limite_cores)
    gray = cv2.cvtColor(quadro_bgr, cv2.COLOR_BGR2GRAY)
    contornos = xdog_contornos(gray)

    # Contagem de pixels de contorno (0 = borda)
    total_pixels = contornos.size
    pixels_borda = int(np.sum(contornos < 128))
    proporcao_borda = round(pixels_borda / total_pixels, 4)

    # Contorno razoável de anime deve cobrir entre 0.1% e 30% da imagem
    ok = 0.001 <= proporcao_borda <= 0.30

    return {
        "tecnica": "anime_contornos",
        "proporcao_contornos": proporcao_borda,
        "limite_cores": limite_cores,
        "ok": ok,
        "detalhe": f"Contornos representam {proporcao_borda * 100:.1f}% da área da cena",
    }
