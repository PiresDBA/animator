"""Testes da descoberta: assinaturas, exclusoes e varredura somente leitura."""
from __future__ import annotations

import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "descoberta"))

import varredura  # noqa: E402


class BaseTemp(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(dir=RAIZ / "tests")
        self.base = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def tipos(self, pasta: Path) -> list[str]:
        return [tipo for tipo, _ in varredura.identificar(pasta)]


class TestAssinaturas(BaseTemp):
    def test_comfyui_com_acentos_e_espacos(self) -> None:
        pasta = self.base / "Comfy UI ação"
        (pasta / "models").mkdir(parents=True)
        (pasta / "main.py").write_text("# comfy\n", encoding="utf-8")
        self.assertIn("comfyui", self.tipos(pasta))

    def test_remotion(self) -> None:
        pasta = self.base / "projeto remotion"
        (pasta / "src").mkdir(parents=True)
        (pasta / "src" / "Root.tsx").write_text("export {};\n", encoding="utf-8")
        (pasta / "package.json").write_text(
            json.dumps({"dependencies": {"remotion": "4.0.0"}}), encoding="utf-8"
        )
        self.assertIn("remotion", self.tipos(pasta))

    def test_motor_three_mais_remotion(self) -> None:
        pasta = self.base / "motor"
        pasta.mkdir()
        (pasta / "package.json").write_text(
            json.dumps({"dependencies": {"three": "0.170.0", "remotion": "4.0.0"}}),
            encoding="utf-8",
        )
        self.assertIn("motor_bonecos", self.tipos(pasta))

    def test_motor_stick_film_local(self) -> None:
        pasta = self.base / "stick-film"
        (pasta / "engine").mkdir(parents=True)
        (pasta / "engine" / "render.mjs").write_text("// render\n", encoding="utf-8")
        (pasta / "engine" / "character.js").write_text("// character\n", encoding="utf-8")
        self.assertIn("motor_bonecos", self.tipos(pasta))

    def test_ffmpeg(self) -> None:
        pasta = self.base / "ffmpeg bin"
        pasta.mkdir()
        (pasta / "ffmpeg.exe").write_bytes(b"stub")
        (pasta / "ffprobe.exe").write_bytes(b"stub")
        self.assertIn("ffmpeg", self.tipos(pasta))

    def test_effectcraft(self) -> None:
        pasta = self.base / "EffectCraft"
        pasta.mkdir()
        (pasta / "effectcraft.exe").write_bytes(b"stub")
        self.assertIn("effectcraft", self.tipos(pasta))

    def test_videofactoryai_por_nome(self) -> None:
        pasta = self.base / "VideoFactoryAI"
        pasta.mkdir()
        self.assertIn("videofactoryai", self.tipos(pasta))


class TestVarredura(BaseTemp):
    def _snapshot(self) -> list[tuple[str, int, int]]:
        itens = []
        for p in sorted(self.base.rglob("*")):
            try:
                st = p.stat()
                itens.append((str(p.relative_to(self.base)), st.st_size, st.st_mtime_ns))
            except OSError:
                continue
        return itens

    def test_nao_altera_arquivos(self) -> None:
        pasta = self.base / "Comfy UI acentuada"
        (pasta / "models").mkdir(parents=True)
        (pasta / "main.py").write_text("# comfy\n", encoding="utf-8")
        (pasta / "package.json").write_text(
            json.dumps({"dependencies": {"remotion": "4.0.0"}}), encoding="utf-8"
        )
        antes = self._snapshot()
        encontrados, stats = varredura.varrer_raizes([(self.base, 4)], max_seconds=5.0)
        depois = self._snapshot()
        self.assertEqual(antes, depois)
        self.assertGreaterEqual(stats["pastas"], 2)
        self.assertTrue(any(item["tipo"] == "comfyui" for item in encontrados))

    def test_respeita_prazo(self) -> None:
        for indice in range(20):
            pasta = self.base / f"pasta_{indice}"
            pasta.mkdir()
            (pasta / "arquivo.txt").write_text("x", encoding="utf-8")
        inicio = time.monotonic()
        varredura.varrer_raizes([(self.base, 20)], max_seconds=0.05)
        self.assertLess(time.monotonic() - inicio, 2.0)

    def test_lista_de_exclusoes(self) -> None:
        self.assertIn("node_modules", varredura.EXCLUIR_DIRS)
        self.assertIn("windows", varredura.EXCLUIR_DIRS)
        self.assertIn("system volume information", varredura.EXCLUIR_DIRS)
        self.assertIn("$recycle.bin", varredura.EXCLUIR_DIRS)


if __name__ == "__main__":
    unittest.main()
