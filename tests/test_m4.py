"""Testes automatizados do Marco M4 (Estilos procedurais: LEGO, Anime, Cartoon 3D e 3D PBR).

Criterios de aceite M4:
  - Estilos procedurais disponiveis no backend sem erro.
  - Previa de 5s gerada sem difusao para cada tecnica procedural.
  - Verificacoes de tecnica (secao 7 do contrato):
      * LEGO: paleta respeita o limite de cores.
      * Anime: contornos continuos, sem ruido excessivo.
      * Cartoon 3D: rampa de 4 tons, sem artefatos extremos nas bordas.
      * 3D PBR: sombras e oclusao ambiental (AO) presentes.
  - Laudo de seguranca infantil verde/amarelo em todas as saidas.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import unittest

import cv2
import numpy as np

from backend import app as backend_app
from backend.servicos import projetos
from backend.servicos.caminhos import RAIZ
from tecnicas import anime, cartoon, lego, tres_d

PROJETO_TESTE = "teste-backend"


class TestTecnicasProcedurais(unittest.TestCase):
    """Testa individualmente as 4 tecnicas procedurais e suas verificacoes contratuais."""

    @classmethod
    def setUpClass(cls) -> None:
        # Gera quadro sintético RGB/BGR com gradientes e formas geométricas
        h, w = 240, 320
        y, x = np.mgrid[0:h, 0:w]
        b = (x / w * 255).astype(np.uint8)
        g = (y / h * 255).astype(np.uint8)
        r = ((x + y) / (w + h) * 255).astype(np.uint8)
        quadro = np.dstack((b, g, r))
        # Adiciona formas para simular personagem e cenario
        cv2.circle(quadro, (160, 120), 40, (30, 200, 240), -1)
        cv2.rectangle(quadro, (60, 140), (120, 220), (220, 50, 40), -1)
        cls.quadro_teste = quadro

    def test_tecnica_lego_verificacao(self) -> None:
        """Mosaico LEGO: verifica que a paleta respeita o limite de cores."""
        resultado = lego.verificar(self.quadro_teste, limite_cores=16)
        self.assertTrue(resultado["ok"], f"Falha na verificacao LEGO: {resultado}")
        self.assertEqual(resultado["tecnica"], "lego_mosaico")
        self.assertLessEqual(resultado["cores_encontradas"], 32)

    def test_tecnica_anime_verificacao(self) -> None:
        """Traco Anime: contornos XDoG continuos sem cobrir imagem inteira com ruido."""
        resultado = anime.verificar(self.quadro_teste, limite_cores=12)
        self.assertTrue(resultado["ok"], f"Falha na verificacao Anime: {resultado}")
        self.assertEqual(resultado["tecnica"], "anime_contornos")
        self.assertGreater(resultado["proporcao_contornos"], 0.0)
        self.assertLess(resultado["proporcao_contornos"], 0.25)

    def test_tecnica_cartoon_verificacao(self) -> None:
        """Cartoon 3D Toon: rampa de tons e contorno sem artefatos divergentes."""
        resultado = cartoon.verificar(self.quadro_teste)
        self.assertTrue(resultado["ok"], f"Falha na verificacao Cartoon: {resultado}")
        self.assertEqual(resultado["tecnica"], "toon3d")
        self.assertTrue(resultado["sem_artefatos_bordas"])

    def test_tecnica_3d_pbr_verificacao(self) -> None:
        """3D PBR: sombras e oclusao ambiental (AO) presentes no laudo."""
        resultado = tres_d.verificar(self.quadro_teste)
        self.assertTrue(resultado["ok"], f"Falha na verificacao 3D PBR: {resultado}")
        self.assertEqual(resultado["tecnica"], "pbr3d")
        self.assertTrue(resultado["sombras_presentes"])


class TestBackendM4(unittest.TestCase):
    """Verifica contratos da API e disponibilidade dos 5 estilos no Marco M4."""

    def test_api_estado_retorna_m4(self) -> None:
        dados = asyncio.run(backend_app.estado())
        self.assertEqual(dados.get("marco"), "M4")
        self.assertEqual(dados.get("backend"), "ok")

    def test_todos_estilos_m4_disponiveis(self) -> None:
        """No M4, bonecos, lego, anime, cartoon e 3d devem estar disponiveis."""
        meta = projetos.meta(PROJETO_TESTE)
        if meta is None:
            self.skipTest(f"Projeto {PROJETO_TESTE} nao encontrado")
        estilos = {e["id"]: e for e in meta.get("estilos", [])}
        for estilo_id in ("bonecos", "lego", "anime", "cartoon", "3d"):
            self.assertIn(estilo_id, estilos, f"Estilo '{estilo_id}' nao encontrado em meta.json")
            self.assertTrue(
                estilos[estilo_id].get("disponivel"),
                f"Estilo '{estilo_id}' deveria estar disponivel no M4",
            )
            self.assertIsNone(estilos[estilo_id].get("motivo"))


class TestPreviasM4(unittest.TestCase):
    """Valida saidas geradas para os estilos procedurais."""

    def test_previa_lego_existente(self) -> None:
        caminho_previa = RAIZ / "projetos" / PROJETO_TESTE / "previa.json"
        if not caminho_previa.is_file():
            self.skipTest("previa.json nao encontrado")
        dados = json.loads(caminho_previa.read_text(encoding="utf-8"))
        self.assertEqual(dados.get("versao"), 1)
        self.assertEqual(dados.get("status"), "pronto")
        self.assertIn("seguranca", dados)
        self.assertIn(dados["seguranca"]["veredito"], ("verde", "amarelo"))
        self.assertTrue(Path(RAIZ / dados["arquivo"]).is_file())
        self.assertTrue(Path(RAIZ / dados["miniatura"]).is_file())


if __name__ == "__main__":
    unittest.main()
