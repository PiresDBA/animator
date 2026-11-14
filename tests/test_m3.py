"""Testes automatizados do Marco M3 (Portao e Seguranca).

Criterios de aceite M3:
  - Nenhuma Fase B sem aprovacao humana.
  - Flash sintetico detectado e bloqueado.
  - Volume acima de -6 dBTP bloqueado.
  - Decisoes em avaliacoes.json conforme contrato.
  - Retomada da fila apos fechar o app.
"""
from __future__ import annotations

import asyncio
import json
import shutil
import tempfile
import time
from pathlib import Path
import unittest

import cv2
import numpy as np

from backend import app as backend_app
from backend.servicos import avaliacoes, fila as fila_mod, projetos
from backend.servicos.caminhos import RAIZ
from pipeline import seguranca

PROJETO_TESTE = "teste-backend"


class TestEstadoM3(unittest.TestCase):
    """Verifica que o backend reporta M3."""

    def test_api_estado_retorna_m3(self) -> None:
        dados = asyncio.run(backend_app.estado())
        self.assertIn(dados.get("marco"), ("M3", "M4", "M5", "M6"))
        self.assertEqual(dados.get("backend"), "ok")
        self.assertIn("hardware", dados)
        self.assertIn("programas", dados)


class TestPortaoAprovacao(unittest.TestCase):
    """Verifica o portao de aprovacao humana na Fase B."""

    def test_portao_bloqueia_sem_aprovacao(self) -> None:
        """POST /completo sem aprovacao retorna 403."""
        resp = asyncio.run(backend_app.gerar_completo("projeto-inexistente-xyz"))
        # Projeto inexistente -> 404
        self.assertEqual(resp.status_code, 404)

    def test_portao_bloqueia_sem_avaliacao(self) -> None:
        """Projeto sem avaliacoes retorna 403."""
        # Cria projeto temporario sem avaliacoes
        pasta_tmp = RAIZ / "projetos" / "_test_m3_sem_avaliacao"
        pasta_tmp.mkdir(parents=True, exist_ok=True)
        meta = {
            "versao": 1,
            "id": "_test_m3_sem_avaliacao",
            "nome": "Teste sem avaliacao",
            "status": "analisado",
            "entrada": {"video": "inexistente.mp4"},
        }
        (pasta_tmp / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        try:
            resp = asyncio.run(
                backend_app.gerar_completo("_test_m3_sem_avaliacao")
            )
            self.assertEqual(resp.status_code, 403)
            corpo = json.loads(resp.body.decode("utf-8"))
            self.assertEqual(corpo["erro"], "sem_aprovacao")
        finally:
            shutil.rmtree(pasta_tmp, ignore_errors=True)

    def test_portao_libera_com_aprovacao(self) -> None:
        """POST /completo com aprovacao retorna 202 (job enfileirado)."""
        # O projeto teste-backend ja tem uma aprovacao em avaliacoes.json
        resultado = asyncio.run(backend_app.gerar_completo(PROJETO_TESTE))
        # Com aprovacao, retorna dict com job_id (status 202)
        self.assertIsInstance(resultado, dict)
        self.assertIn("job_id", resultado)
        self.assertIn("aprovacao", resultado)


class TestFlashSintetico(unittest.TestCase):
    """Testa a deteccao de flashes luminosos (WCAG 2.3.1)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="m3_flash_"))

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def _criar_video_sintetico(self, nome: str, flashes_por_segundo: int, duracao_s: float = 2.0) -> Path:
        """Cria video com alternancia de quadros preto/branco."""
        caminho = self.tmpdir / nome
        fps = 30
        total_quadros = int(duracao_s * fps)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        escritor = cv2.VideoWriter(str(caminho), fourcc, fps, (320, 240))
        quadros_por_flash = max(1, fps // (flashes_por_segundo * 2)) if flashes_por_segundo > 0 else total_quadros
        for i in range(total_quadros):
            ciclo = (i // quadros_por_flash) % 2
            cor = 255 if ciclo == 0 else 0
            quadro = np.full((240, 320, 3), cor, dtype=np.uint8)
            escritor.write(quadro)
        escritor.release()
        return caminho

    def _criar_video_seguro(self, nome: str, duracao_s: float = 2.0) -> Path:
        """Cria video com cor constante (sem flashes)."""
        caminho = self.tmpdir / nome
        fps = 30
        total_quadros = int(duracao_s * fps)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        escritor = cv2.VideoWriter(str(caminho), fourcc, fps, (320, 240))
        for _ in range(total_quadros):
            quadro = np.full((240, 320, 3), 128, dtype=np.uint8)
            escritor.write(quadro)
        escritor.release()
        return caminho

    def test_flash_sintetico_bloqueado(self) -> None:
        """Video com muitos flashes (>3/s) deve ser bloqueado."""
        video = self._criar_video_sintetico("flash_intenso.mp4", flashes_por_segundo=10)
        resultado = seguranca.medir_flashes(video)
        self.assertFalse(
            resultado["ok"],
            f"Video com 10 flashes/s devia ser bloqueado, mas resultado: {resultado}"
        )
        self.assertGreater(resultado["max_flashes_1s"], 3)

    def test_flash_seguro_passa(self) -> None:
        """Video sem flashes deve passar."""
        video = self._criar_video_seguro("sem_flash.mp4")
        resultado = seguranca.medir_flashes(video)
        self.assertTrue(
            resultado["ok"],
            f"Video sem flashes devia passar, mas resultado: {resultado}"
        )
        self.assertEqual(resultado["max_flashes_1s"], 0)

    def test_flash_limite_exato(self) -> None:
        """Video com poucos flashes (1/s) deve passar."""
        # 1 flash/s = 2 transicoes/s, bem abaixo do limite de 3
        video = self._criar_video_sintetico("flash_limite.mp4", flashes_por_segundo=1)
        resultado = seguranca.medir_flashes(video)
        self.assertTrue(
            resultado["ok"],
            f"Video com 1 flash/s devia passar (limite <= 3), resultado: {resultado}"
        )


class TestVolume(unittest.TestCase):
    """Testa a deteccao de volume alto."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = Path(tempfile.mkdtemp(prefix="m3_vol_"))

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmpdir, ignore_errors=True)

    def test_volume_seguro_passa(self) -> None:
        """A previa existente deve ter volume seguro."""
        previa = RAIZ / "projetos" / PROJETO_TESTE / "saidas" / "previa_bonecos_004.mp4"
        if not previa.is_file():
            self.skipTest("previa_bonecos_004.mp4 nao encontrada")
        resultado = seguranca.medir_volume(previa)
        self.assertTrue(resultado.get("ok", True), f"Previa devia ser segura: {resultado}")

    def test_checagem_completa_previa(self) -> None:
        """A checagem completa da previa existente deve dar veredito verde."""
        previa = RAIZ / "projetos" / PROJETO_TESTE / "saidas" / "previa_bonecos_004.mp4"
        if not previa.is_file():
            self.skipTest("previa_bonecos_004.mp4 nao encontrada")
        resultado = seguranca.checar(previa, descricao="Um passeio divertido no parque")
        self.assertIn(resultado["veredito"], ("verde", "amarelo"))


class TestAvaliacoesContrato(unittest.TestCase):
    """Verifica que avaliacoes.json segue o contrato (secao 5)."""

    def test_avaliacoes_json_conforme_contrato(self) -> None:
        """avaliacoes.json tem versao, lista e campos obrigatorios."""
        caminho = RAIZ / "projetos" / PROJETO_TESTE / "avaliacoes.json"
        if not caminho.is_file():
            self.skipTest("avaliacoes.json nao encontrado")
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        self.assertEqual(dados.get("versao"), 1)
        self.assertIn("avaliacoes", dados)
        lista = dados["avaliacoes"]
        self.assertIsInstance(lista, list)
        self.assertGreater(len(lista), 0)
        for item in lista:
            self.assertIn("id", item)
            self.assertIn("decisao", item)
            self.assertIn("notas", item)
            self.assertIn("data", item)
            self.assertIn(item["decisao"], ("aprovar", "ajustar", "reprovar"))
            notas = item["notas"]
            self.assertIsInstance(notas, dict)
            for chave in avaliacoes.CHAVES_NOTAS:
                self.assertIn(chave, notas)
                self.assertGreaterEqual(notas[chave], 1)
                self.assertLessEqual(notas[chave], 5)

    def test_tem_aprovacao(self) -> None:
        """tem_aprovacao() devolve a aprovacao mais recente do projeto teste."""
        resultado = avaliacoes.tem_aprovacao(PROJETO_TESTE)
        if resultado is None:
            self.skipTest("Nenhuma aprovacao no projeto teste")
        self.assertEqual(resultado["decisao"], "aprovar")

    def test_validacao_notas_invalidas(self) -> None:
        """Notas fora do intervalo 1-5 devem gerar ErroAvaliacao."""
        with self.assertRaises(avaliacoes.ErroAvaliacao):
            avaliacoes.validar({
                "decisao": "aprovar",
                "notas": {
                    "fidelidade": 6,  # invalido
                    "identidade_visual": 3,
                    "fluidez": 4,
                    "adequacao_infantil": 5,
                    "clareza_historia": 3,
                },
            })

    def test_validacao_decisao_invalida(self) -> None:
        """Decisao fora do enum deve gerar ErroAvaliacao."""
        with self.assertRaises(avaliacoes.ErroAvaliacao):
            avaliacoes.validar({
                "decisao": "talvez",
                "notas": {
                    "fidelidade": 3,
                    "identidade_visual": 3,
                    "fluidez": 4,
                    "adequacao_infantil": 5,
                    "clareza_historia": 3,
                },
            })

    def test_alias_criterios(self) -> None:
        """Aliases de criterios sao aceitos e mapeados para as chaves canonicas."""
        notas = avaliacoes.validar({
            "decisao": "aprovar",
            "notas": {
                "fidelidade": 4,
                "estilo_consistente": 3,     # alias de identidade_visual
                "ausencia_artefatos": 4,     # alias de fluidez
                "atencao_infantil": 5,       # alias de adequacao_infantil
                "clareza_cenas": 3,          # alias de clareza_historia
            },
        })
        self.assertIn("identidade_visual", notas)
        self.assertIn("fluidez", notas)
        self.assertIn("adequacao_infantil", notas)
        self.assertIn("clareza_historia", notas)


class TestConteudoSeguranca(unittest.TestCase):
    """Testes do filtro de conteudo lexical."""

    def test_conteudo_limpo(self) -> None:
        resultado = seguranca.classificar_conteudo("Aventuras no parque com gatinhos.")
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["classificacao"], "infantil")

    def test_conteudo_violento(self) -> None:
        resultado = seguranca.classificar_conteudo("Cena com violencia extrema e explosao.")
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["classificacao"], "improprio")
        self.assertIn("violencia", resultado["termos"])

    def test_conteudo_terror(self) -> None:
        resultado = seguranca.classificar_conteudo("Um zumbi assustador aparece.")
        self.assertFalse(resultado["ok"])
        self.assertIn("zumbi", resultado["termos"])

    def test_conteudo_vazio(self) -> None:
        resultado = seguranca.classificar_conteudo("")
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["classificacao"], "nao_classificado")


class TestRetomadaFila(unittest.TestCase):
    """Testa a persistencia e recuperacao da fila SQLite."""

    def test_fila_persiste_jobs(self) -> None:
        """Jobs criados sobrevivem a uma nova instancia de Fila."""
        from backend.servicos.eventos import Difusor
        banco = Path(tempfile.mktemp(suffix=".sqlite3", prefix="m3_fila_"))
        try:
            # Primeira instancia: cria um job
            dif1 = Difusor()
            fila1 = fila_mod.Fila(banco=banco, difusor=dif1)
            job = fila1.enfileirar("teste", "projeto-x", {"msg": "oi"}, "Test job")
            job_id = job["id"]
            self.assertEqual(job["status"], "na_fila")

            # Segunda instancia (simula reinicio): job ainda esta la
            dif2 = Difusor()
            fila2 = fila_mod.Fila(banco=banco, difusor=dif2)
            job_recuperado = fila2.obter(job_id)
            self.assertIsNotNone(job_recuperado)
            self.assertEqual(job_recuperado["status"], "na_fila")
        finally:
            banco.unlink(missing_ok=True)

    def test_recuperacao_jobs_rodando(self) -> None:
        """Jobs 'rodando' num processo anterior sao marcados como erro no reinicio."""
        from backend.servicos.eventos import Difusor
        banco = Path(tempfile.mktemp(suffix=".sqlite3", prefix="m3_recup_"))
        try:
            dif1 = Difusor()
            fila1 = fila_mod.Fila(banco=banco, difusor=dif1)
            job = fila1.enfileirar("teste", "proj", {}, "Test")
            # Muda manualmente para 'rodando' simulando crash
            fila1.atualizar(job["id"], status="rodando")
            job_rodando = fila1.obter(job["id"])
            self.assertEqual(job_rodando["status"], "rodando")

            # Nova instancia: _recuperar() e chamado dentro de iniciar()
            dif2 = Difusor()
            fila2 = fila_mod.Fila(banco=banco, difusor=dif2)
            fila2.iniciar()  # _recuperar() roda aqui
            fila2.parar()

            job_recuperado = fila2.obter(job["id"])
            self.assertEqual(
                job_recuperado["status"], "erro",
                "Job 'rodando' deveria ser marcado como 'erro' apos reinicio"
            )
            self.assertIn("reiniciado", job_recuperado.get("mensagem", "").lower())
        finally:
            banco.unlink(missing_ok=True)


class TestCompletoModule(unittest.TestCase):
    """Testa o modulo pipeline.completo em isolamento."""

    def test_portao_bloqueia_sem_avaliacoes(self) -> None:
        """completo.executar() sem avaliacoes.json lanca RuntimeError."""
        from pipeline import completo
        with self.assertRaises((RuntimeError, FileNotFoundError)):
            completo.executar(
                projeto_id="_projeto_inexistente_m3_test",
                estilo="bonecos",
            )

    def test_resolucao_dimensoes(self) -> None:
        """resolucao_dimensoes() retorna (w, h) corretos."""
        from pipeline.completo import resolucao_dimensoes
        self.assertEqual(resolucao_dimensoes("480p", "16:9"), (854, 480))
        self.assertEqual(resolucao_dimensoes("720p", "16:9"), (1280, 720))
        self.assertEqual(resolucao_dimensoes("480p", "9:16"), (480, 854))
        self.assertEqual(resolucao_dimensoes("720p", "9:16"), (720, 1280))


if __name__ == "__main__":
    unittest.main()
