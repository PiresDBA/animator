"""Testes do pipeline de analise do M1."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from pipeline import movimento, validar, video  # noqa: E402

EVIDENCIAS = RAIZ / "docs" / "evidencias" / "m1"


class TestVideo(unittest.TestCase):
    def test_parse_fps_fracao(self) -> None:
        self.assertAlmostEqual(video.parse_fps("30000/1001"), 29.97002997, places=7)

    def test_parse_fps_decimal_e_inteiro(self) -> None:
        self.assertAlmostEqual(video.parse_fps("29.97"), 29.97)
        self.assertAlmostEqual(video.parse_fps("25"), 25.0)

    def test_parse_fps_invalido_usa_padrao(self) -> None:
        self.assertEqual(video.parse_fps(None), 30.0)
        self.assertEqual(video.parse_fps("0/0"), 30.0)
        self.assertEqual(video.parse_fps("invalido"), 30.0)

    def test_tempos_amostra_10s_2fps(self) -> None:
        tempos = video.tempos_amostra(10.0, 2.0)
        self.assertEqual(len(tempos), 20)
        self.assertEqual(tempos[0], 0.0)
        self.assertEqual(tempos[-1], 9.5)
        self.assertTrue(all(t < 10.0 for t in tempos))

    def test_tempos_amostra_curto(self) -> None:
        self.assertEqual(video.tempos_amostra(0.1, 2.0), [])
        self.assertEqual(video.tempos_amostra(1.0, 2.0), [0.0, 0.5])

    def test_tempos_amostra_rejeita_nao_positivo(self) -> None:
        with self.assertRaises(ValueError):
            video.tempos_amostra(0.0, 2.0)
        with self.assertRaises(ValueError):
            video.tempos_amostra(10.0, 0.0)


class TestMovimento(unittest.TestCase):
    def test_resumo_ignora_none(self) -> None:
        resumo = movimento.resumo_movimento(
            [
                {"dif_media": 0.2, "fluxo_medio": 1.0},
                {"dif_media": None, "fluxo_medio": None},
                {"dif_media": 0.4, "fluxo_medio": 3.0},
            ]
        )
        self.assertAlmostEqual(resumo["dif_media_media"], 0.3)
        self.assertAlmostEqual(resumo["dif_media_pico"], 0.4)
        self.assertAlmostEqual(resumo["fluxo_medio_media"], 2.0)
        self.assertAlmostEqual(resumo["fluxo_medio_pico"], 3.0)

    def test_resumo_vazio(self) -> None:
        resumo = movimento.resumo_movimento([])
        self.assertEqual(
            resumo,
            {
                "dif_media_media": 0.0,
                "dif_media_pico": 0.0,
                "fluxo_medio_media": 0.0,
                "fluxo_medio_pico": 0.0,
            },
        )


class TestSchema(unittest.TestCase):
    def test_schema_versionado(self) -> None:
        schema = validar.carregar_schema()
        self.assertEqual(schema["properties"]["versao"]["const"], 1)
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_evidencias_do_golden_validam(self) -> None:
        arquivos = sorted(EVIDENCIAS.glob("clipe_*.json"))
        self.assertEqual(len(arquivos), 3)
        for arquivo in arquivos:
            with self.subTest(arquivo=arquivo.name):
                dados = json.loads(arquivo.read_text(encoding="utf-8"))
                validar.validar(dados)

    def test_json_invalido_e_rejeitado(self) -> None:
        dados = json.loads(
            (EVIDENCIAS / "clipe_01_estatico.json").read_text(encoding="utf-8")
        )
        dados["versao"] = 2
        with self.assertRaises(ValueError) as contexto:
            validar.validar(dados)
        self.assertIn("versao", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
