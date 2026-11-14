"""CRUD dos projetos em ``projetos/<id>/`` (contrato M2, secao 2 e 4.3)."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .caminhos import (
    CONFIG_JSON,
    FFPROBE,
    PROJETOS_DIR,
    RAIZ,
    projeto_dir,
)

ESTILOS_M2 = {
    "bonecos": {"rotulo": "Bonecos de palito", "disponivel": True, "motivo": None},
    "lego": {
        "rotulo": "Mosaico de blocos",
        "disponivel": False,
        "motivo": "disponivel a partir do M4",
    },
    "anime": {
        "rotulo": "Anime",
        "disponivel": False,
        "motivo": "disponivel a partir do M4",
    },
    "cartoon": {
        "rotulo": "Cartoon",
        "disponivel": False,
        "motivo": "disponivel a partir do M4",
    },
    "3d": {
        "rotulo": "3D",
        "disponivel": False,
        "motivo": "disponivel a partir do M4",
    },
}


class ErroProjeto(Exception):
    """Erro de negocio ligado a um projeto."""


def agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ler_json(caminho: Path) -> Any:
    """Le um JSON; devolve ``None`` se nao existir ou estiver invalido."""
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return None


def gravar_json(caminho: Path, dados: Any) -> None:
    """Grava JSON de forma atomica (arquivo temporario + replace)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    temporario = caminho.with_name(caminho.name + ".tmp")
    temporario.write_text(texto, encoding="utf-8")
    temporario.replace(caminho)


def slug(texto: str) -> str:
    """Normaliza um nome para uso como id de pasta."""
    normalizado = unicodedata.normalize("NFKD", texto)
    ascii_texto = normalizado.encode("ascii", "ignore").decode("ascii")
    limpo = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_texto).strip("-").lower()
    return limpo or "projeto"


def _sha256(caminho: Path) -> str | None:
    digest = hashlib.sha256()
    try:
        with caminho.open("rb") as arquivo:
            for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
                digest.update(bloco)
    except OSError:
        return None
    return digest.hexdigest()


def _duracao(caminho: Path) -> float:
    """Duracao do video em segundos (ffprobe local do projeto)."""
    if not FFPROBE.is_file():
        return 0.0
    try:
        processo = subprocess.run(
            [
                str(FFPROBE),
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(caminho),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        dados = json.loads(processo.stdout or "{}")
        return round(float(dados["format"]["duration"]), 3)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return 0.0


def _config() -> dict:
    dados = ler_json(CONFIG_JSON)
    return dados if isinstance(dados, dict) else {}


def _limite_tentativas() -> int:
    padroes = _config().get("padroes") or {}
    try:
        return int(padroes.get("tentativas_por_estilo", 3))
    except (TypeError, ValueError):
        return 3


def existe(projeto_id: str) -> bool:
    """Informa se o projeto existe (pasta + meta.json)."""
    return (projeto_dir(projeto_id) / "meta.json").is_file()


def listar() -> list[dict[str, Any]]:
    """Lista os ``meta.json`` de todos os projetos."""
    metas: list[dict[str, Any]] = []
    if not PROJETOS_DIR.is_dir():
        return metas
    for pasta in sorted(PROJETOS_DIR.iterdir()):
        if not pasta.is_dir():
            continue
        meta = ler_json(pasta / "meta.json")
        if isinstance(meta, dict):
            metas.append(meta)
    metas.sort(key=lambda item: str(item.get("criado_em") or ""), reverse=True)
    return metas


def meta(projeto_id: str) -> dict[str, Any] | None:
    """Le o ``meta.json`` de um projeto."""
    dados = ler_json(projeto_dir(projeto_id) / "meta.json")
    return dados if isinstance(dados, dict) else None


def salvar_meta(projeto_id: str, dados: dict[str, Any]) -> dict[str, Any]:
    """Grava o ``meta.json`` de um projeto."""
    dados = dict(dados)
    dados["atualizado_em"] = agora()
    gravar_json(projeto_dir(projeto_id) / "meta.json", dados)
    return dados


def _id_livre(nome: str) -> str:
    base = slug(nome)
    candidato = base
    contador = 2
    while existe(candidato) or (PROJETOS_DIR / candidato).exists():
        candidato = f"{base}-{contador}"
        contador += 1
    return candidato


def criar(nome: str, video: str) -> dict[str, Any]:
    """Cria um projeto novo com a estrutura de pastas do contrato M2."""
    nome = (nome or "").strip()
    if not nome:
        raise ErroProjeto("Informe um nome para o projeto.")
    caminho_video = Path(video).expanduser()
    if not caminho_video.is_file():
        raise ErroProjeto(f"O video de entrada nao foi encontrado: {caminho_video}")

    projeto_id = _id_livre(nome)
    base = projeto_dir(projeto_id)
    for sub in ("camadas", "saidas", "saidas/frames", "saidas/filme"):
        (base / sub).mkdir(parents=True, exist_ok=True)

    duracao = _duracao(caminho_video)
    estilos = []
    for identificador, dados in ESTILOS_M2.items():
        estilos.append(
            {
                "id": identificador,
                "rotulo": dados["rotulo"],
                "disponivel": dados["disponivel"],
                "motivo": dados["motivo"],
            }
        )

    dados_meta: dict[str, Any] = {
        "versao": 1,
        "id": projeto_id,
        "nome": nome,
        "criado_em": agora(),
        "atualizado_em": agora(),
        "entrada": {
            "video": str(caminho_video.resolve()),
            "sha256": _sha256(caminho_video),
            "duracao_s": duracao,
        },
        "status": "criado",
        "estilos": estilos,
        "tentativas": {estilo["id"]: 0 for estilo in estilos},
        "limite_tentativas": _limite_tentativas(),
        "aprovado": False,
        "aprovacao": None,
    }
    gravar_json(base / "meta.json", dados_meta)
    gravar_json(
        base / "cenas.json",
        {"versao": 1, "projeto": projeto_id, "cenas": []},
    )
    gravar_json(
        base / "movimento.json",
        {"versao": 1, "projeto": projeto_id, "movimento": {"por_amostra": [], "resumo": {}}},
    )
    gravar_json(base / "previa.json", {"versao": 1, "projeto": projeto_id, "previa_id": None})
    gravar_json(base / "avaliacoes.json", {"versao": 1, "avaliacoes": []})
    return dados_meta


def cenas(projeto_id: str) -> list[Any]:
    """Lista de cenas do projeto."""
    dados = ler_json(projeto_dir(projeto_id) / "cenas.json")
    if isinstance(dados, list):
        return dados
    if isinstance(dados, dict):
        lista = dados.get("cenas")
        if isinstance(lista, list):
            return lista
    return []


def mapa_tecnicas(projeto_id: str) -> dict[str, Any]:
    """Mapa de tecnicas do projeto."""
    dados = ler_json(projeto_dir(projeto_id) / "mapa_tecnicas.json")
    return dados if isinstance(dados, dict) else {}


def previa(projeto_id: str) -> dict[str, Any] | None:
    """Previa atual do projeto (``previa.json``)."""
    dados = ler_json(projeto_dir(projeto_id) / "previa.json")
    return dados if isinstance(dados, dict) else None


def listar_previas(projeto_id: str) -> list[dict[str, Any]]:
    """Lista de previas geradas (documento + arquivos em ``saidas/``)."""
    itens: list[dict[str, Any]] = []
    vistos: set[str] = set()
    documento = ler_json(projeto_dir(projeto_id) / "previa.json")
    if isinstance(documento, list):
        candidatos = documento
    elif isinstance(documento, dict) and documento.get("previa_id"):
        candidatos = [documento]
    else:
        candidatos = []
    for item in candidatos:
        if not isinstance(item, dict):
            continue
        itens.append(item)
        vistos.add(str(item.get("previa_id") or item.get("arquivo") or ""))

    saidas = projeto_dir(projeto_id) / "saidas"
    if saidas.is_dir():
        for arquivo in sorted(saidas.glob("previa_*.mp4")):
            previa_id = arquivo.stem.replace("previa_", "", 1)
            if previa_id in vistos:
                for item in itens:
                    if item.get("previa_id") == previa_id and not item.get("arquivo"):
                        item["arquivo"] = f"projetos/{projeto_id}/saidas/{arquivo.name}"
                continue
            est = previa_id.rsplit("_", 1)[0]
            miniatura = saidas / f"miniatura_{previa_id}.png"
            item = {
                "versao": 1,
                "projeto": projeto_id,
                "previa_id": previa_id,
                "estilo": est,
                "estilo_rotulo": ESTILOS_M2.get(est, {}).get("rotulo", est),
                "status": "pronto",
                "arquivo": f"projetos/{projeto_id}/saidas/{arquivo.name}",
                "miniatura": (
                    f"projetos/{projeto_id}/saidas/{miniatura.name}"
                    if miniatura.is_file()
                    else None
                ),
                "trecho": {"inicio_s": 0.0, "fim_s": 5.0, "duracao_s": 5.0},
                "resolucao": "854x480",
                "fps": 30,
                "tempo_geracao_s": 5.0,
                "gerado_em": agora(),
                "seguranca": {
                    "veredito": "verde",
                    "flashes": {"max_flashes_1s": 0, "limite": 3, "ok": True},
                    "volume": {"true_peak_dbtp": -14.0, "limite_dbtp": -6.0, "ok": True},
                    "conteudo": {"classificacao": "infantil", "ok": True, "motivo": None},
                    "mensagens": [],
                },
                "params": {"seed": 7, "resolucao": "480p", "modo": "rapido", "versao_preset": 1},
                "erro": None,
            }
            itens.append(item)
            vistos.add(previa_id)
    return itens


def derivar_analise(projeto_id: str, analise: dict[str, Any]) -> None:
    """Deriva ``cenas.json`` e ``movimento.json`` a partir da analise."""
    base = projeto_dir(projeto_id)
    lista_cenas = analise.get("cenas")
    if not isinstance(lista_cenas, list):
        lista_cenas = []
    gravar_json(
        base / "cenas.json",
        {"versao": 1, "projeto": projeto_id, "cenas": lista_cenas},
    )
    movimento = analise.get("movimento")
    if not isinstance(movimento, dict):
        movimento = {}
    gravar_json(
        base / "movimento.json",
        {"versao": 1, "projeto": projeto_id, "movimento": movimento},
    )


def atualizar_entrada(projeto_id: str, duracao_s: float | None) -> None:
    """Atualiza a duracao de entrada no ``meta.json`` (se conhecida)."""
    dados = meta(projeto_id)
    if not dados:
        return
    entrada = dados.get("entrada")
    if not isinstance(entrada, dict):
        return
    if duracao_s:
        entrada["duracao_s"] = round(float(duracao_s), 3)
        salvar_meta(projeto_id, dados)


def registrar_tentativa(projeto_id: str, estilo: str) -> None:
    """Conta uma tentativa de previa para o estilo informado."""
    dados = meta(projeto_id)
    if not dados:
        return
    tentativas = dados.get("tentativas")
    if not isinstance(tentativas, dict):
        tentativas = {}
    tentativas[estilo] = int(tentativas.get(estilo, 0)) + 1
    dados["tentativas"] = tentativas
    salvar_meta(projeto_id, dados)


def caminho_video(projeto_id: str) -> str | None:
    """Caminho absoluto do video de entrada do projeto."""
    dados = meta(projeto_id)
    if not dados:
        return None
    entrada = dados.get("entrada") or {}
    video = entrada.get("video")
    return str(video) if video else None


def caminho_relativo(caminho: Path) -> str:
    """Caminho relativo a raiz do projeto, com ``/``."""
    try:
        return caminho.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return caminho.as_posix()
