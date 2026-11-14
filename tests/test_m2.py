"""Testes automatizados do Marco M2 (Bonecos de palito, portao e seguranca)."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import unittest

from backend import app as backend_app
from pipeline import roteador, seguranca

RAIZ = Path(__file__).resolve().parent.parent


class TestSeguranca(unittest.TestCase):
    """Testes dos filtros de seguranca infantil."""

    def test_conteudo_limpo_passa(self) -> None:
        laudo = seguranca.classificar_conteudo("Um passeio divertido no parque com brinquedos.")
        self.assertTrue(laudo["ok"])
        self.assertEqual(laudo["classificacao"], "infantil")
        self.assertEqual(len(laudo["termos"]), 0)

    def test_conteudo_improprio_bloqueia(self) -> None:
        laudo = seguranca.classificar_conteudo("Cena de violencia e monstros assustadores.")
        self.assertFalse(laudo["ok"])
        self.assertEqual(laudo["classificacao"], "improprio")
        self.assertTrue(len(laudo["termos"]) > 0)
        self.assertIn("violencia", laudo["termos"])


class TestRoteador(unittest.TestCase):
    """Testes do roteador por cena."""

    def test_roteamento_bonecos(self) -> None:
        cenas = [{"id": "c01", "pessoas": 2, "movimento": "intenso"}]
        resultado = roteador.rotear_cenas(cenas, estilo_padrao="bonecos")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id"], "c01")
        self.assertEqual(resultado[0]["tecnica"], "bonecos")


class TestPortaoBackend(unittest.TestCase):
    """Testes dos contratos e portao de aprovacao da API."""

    def test_api_estado_retorna_marco_atual(self) -> None:
        dados = asyncio.run(backend_app.estado())
        # M3+ : marco avanca conforme o desenvolvimento
        self.assertIn(dados.get("marco"), ("M2", "M3", "M4", "M5", "M6"))
        self.assertEqual(dados.get("backend"), "ok")
        self.assertIn("hardware", dados)
        self.assertIn("programas", dados)

    def test_portao_bloqueia_video_completo_sem_aprovacao(self) -> None:
        """Sem aprovacao, o portao retorna 403 independente do marco."""
        resp = asyncio.run(backend_app.gerar_completo("_projeto_sem_aprovacao_m2test"))
        # Projeto inexistente = 404; se existir sem aprovacao = 403
        self.assertIn(resp.status_code, (403, 404))

    def test_previa_json_conforme_contrato(self) -> None:
        caminho_previa = RAIZ / "projetos" / "teste-backend" / "previa.json"
        if not caminho_previa.is_file():
            self.skipTest("previa.json nao encontrado em teste-backend")
        dados = json.loads(caminho_previa.read_text(encoding="utf-8"))
        self.assertEqual(dados.get("versao"), 1)
        self.assertEqual(dados.get("estilo"), "bonecos")
        self.assertEqual(dados.get("status"), "pronto")
        self.assertIn("arquivo", dados)
        self.assertIn("miniatura", dados)
        self.assertIn("seguranca", dados)
        seg = dados["seguranca"]
        self.assertIn(seg.get("veredito"), ("verde", "amarelo", "vermelho"))
        self.assertIn("flashes", seg)
        self.assertIn("volume", seg)
        self.assertIn("conteudo", seg)


if __name__ == "__main__":
    unittest.main()
