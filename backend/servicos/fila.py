"""Fila de jobs do M2 (SQLite em ``backend/fila.sqlite3``).

Regras do contrato:
- Estados: ``na_fila``, ``rodando``, ``pronto``, ``erro``, ``cancelado``.
- Um unico job roda por vez (worker em thread).
- Cada mudanca de estado publica um evento ``{"tipo": "job", ...}``.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from .caminhos import BANCO_FILA
from .eventos import Difusor, agora

ESTADOS = ("na_fila", "rodando", "pronto", "erro", "cancelado")

CAMPOS = (
    "id",
    "tipo",
    "projeto",
    "status",
    "progresso",
    "mensagem",
    "criado_em",
    "finished_em",
)


class Cancelado(Exception):
    """Sinaliza que o job foi cancelado pelo usuario."""


class Contexto:
    """Passado ao handler do job para reportar progresso, logs e cancelamento."""

    def __init__(self, fila: "Fila", job_id: str) -> None:
        self.fila = fila
        self.job_id = job_id
        self.mensagem = ""

    def progresso(self, valor: float, mensagem: str | None = None) -> None:
        """Atualiza o progresso (0..1) e a mensagem do job."""
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            numero = 0.0
        numero = max(0.0, min(1.0, numero))
        campos: dict[str, Any] = {"progresso": numero}
        if mensagem:
            campos["mensagem"] = mensagem
            self.mensagem = mensagem
        self.fila.atualizar(self.job_id, **campos)

    progress = progresso

    def log(self, nivel: str, mensagem: str) -> None:
        """Publica uma linha de log (nivel: info | aviso | erro)."""
        self.fila.difusor.publicar(
            {
                "tipo": "log",
                "nivel": nivel,
                "mensagem": mensagem,
                "job_id": self.job_id,
            }
        )

    def cancelado(self) -> bool:
        """Informa se o usuario pediu o cancelamento do job em execucao."""
        return self.fila.solicitar_cancelamento_ativo()


class Fila:
    """Fila persistente de jobs com worker unico."""

    def __init__(self, banco: Path = BANCO_FILA, difusor: Difusor | None = None) -> None:
        self.banco = Path(banco)
        self.difusor = difusor or Difusor()
        self._handlers: dict[str, Callable[[dict, Contexto, dict], None]] = {}
        self._thread: threading.Thread | None = None
        self._parar = threading.Event()
        self._cancel = threading.Event()
        self._lock = threading.RLock()
        self.banco.parent.mkdir(parents=True, exist_ok=True)
        self._criar_tabela()

    # ------------------------------------------------------------------ banco
    def _conexao(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.banco, timeout=20)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA busy_timeout=20000")
        return con

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        con = self._conexao()
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def _criar_tabela(self) -> None:
        with self._tx() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id           TEXT PRIMARY KEY,
                    tipo         TEXT NOT NULL,
                    projeto      TEXT,
                    status       TEXT NOT NULL,
                    progresso    REAL NOT NULL DEFAULT 0.0,
                    mensagem     TEXT,
                    criado_em    TEXT NOT NULL,
                    finished_em  TEXT,
                    payload      TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            con.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")

    # ------------------------------------------------------------------ jobs
    @staticmethod
    def _linha(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        return {campo: row[campo] for campo in CAMPOS}

    def obter(self, job_id: str) -> dict[str, Any] | None:
        with self._tx() as con:
            row = con.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return self._linha(row)

    def listar(self) -> list[dict[str, Any]]:
        with self._tx() as con:
            rows = con.execute(
                "SELECT * FROM jobs ORDER BY criado_em DESC, rowid DESC"
            ).fetchall()
        return [self._linha(row) for row in rows if row is not None]

    def enfileirar(
        self,
        tipo: str,
        projeto: str | None = None,
        payload: dict | None = None,
        mensagem: str | None = None,
    ) -> dict[str, Any]:
        """Cria um job na fila e devolve o registro criado."""
        job_id = "job_" + uuid.uuid4().hex[:8]
        with self._tx() as con:
            con.execute(
                """
                INSERT INTO jobs
                    (id, tipo, projeto, status, progresso, mensagem, criado_em, payload)
                VALUES (?, ?, ?, 'na_fila', 0.0, ?, ?, ?)
                """,
                (
                    job_id,
                    tipo,
                    projeto,
                    mensagem or "Na fila.",
                    agora(),
                    json.dumps(payload or {}, ensure_ascii=False),
                ),
            )
        job = self.obter(job_id)
        assert job is not None
        self._publicar_job(job)
        return job

    def atualizar(self, job_id: str, **campos: Any) -> dict[str, Any] | None:
        """Atualiza colunas do job e publica o novo estado."""
        if not campos:
            return self.obter(job_id)
        colunas = ", ".join(f"{nome} = ?" for nome in campos)
        valores = list(campos.values())
        with self._tx() as con:
            cur = con.execute(
                f"UPDATE jobs SET {colunas} WHERE id = ?", (*valores, job_id)
            )
            if cur.rowcount == 0:
                return None
        job = self.obter(job_id)
        if job is not None:
            self._publicar_job(job)
        return job

    def resumo(self) -> dict[str, Any]:
        """Contagem por estado (usado em ``GET /api/estado``)."""
        contagem = {estado: 0 for estado in ESTADOS}
        with self._tx() as con:
            for linha in con.execute(
                "SELECT status, COUNT(*) AS total FROM jobs GROUP BY status"
            ):
                contagem[linha["status"]] = int(linha["total"])
        contagem["total"] = sum(contagem.values())
        return contagem

    def cancelar(self, job_id: str) -> tuple[dict[str, Any] | None, str | None]:
        """Cancela um job. Devolve ``(job, motivo_falha)``."""
        job = self.obter(job_id)
        if job is None:
            return None, "Job nao encontrado."
        status = job["status"]
        if status in ("pronto", "erro", "cancelado"):
            return job, f"O job ja terminou com status '{status}' e nao pode ser cancelado."
        if status == "rodando":
            self._cancel.set()
            job = self.atualizar(job_id, mensagem="Cancelamento solicitado.")
            return job, None
        job = self.atualizar(
            job_id,
            status="cancelado",
            mensagem="Cancelado antes de iniciar.",
            finished_em=agora(),
        )
        return job, None

    # --------------------------------------------------------------- worker
    def registrar_handler(
        self, tipo: str, handler: Callable[[dict, Contexto, dict], None]
    ) -> None:
        """Registra a funcao que executa um tipo de job."""
        self._handlers[tipo] = handler

    def iniciar(self) -> None:
        """Sobe a thread do worker (idempotente)."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._recuperar()
            self._parar.clear()
            self._thread = threading.Thread(
                target=self._loop, name="worker-fila", daemon=True
            )
            self._thread.start()

    def _recuperar(self) -> None:
        """Jobs que ficaram 'rodando' num processo anterior sao marcados como erro."""
        with self._tx() as con:
            con.execute(
                """
                UPDATE jobs
                   SET status = 'erro',
                       mensagem = 'Job interrompido: o backend foi reiniciado.',
                       finished_em = ?
                 WHERE status = 'rodando'
                """,
                (agora(),),
            )

    def parar(self) -> None:
        """Para o worker (usado no shutdown)."""
        self._parar.set()
        self._cancel.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=5)

    def solicitar_cancelamento_ativo(self) -> bool:
        """Verifica se o job em execucao foi marcado para cancelamento."""
        return self._cancel.is_set()

    def _publicar_job(self, job: dict[str, Any] | None) -> None:
        if job is None:
            return
        self.difusor.publicar({"tipo": "job", "job": job})

    def _loop(self) -> None:
        while not self._parar.is_set():
            try:
                job = self._proxima()
            except Exception as exc:  # noqa: BLE001 - o worker nunca pode morrer
                self.difusor.publicar(
                    {
                        "tipo": "log",
                        "nivel": "erro",
                        "mensagem": f"Falha interna da fila ao buscar o proximo job: {exc}",
                    }
                )
                self._parar.wait(1.0)
                continue
            if job is None:
                self._parar.wait(0.25)
                continue
            self._executar(job)

    def _proxima(self) -> dict[str, Any] | None:
        with self._tx() as con:
            row = con.execute(
                "SELECT * FROM jobs WHERE status = 'na_fila' ORDER BY criado_em ASC, rowid ASC LIMIT 1"
            ).fetchone()
            if row is None:
                return None
            con.execute(
                "UPDATE jobs SET status = 'rodando', mensagem = ? WHERE id = ?",
                ("Iniciado.", row["id"]),
            )
        job = self.obter(row["id"])
        if job is not None:
            self._publicar_job(job)
        execucao = dict(row)
        execucao["status"] = "rodando"
        return execucao

    def _executar(self, job: dict[str, Any]) -> None:
        self._cancel.clear()
        ctx = Contexto(self, job["id"])
        handler = self._handlers.get(job["tipo"])
        try:
            if handler is None:
                raise RuntimeError(
                    f"Nenhum handler registrado para o tipo de job '{job['tipo']}'."
                )
            payload = json.loads(job["payload"] or "{}")
            handler(job, ctx, payload)
        except Cancelado:
            ctx.log("aviso", "Job cancelado.")
            self.atualizar(
                job["id"],
                status="cancelado",
                mensagem="Cancelado.",
                finished_em=agora(),
            )
        except Exception as exc:  # noqa: BLE001 - erro vira estado do job
            ctx.log("erro", f"Falha no job: {exc}")
            self.atualizar(
                job["id"],
                status="erro",
                mensagem=str(exc),
                finished_em=agora(),
            )
        else:
            if ctx.cancelado():
                self.atualizar(
                    job["id"],
                    status="cancelado",
                    mensagem="Cancelado.",
                    finished_em=agora(),
                )
            else:
                self.atualizar(
                    job["id"],
                    status="pronto",
                    progresso=1.0,
                    mensagem=ctx.mensagem or "Concluido.",
                    finished_em=agora(),
                )
