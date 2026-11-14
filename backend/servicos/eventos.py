"""Difusor de eventos em memoria para o WebSocket ``/api/eventos``.

O worker da fila roda em thread; as conexoes WebSocket vivem no event loop do
ASGI. Por isso a publicacao usa ``call_soon_threadsafe`` quando o loop
conhecido existe, e a leitura das filas acontece sempre no loop.
"""
from __future__ import annotations

import asyncio
import threading
from datetime import datetime, timezone
from typing import Any


def agora() -> str:
    """Timestamp ISO-8601 em UTC (segundos)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Difusor:
    """Distribui eventos JSON para todos os WebSocket conectados."""

    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._inscritos: list[asyncio.Queue] = []
        self._lock = threading.Lock()

    def vincular_loop(self, loop: asyncio.AbstractEventLoop | None) -> None:
        """Guarda o event loop do ASGI (chamado no startup da aplicacao)."""
        self._loop = loop

    def inscrever(self) -> asyncio.Queue:
        """Cria uma fila para um novo assinante."""
        fila: asyncio.Queue = asyncio.Queue(maxsize=2000)
        with self._lock:
            self._inscritos.append(fila)
        return fila

    def cancelar_inscricao(self, fila: asyncio.Queue) -> None:
        """Remove um assinante (WebSocket desconectou)."""
        with self._lock:
            if fila in self._inscritos:
                self._inscritos.remove(fila)

    def publicar(self, evento: dict[str, Any]) -> None:
        """Publica um evento para todos os assinantes. Seguro entre threads."""
        dados = dict(evento)
        dados.setdefault("ts", agora())
        with self._lock:
            inscritos = list(self._inscritos)
        loop = self._loop
        for fila in inscritos:
            if loop is not None and loop.is_running():
                try:
                    loop.call_soon_threadsafe(self._colocar, fila, dados)
                    continue
                except RuntimeError:
                    pass
            self._colocar(fila, dados)

    @staticmethod
    def _colocar(fila: asyncio.Queue, evento: dict[str, Any]) -> None:
        try:
            fila.put_nowait(evento)
        except asyncio.QueueFull:
            pass
