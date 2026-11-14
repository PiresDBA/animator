"""Backend do Estucio de Animacao (M2).

FastAPI na porta 8765. Implementa a secao 5 do contrato M2:
``/api/estado``, ``/api/projetos`` (CRUD + analisar + previa + previas),
``/api/avaliacoes``, ``/api/projetos/{id}/completo`` (bloqueado no M2),
``/api/fila`` (com cancelamento) e o WebSocket ``/api/eventos``.

Para subir:
    .venv\\Scripts\\python.exe -m uvicorn app:app --app-dir backend --host 127.0.0.1 --port 8765
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from servicos import avaliacoes, fila as fila_mod, hardware, previa, projetos
    from servicos.caminhos import FRONTEND_DIST, RAIZ
    from servicos.eventos import Difusor, agora
except ImportError:
    from backend.servicos import avaliacoes, fila as fila_mod, hardware, previa, projetos
    from backend.servicos.caminhos import FRONTEND_DIST, RAIZ
    from backend.servicos.eventos import Difusor, agora

difusor = Difusor()
fila = fila_mod.Fila(difusor=difusor)


# --------------------------------------------------------------------- erros
def erro_resposta(codigo_http: int, codigo: str, mensagem: str) -> JSONResponse:
    """Resposta de erro no formato do contrato: {"erro", "mensagem"}."""
    return JSONResponse(
        status_code=codigo_http, content={"erro": codigo, "mensagem": mensagem}
    )



# ------------------------------------------------------------------- modelos
class PedidoProjeto(BaseModel):
    nome: str = Field(min_length=1, max_length=140)
    video: str = Field(min_length=1)


class PedidoPrevia(BaseModel):
    estilo: str = "bonecos"
    trecho_inicio: float = 0.0
    trecho_fim: float = 5.0
    seed: int | None = None
    resolucao: str = "480p"


class PedidoAvaliacao(BaseModel):
    projeto: str | None = None
    previa_id: str | None = None
    estilo: str | None = None
    decisao: str
    notas: dict[str, Any]
    comentario: str | None = None
    params: dict[str, Any] | None = None
    observacao_responsavel: str | None = None


# --------------------------------------------------------------- handlers
def _job_analisar(job: dict, ctx: fila_mod.Contexto, payload: dict) -> None:
    projeto_id = job["projeto"] or ""
    base = projetos.projeto_dir(projeto_id)
    video = payload.get("video") or ""
    caminho_video = Path(video)
    if not caminho_video.is_file():
        raise RuntimeError(f"Video de entrada nao encontrado: {video}")

    saida = base / "analise.json"
    previa_dir = base / "saidas" / "frames"
    ctx.progresso(0.05, "Iniciando a analise do video.")
    ctx.log("info", f"Analisando '{caminho_video.name}' (projeto {projeto_id}).")

    resultado = previa.executar(
        "pipeline.analisar",
        previa.argumentos_analisar(caminho_video, saida, previa_dir),
        cancelado=ctx.cancelado,
        ao_ler=lambda linha: ctx.log("info", linha),
    )
    if resultado.cancelado:
        raise fila_mod.Cancelado()
    if not resultado.ok:
        ctx.log("erro", resultado.texto_erro())
        raise RuntimeError(resultado.texto_erro())

    ctx.progresso(0.85, "Analise concluida; derivando cenas e movimento.")
    analise = projetos.ler_json(saida)
    if isinstance(analise, dict):
        projetos.derivar_analise(projeto_id, analise)
        info = analise.get("video") or {}
        projetos.atualizar_entrada(projeto_id, info.get("duracao_s"))
        meta = projetos.meta(projeto_id) or {}
        meta["status"] = "analisado"
        meta["analise"] = {
            "arquivo": f"projetos/{projeto_id}/analise.json",
            "status": analise.get("status"),
            "gerado_em": analise.get("gerado_em"),
        }
        projetos.salvar_meta(projeto_id, meta)
    ctx.progresso(0.95, "Concluido.")
    ctx.mensagem = "Analise concluida."


def _job_previa(job: dict, ctx: fila_mod.Contexto, payload: dict) -> None:
    projeto_id = job["projeto"] or ""
    estilo = payload.get("estilo") or "bonecos"
    argumentos = previa.argumentos_previa(
        projeto_id,
        estilo,
        payload.get("trecho_inicio"),
        payload.get("trecho_fim"),
        payload.get("seed"),
        payload.get("resolucao") or "480p",
    )
    ctx.progresso(0.05, "Iniciando a geracao da previa.")
    ctx.log("info", f"Gerando previa '{estilo}' do projeto {projeto_id}.")

    resultado = previa.executar(
        "pipeline.previa",
        argumentos,
        cancelado=ctx.cancelado,
        ao_ler=lambda linha: ctx.log("info", linha),
    )
    if resultado.cancelado:
        raise fila_mod.Cancelado()
    if not resultado.ok:
        ctx.log("erro", resultado.texto_erro())
        raise RuntimeError(resultado.texto_erro())

    ctx.progresso(0.9, "Previa gerada.")
    projetos.registrar_tentativa(projeto_id, estilo)
    documento = projetos.previa(projeto_id)
    difusor.publicar(
        {"tipo": "previa", "projeto": projeto_id, "previa": documento}
    )
    ctx.progresso(0.95, "Concluido.")
    ctx.mensagem = "Previa gerada."


fila.registrar_handler("analisar", _job_analisar)
fila.registrar_handler("previa", _job_previa)


# ------------------------------------------------------------------- ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    difusor.vincular_loop(asyncio.get_running_loop())
    fila.iniciar()
    try:
        yield
    finally:
        fila.parar()


app = FastAPI(
    title="Estudio de Animacao - M2",
    version="1.0.0",
    description="Backend local do M2 (bonecos de palito).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def erro_de_validacao(request, exc: RequestValidationError) -> JSONResponse:
    """Erros de validacao do pydantic no formato do contrato."""
    detalhe = "; ".join(
        f"{erro.get('loc', ['corpo'])[-1]}: {erro.get('msg', 'valor invalido')}"
        for erro in exc.errors()
    )
    return erro_resposta(
        422, "dados_invalidos", f"Dados de entrada invalidos. {detalhe}".strip()
    )


# --------------------------------------------------------------------- estado
@app.get("/api/estado")
async def estado() -> dict[str, Any]:
    """Estado geral do backend (contrato M2, secao 5)."""
    return {
        "marco": "M2",
        "backend": "ok",
        "fila": fila.resumo(),
        "hardware": hardware.resumo(),
        "programas": hardware.programas(),
        "ts": agora(),
    }


# ------------------------------------------------------------------ projetos
@app.get("/api/projetos")
async def listar_projetos() -> list[dict[str, Any]]:
    """Lista os meta.json de todos os projetos."""
    return projetos.listar()


@app.post("/api/projetos", status_code=201)
async def criar_projeto(pedido: PedidoProjeto):
    """Cria um projeto novo (pastas + meta.json)."""
    try:
        return projetos.criar(pedido.nome, pedido.video)
    except projetos.ErroProjeto as exc:
        return erro_resposta(400, "projeto_invalido", str(exc))


@app.get("/api/projetos/{projeto_id}")
async def obter_projeto(projeto_id: str):
    """Detalhe do projeto: meta, cenas, previa, avaliacoes e mapa de tecnicas."""
    meta = projetos.meta(projeto_id)
    if meta is None:
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    return {
        "meta": meta,
        "cenas": projetos.cenas(projeto_id),
        "previa": projetos.previa(projeto_id),
        "avaliacoes": avaliacoes.ler(projeto_id),
        "mapa_tecnicas": projetos.mapa_tecnicas(projeto_id),
    }


@app.get("/api/projetos/{projeto_id}/avaliacoes")
async def listar_avaliacoes(projeto_id: str):
    """Avaliacoes humanas de um projeto."""
    if not projetos.existe(projeto_id):
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    return {"avaliacoes": avaliacoes.ler(projeto_id)}


@app.post("/api/projetos/{projeto_id}/analisar", status_code=202)
async def enfileirar_analise(projeto_id: str):
    """Enfileira a analise do video de entrada (pipeline.analisar)."""
    meta = projetos.meta(projeto_id)
    if meta is None:
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    video = (meta.get("entrada") or {}).get("video")
    if not video or not Path(str(video)).is_file():
        return erro_resposta(
            400,
            "video_inexistente",
            f"O video de entrada do projeto nao foi encontrado: {video}",
        )
    job = fila.enfileirar(
        "analisar",
        projeto_id,
        {"video": str(video)},
        "Analise do video na fila.",
    )
    return {"job_id": job["id"]}


@app.post("/api/projetos/{projeto_id}/previa", status_code=202)
async def enfileirar_previa(projeto_id: str, pedido: PedidoPrevia):
    """Enfileira a geracao de uma previa (pipeline.previa)."""
    meta = projetos.meta(projeto_id)
    if meta is None:
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    estilos = {str(item.get("id")): item for item in (meta.get("estilos") or [])}
    estilo = (pedido.estilo or "bonecos").strip().lower()
    if estilo not in estilos:
        return erro_resposta(
            400,
            "estilo_desconhecido",
            f"Estilo '{pedido.estilo}' nao existe. Disponiveis: "
            + ", ".join(sorted(estilos))
            + ".",
        )
    if not estilos[estilo].get("disponivel"):
        motivo = estilos[estilo].get("motivo") or "estilo indisponivel no M2"
        return erro_resposta(
            400, "estilo_indisponivel", f"O estilo '{estilo}' esta indisponivel: {motivo}."
        )
    if pedido.trecho_fim <= pedido.trecho_inicio:
        return erro_resposta(
            400,
            "trecho_invalido",
            "O trecho final deve ser maior que o trecho inicial.",
        )
    if pedido.resolucao not in ("480p", "720p"):
        return erro_resposta(
            400,
            "resolucao_invalida",
            "Resolucao invalida. Valores aceitos: 480p, 720p.",
        )
    job = fila.enfileirar(
        "previa",
        projeto_id,
        {
            "estilo": estilo,
            "trecho_inicio": pedido.trecho_inicio,
            "trecho_fim": pedido.trecho_fim,
            "seed": pedido.seed,
            "resolucao": pedido.resolucao,
        },
        f"Previa '{estilo}' na fila.",
    )
    return {"job_id": job["id"]}


@app.get("/api/projetos/{projeto_id}/previas")
async def listar_previas(projeto_id: str):
    """Lista as previas geradas de um projeto."""
    if not projetos.existe(projeto_id):
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    return {"previas": projetos.listar_previas(projeto_id)}


# --------------------------------------------------------------- avaliacoes
@app.post("/api/avaliacoes", status_code=201)
async def registrar_avaliacao(pedido: PedidoAvaliacao):
    """Grava uma avaliacao humana (contrato M2, secao 4.2)."""
    projeto_id = (pedido.projeto or "").strip()
    if not projeto_id:
        return erro_resposta(
            400,
            "projeto_obrigatorio",
            "Informe o campo 'projeto' com o id do projeto avaliado.",
        )
    try:
        registro = avaliacoes.salvar(
            projeto_id,
            {
                "previa_id": pedido.previa_id,
                "estilo": pedido.estilo,
                "decisao": pedido.decisao,
                "notas": pedido.notas,
                "comentario": pedido.comentario,
                "params": pedido.params,
                "observacao_responsavel": pedido.observacao_responsavel,
            },
        )
    except avaliacoes.ErroAvaliacao as exc:
        return erro_resposta(400, "avaliacao_invalida", str(exc))
    return registro


@app.post("/api/projetos/{projeto_id}/avaliacoes", status_code=201)
async def registrar_avaliacao_no_projeto(projeto_id: str, pedido: PedidoAvaliacao):
    """Atalho de ``POST /api/avaliacoes`` com o projeto na URL."""
    pedido.projeto = projeto_id
    return await registrar_avaliacao(pedido)


# ------------------------------------------------------------------ completo
@app.post("/api/projetos/{projeto_id}/completo")
async def gerar_completo(projeto_id: str):
    """Portao do M2: nao ha geracao de video completo neste marco."""
    meta = projetos.meta(projeto_id)
    if meta is None:
        return erro_resposta(
            404, "projeto_inexistente", f"Projeto nao encontrado: {projeto_id}"
        )
    aprovacao = avaliacoes.tem_aprovacao(projeto_id)
    if aprovacao is None:
        return erro_resposta(
            403,
            "sem_aprovacao",
            "Nenhum estilo aprovado neste projeto. Avalie uma previa e aprove "
            "o estilo para liberar a geracao do video completo.",
        )
    return erro_resposta(
        403,
        "video_completo_bloqueado_no_m2",
        "O projeto tem uma previa aprovada ("
        f"{aprovacao.get('id')}), mas o M2 nao produz video completo: a "
        "geracao completa fica disponivel apenas a partir de um marco "
        "posterior. Ate la, use as previas para revisar o resultado.",
    )


# ---------------------------------------------------------------------- fila
@app.get("/api/fila")
async def listar_fila() -> list[dict[str, Any]]:
    """Lista os jobs da fila."""
    return fila.listar()


@app.post("/api/fila/{job_id}/cancelar")
async def cancelar_job(job_id: str):
    """Cancela um job (na fila ou em execucao)."""
    job, motivo = fila.cancelar(job_id)
    if job is None:
        return erro_resposta(404, "job_inexistente", motivo or "Job nao encontrado.")
    if motivo:
        return erro_resposta(409, "job_nao_cancelavel", motivo)
    return job


# ------------------------------------------------------------------- eventos
@app.websocket("/api/eventos")
async def eventos(websocket: WebSocket) -> None:
    """WebSocket com eventos de log, job e previa."""
    await websocket.accept()
    inscricao = difusor.inscrever()
    try:
        await websocket.send_json(
            {
                "tipo": "log",
                "nivel": "info",
                "mensagem": "Conectado ao fluxo de eventos do estudio.",
                "ts": agora(),
            }
        )
        while True:
            try:
                evento = await asyncio.wait_for(inscricao.get(), timeout=15.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"tipo": "ping", "ts": agora()})
                continue
            await websocket.send_json(evento)
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001 - cliente caiu no meio do envio
        pass
    finally:
        difusor.cancelar_inscricao(inscricao)


# --------------------------------------------------------------------- estaticos
class StaticRaiz(StaticFiles):
    """Estatico da raiz do projeto, bloqueando pastas sensiveis."""

    BLOQUEADOS = {".venv", ".git", ".cache", "node_modules", "__pycache__", "backend"}

    def lookup_path(self, path: str):
        partes = [parte for parte in Path(path).parts if parte not in (".", "/")]
        if any(parte in self.BLOQUEADOS for parte in partes):
            return "", None
        if any(parte.startswith(".") for parte in partes):
            return "", None
        return super().lookup_path(path)


app.mount("/media", StaticRaiz(directory=str(RAIZ)), name="media")

if FRONTEND_DIST.is_dir():
    app.mount(
        "/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend"
    )


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
