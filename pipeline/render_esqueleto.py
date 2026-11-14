"""Renderizador de Rotoscopia Esqueletica Real (Bonecos de Palito Expressivos).

Extrai quadro a quadro as poses humanas reais via YOLOv8n-pose e desenha
os bonecos de palito copiando fielmente toda a movimentacao, danca, gestos,
saltos e articulacoes do video original, com suavizacao temporal One-Euro.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from ultralytics import YOLO

from pipeline import cache

RAIZ = cache.CONFIG["raiz"]
MODELO_YOLO = RAIZ / ".cache" / "modelos" / "yolov8n-pose.pt"
if not MODELO_YOLO.is_file():
    MODELO_YOLO = Path("yolov8n-pose.pt")


class SuavizadorOneEuro:
    """Filtro One Euro para suavizacao de keypoints sem latencia perceptivel."""

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev: np.ndarray | None = None
        self.dx_prev: np.ndarray | None = None
        self.t_prev: float | None = None

    def _alpha(self, cutoff: np.ndarray, dt: float) -> np.ndarray:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def filtrar(self, x: np.ndarray, t: float) -> np.ndarray:
        if self.x_prev is None:
            self.x_prev = x.copy()
            self.dx_prev = np.zeros_like(x)
            self.t_prev = t
            return x

        dt = max(1e-4, t - (self.t_prev or t))
        self.t_prev = t

        dx = (x - self.x_prev) / dt
        alpha_d = self._alpha(np.full_like(dx, self.d_cutoff), dt)
        dx_hat = alpha_d * dx + (1.0 - alpha_d) * self.dx_prev
        self.dx_prev = dx_hat

        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        alpha = self._alpha(cutoff, dt)
        x_hat = alpha * x + (1.0 - alpha) * self.x_prev
        self.x_prev = x_hat
        return x_hat


CONEXOES_CORPO = [
    (5, 6),   # ombro esquerdo - ombro direito
    (5, 7),   # ombro esquerdo - cotovelo esquerdo
    (7, 9),   # cotovelo esquerdo - pulso esquerdo
    (6, 8),   # ombro direito - cotovelo direito
    (8, 10),  # cotovelo direito - pulso direito
    (5, 11),  # ombro esquerdo - quadril esquerdo
    (6, 12),  # ombro direito - quadril direito
    (11, 12), # quadril esquerdo - quadril direito
    (11, 13), # quadril esquerdo - joelho esquerdo
    (13, 15), # joelho esquerdo - tornozelo esquerdo
    (12, 14), # quadril direito - joelho direito
    (14, 16), # joelho direito - tornozelo direito
]


def desenhar_cenario_ludico(
    largura: int,
    altura: int,
    tempo_s: float,
) -> np.ndarray:
    """Gera um cenario infantil acolhedor com ceu gradiente, colinas, sol e nuvens em parallax."""
    canvas = np.zeros((altura, largura, 3), dtype=np.uint8)

    # Ceu suave (gradiente vertical de azul suave para creme)
    topo = np.array([245, 230, 210], dtype=np.float32)  # BGR
    base = np.array([255, 252, 245], dtype=np.float32)
    for y in range(altura):
        fator = y / float(altura)
        cor = topo * (1.0 - fator) + base * fator
        canvas[y, :] = cor.astype(np.uint8)

    # Sol sutil
    sol_x = int(largura * 0.85)
    sol_y = int(altura * 0.22)
    cv2.circle(canvas, (sol_x, sol_y), 46, (170, 235, 255), -1, cv2.LINE_AA)
    cv2.circle(canvas, (sol_x, sol_y), 54, (200, 245, 255), 3, cv2.LINE_AA)

    # Nuvens em movimento (drift suave)
    deslocamento = (tempo_s * 15.0) % (largura + 200) - 100
    posicoes_nuvens = [
        (int(deslocamento), int(altura * 0.18), 35),
        (int((deslocamento + 350) % (largura + 200) - 100), int(altura * 0.26), 28),
        (int((deslocamento + 700) % (largura + 200) - 100), int(altura * 0.15), 42),
    ]
    for cx, cy, r in posicoes_nuvens:
        cv2.circle(canvas, (cx, cy), r, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx + int(r * 0.7), cy - 4), int(r * 0.8), (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx - int(r * 0.6), cy + 2), int(r * 0.7), (255, 255, 255), -1, cv2.LINE_AA)

    # Chao / Colina suave no rodape
    rodape_y = int(altura * 0.88)
    curva_chao = []
    for x in range(0, largura + 10, 10):
        ondulacao = math.sin((x / float(largura) * 2.0 * math.pi) + 0.5) * 8.0
        curva_chao.append([x, int(rodape_y + ondulacao)])
    curva_chao.append([largura, altura])
    curva_chao.append([0, altura])
    pts = np.array(curva_chao, dtype=np.int32)
    cv2.fillPoly(canvas, [pts], (210, 225, 205), cv2.LINE_AA)
    cv2.polylines(canvas, [pts[:len(pts)-2]], False, (170, 195, 160), 3, cv2.LINE_AA)

    return canvas


def desenhar_stick_figure_rotoscopia(
    canvas: np.ndarray,
    keypoints: np.ndarray,
    cor_primaria: tuple[int, int, int] = (30, 41, 59),  # slate-800
    cor_destaque: tuple[int, int, int] = (14, 165, 233), # sky-500
    espessura: int = 5,
) -> None:
    """Desenha o boneco de palito articulado nos exatos keypoints anatômicos da pessoa."""
    # Pontos chave (x, y, confianca)
    # 0: nariz, 5: ombro_e, 6: ombro_d, 11: quadril_e, 12: quadril_d
    kps = keypoints

    # 1. Sombra projetada sob os pés
    pes = []
    for idx_pe in (15, 16):
        if kps[idx_pe, 2] > 0.25:
            pes.append((int(kps[idx_pe, 0]), int(kps[idx_pe, 1])))
    if pes:
        pe_centro_x = int(sum(p[0] for p in pes) / len(pes))
        pe_max_y = int(max(p[1] for p in pes))
        cv2.ellipse(
            canvas,
            (pe_centro_x, pe_max_y + 3),
            (32, 8),
            0, 0, 360,
            (160, 180, 160),
            -1,
            cv2.LINE_AA,
        )

    # 2. Conexoes / Ossos do corpo
    for i1, i2 in CONEXOES_CORPO:
        if kps[i1, 2] > 0.20 and kps[i2, 2] > 0.20:
            pt1 = (int(round(kps[i1, 0])), int(round(kps[i1, 1])))
            pt2 = (int(round(kps[i2, 0])), int(round(kps[i2, 1])))
            cv2.line(canvas, pt1, pt2, cor_primaria, espessura, cv2.LINE_AA)

    # 3. Articulações circulares (juntas orgânicas)
    juntas = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    for idx in juntas:
        if kps[idx, 2] > 0.25:
            pt = (int(round(kps[idx, 0])), int(round(kps[idx, 1])))
            cv2.circle(canvas, pt, espessura + 1, cor_destaque, -1, cv2.LINE_AA)
            cv2.circle(canvas, pt, espessura + 1, cor_primaria, 2, cv2.LINE_AA)

    # 4. Cabeça e Feição
    nariz_valido = kps[0, 2] > 0.20
    ombros_validos = (kps[5, 2] > 0.20) and (kps[6, 2] > 0.20)

    if ombros_validos:
        ombro_medio = (kps[5, :2] + kps[6, :2]) / 2.0
        largura_ombros = np.linalg.norm(kps[5, :2] - kps[6, :2])
        raio_cabeca = max(16, int(round(largura_ombros * 0.42)))

        if nariz_valido:
            cabeca_centro = (int(kps[0, 0]), int(kps[0, 1]))
        else:
            cabeca_centro = (int(ombro_medio[0]), int(ombro_medio[1] - raio_cabeca * 1.5))

        # Pescoço conectando ao centro dos ombros
        cv2.line(canvas, cabeca_centro, (int(ombro_medio[0]), int(ombro_medio[1])), cor_primaria, espessura, cv2.LINE_AA)

        # Cabeça redonda com preenchimento limpo
        cv2.circle(canvas, cabeca_centro, raio_cabeca, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, cabeca_centro, raio_cabeca, cor_primaria, espessura, cv2.LINE_AA)

        # Olhos expressivos
        olho_offset_x = int(raio_cabeca * 0.35)
        olho_offset_y = int(raio_cabeca * 0.15)
        olho_raio = max(2, int(raio_cabeca * 0.14))
        cv2.circle(canvas, (cabeca_centro[0] - olho_offset_x, cabeca_centro[1] - olho_offset_y), olho_raio, cor_primaria, -1, cv2.LINE_AA)
        cv2.circle(canvas, (cabeca_centro[0] + olho_offset_x, cabeca_centro[1] - olho_offset_y), olho_raio, cor_primaria, -1, cv2.LINE_AA)

        # Sorriso simpático
        sorriso_y = cabeca_centro[1] + int(raio_cabeca * 0.25)
        cv2.ellipse(
            canvas,
            (cabeca_centro[0], sorriso_y),
            (int(raio_cabeca * 0.45), int(raio_cabeca * 0.30)),
            0, 20, 160,
            cor_destaque,
            max(2, int(espessura * 0.7)),
            cv2.LINE_AA,
        )


def renderizar_rotoscopia_video(
    caminho_video: Path,
    pasta_saida: Path,
    inicio_s: float = 0.0,
    duracao_s: float = 5.0,
    fps: int = 30,
    largura: int = 854,
    altura: int = 480,
) -> int:
    """Renderiza a animacao de bonecos de palito por rotoscopia real do video original."""
    pasta_saida.mkdir(parents=True, exist_ok=True)

    # Carrega o modelo YOLOv8-pose
    modelo = YOLO(str(MODELO_YOLO))

    cap = cv2.VideoCapture(str(caminho_video))
    if not cap.isOpened():
        raise RuntimeError(f"Nao foi possivel abrir video: {caminho_video}")

    fps_orig = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w_orig = cap.get(cv2.CAP_PROP_FRAME_WIDTH) or largura
    h_orig = cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or altura
    quadro_inicio = int(inicio_s * fps_orig)
    cap.set(cv2.CAP_PROP_POS_FRAMES, quadro_inicio)

    total_quadros = max(1, int(round(duracao_s * fps)))
    passo = fps_orig / float(fps)
    pos_float = float(quadro_inicio)

    suavizadores: dict[int, SuavizadorOneEuro] = {}
    cores_bonecos = [
        ((30, 41, 59), (14, 165, 233)),   # azul escuro + ciano
        ((120, 25, 40), (245, 158, 11)),  # vinho + amarelo
        ((20, 80, 50), (16, 185, 129)),   # verde escuro + esmeralda
    ]

    escala_x = float(largura) / float(w_orig)
    escala_y = float(altura) / float(h_orig)

    for i in range(total_quadros):
        t_atual = i / float(fps)
        frame_idx = int(round(pos_float))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if not ok:
            break

        # Roda inferência de pose no frame original
        resultados = modelo(frame, verbose=False)

        # Cria o canvas com o cenário dinâmico
        canvas = desenhar_cenario_ludico(largura, altura, t_atual)

        if resultados and len(resultados) > 0 and resultados[0].keypoints is not None:
            kps_all = resultados[0].keypoints.data.cpu().numpy() # (N, 17, 3)

            # Ordena pessoas por área/proeminência para consistência
            for p_idx in range(min(3, len(kps_all))):
                kps = kps_all[p_idx].copy()

                # Escala pontos para a resolução do canvas
                kps[:, 0] *= escala_x
                kps[:, 1] *= escala_y

                # Suavização com One Euro
                if p_idx not in suavizadores:
                    suavizadores[p_idx] = SuavizadorOneEuro(min_cutoff=1.5, beta=0.01)
                kps[:, :2] = suavizadores[p_idx].filtrar(kps[:, :2], t_atual)

                cor_prim, cor_dest = cores_bonecos[p_idx % len(cores_bonecos)]
                desenhar_stick_figure_rotoscopia(canvas, kps, cor_prim, cor_dest, espessura=5)

        caminho_frame = pasta_saida / f"f_{i:05d}.png"
        cv2.imwrite(str(caminho_frame), canvas)
        pos_float += passo

    cap.release()
    return total_quadros
