"""Execucao da CLI do pipeline como subprocesso (contrato M2, secao 3).

Chamadas sempre com ``.venv\\Scripts\\python.exe -m <modulo>`` e ``cwd`` na
raiz do projeto. A saida esperada no stdout e uma linha ``OK: <caminho>``.

Os modulos ``pipeline.analisar`` e ``pipeline.previa`` estao sendo escritos em
paralelo por outro engenheiro; por isso o runner falha de forma explicita
quando o modulo ainda nao existe.
"""
from __future__ import annotations

import os
import queue
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from .caminhos import RAIZ, VENV_PYTHON


@dataclass
class Resultado:
    """Resultado da execucao de um comando do pipeline."""

    ok: bool = False
    codigo: int = 0
    caminho: str | None = None
    erro: str | None = None
    cancelado: bool = False
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)

    def texto_erro(self) -> str:
        if self.erro:
            return self.erro
        if self.stderr:
            return self.stderr[-1]
        if self.stdout:
            return self.stdout[-1]
        return "Falha desconhecida na execucao do pipeline."


def modulo_existe(modulo: str) -> bool:
    """Informa se o modulo do pipeline existe na raiz do projeto."""
    partes = modulo.split(".")
    caminho = RAIZ.joinpath(*partes[:-1], partes[-1] + ".py")
    return caminho.is_file()


def caminho_do_modulo(modulo: str) -> Path:
    partes = modulo.split(".")
    return RAIZ.joinpath(*partes[:-1], partes[-1] + ".py")


def executar(
    modulo: str,
    argumentos: Iterable[str],
    *,
    timeout: float = 7200.0,
    cancelado: Callable[[], bool] | None = None,
    ao_ler: Callable[[str], None] | None = None,
    cwd: Path | None = None,
) -> Resultado:
    """Roda ``python -m <modulo> <argumentos>`` e devolve o resultado.

    O processo e encerrado (kill) quando ``cancelado()`` passa a ser verdadeiro
    ou quando o tempo limite e excedido.
    """
    argumentos = list(argumentos)
    if not VENV_PYTHON.is_file():
        return Resultado(
            ok=False,
            codigo=1,
            erro=(
                "Interpretador do projeto nao encontrado em "
                f"{VENV_PYTHON}. Use o virtualenv .venv do projeto."
            ),
        )
    if not modulo_existe(modulo):
        return Resultado(
            ok=False,
            codigo=1,
            erro=(
                f"O modulo do pipeline '{modulo}' ainda nao existe em "
                f"{caminho_do_modulo(modulo)}. O comando nao pode ser executado."
            ),
        )

    comando = [str(VENV_PYTHON), "-m", modulo, *argumentos]
    ambiente = os.environ.copy()
    ambiente["PYTHONIOENCODING"] = "utf-8"
    ambiente["PYTHONUNBUFFERED"] = "1"
    ambiente.setdefault("PIP_CACHE_DIR", str(RAIZ / ".cache" / "pip"))

    flags = 0
    if os.name == "nt":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        processo = subprocess.Popen(
            comando,
            cwd=str(cwd or RAIZ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=ambiente,
            creationflags=flags,
        )
    except OSError as exc:
        return Resultado(ok=False, codigo=1, erro=f"Falha ao iniciar o comando: {exc}")

    saida_q: queue.Queue = queue.Queue()
    erro_q: queue.Queue = queue.Queue()
    fim_out = threading.Event()
    fim_err = threading.Event()
    threads = []
    for stream, fila, tag, fim in (
        (processo.stdout, saida_q, "out", fim_out),
        (processo.stderr, erro_q, "err", fim_err),
    ):
        thread = threading.Thread(
            target=_ler, args=(stream, fila, tag, fim), daemon=True
        )
        thread.start()
        threads.append(thread)

    linhas_out: list[str] = []
    linhas_err: list[str] = []
    inicio = time.monotonic()

    try:
        while True:
            _drenar(saida_q, linhas_out, ao_ler)
            _drenar(erro_q, linhas_err, ao_ler)
            if cancelado is not None and cancelado():
                _encerrar(processo)
                return Resultado(
                    ok=False,
                    codigo=processo.returncode or -1,
                    erro="Job cancelado pelo usuario.",
                    cancelado=True,
                    stdout=linhas_out,
                    stderr=linhas_err,
                )
            if processo.poll() is not None and fim_out.is_set() and fim_err.is_set():
                break
            if time.monotonic() - inicio > timeout:
                _encerrar(processo)
                return Resultado(
                    ok=False,
                    codigo=processo.returncode or -1,
                    erro=f"Tempo limite de {int(timeout)}s excedido no comando '{modulo}'.",
                    stdout=linhas_out,
                    stderr=linhas_err,
                )
            time.sleep(0.05)
    finally:
        for thread in threads:
            thread.join(timeout=2)

    _drenar(saida_q, linhas_out, ao_ler)
    _drenar(erro_q, linhas_err, ao_ler)

    codigo = processo.returncode if processo.returncode is not None else 1
    caminho = _extrair_ok(linhas_out)
    if codigo != 0:
        detalhe = _detalhe_erro(linhas_out, linhas_err)
        return Resultado(
            ok=False,
            codigo=codigo,
            caminho=caminho,
            erro=(
                f"O comando '{modulo}' terminou com codigo {codigo}. {detalhe}"
            ).strip(),
            stdout=linhas_out,
            stderr=linhas_err,
        )
    return Resultado(
        ok=True,
        codigo=0,
        caminho=caminho,
        stdout=linhas_out,
        stderr=linhas_err,
    )


def _ler(stream, fila: queue.Queue, tag: str, fim: threading.Event) -> None:
    try:
        for linha in stream:
            fila.put((tag, linha.rstrip("\r\n")))
    except (ValueError, OSError):
        pass
    finally:
        fila.put((tag, None))
        fim.set()
        try:
            stream.close()
        except OSError:
            pass


def _drenar(
    fila: queue.Queue, destino: list[str], ao_ler: Callable[[str], None] | None
) -> None:
    while True:
        try:
            tag, linha = fila.get_nowait()
        except queue.Empty:
            return
        if linha is None:
            continue
        destino.append(linha)
        if ao_ler is not None:
            try:
                ao_ler(linha)
            except Exception:  # noqa: BLE001 - log nunca quebra o job
                pass


def _extrair_ok(linhas: Iterable[str]) -> str | None:
    """Le a linha ``OK: <caminho>`` do stdout."""
    for linha in linhas:
        texto = linha.strip()
        if texto.upper().startswith("OK:"):
            return texto[3:].strip() or None
    return None


def _detalhe_erro(stdout: list[str], stderr: list[str]) -> str:
    for linha in stderr + stdout:
        texto = linha.strip()
        if texto.upper().startswith("ERRO:"):
            return texto[5:].strip()
    if stderr:
        return stderr[-1].strip()
    if stdout:
        return stdout[-1].strip()
    return "Sem detalhes na saida do comando."


def _encerrar(processo: subprocess.Popen) -> None:
    try:
        processo.terminate()
    except OSError:
        pass
    try:
        processo.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            processo.kill()
        except OSError:
            pass


# --------------------------------------------------------------------- comandos
def argumentos_analisar(video: Path, saida: Path, previa_dir: Path) -> list[str]:
    """Argumentos de ``pipeline.analisar``."""
    return [
        "--video",
        str(video),
        "--saida",
        str(saida),
        "--previa-dir",
        str(previa_dir),
    ]


def argumentos_previa(
    projeto: str,
    estilo: str,
    trecho_inicio: float | None = None,
    trecho_fim: float | None = None,
    seed: int | None = None,
    resolucao: str = "480p",
) -> list[str]:
    """Argumentos de ``pipeline.previa``."""
    argumentos = ["--projeto", projeto, "--estilo", estilo]
    if trecho_inicio is not None:
        argumentos += ["--trecho-inicio", str(trecho_inicio)]
    if trecho_fim is not None:
        argumentos += ["--trecho-fim", str(trecho_fim)]
    if seed is not None:
        argumentos += ["--seed", str(seed)]
    if resolucao:
        argumentos += ["--resolucao", resolucao]
    return argumentos
