#!/usr/bin/env python3
"""Descoberta local de programas, somente leitura.

Ordem: config.json -> PATH/where -> registro do Windows -> pastas comuns ->
varredura de raizes com prazo maximo. Nenhum arquivo e alterado.

Assinaturas:
  ComfyUI        main.py + models/ (ou python_embeded + main.py)
  Remotion       package.json com dependencia "remotion"
  Motor bonecos  package.json com "three" + "remotion" ou engine/render.mjs +
                 engine/character.js (motor local stick-film)
  EffectCraft    effectcraft.exe / effectcraft-cli.exe
  FFmpeg         ffmpeg.exe + ffprobe.exe na mesma pasta
  VideoFactoryAI pasta VideoFactoryAI ou videofactory_gui.py + config.yaml
"""
from __future__ import annotations

import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

RAIZ = Path(__file__).resolve().parents[1]

EXCLUIR_DIRS = {
    "$recycle.bin",
    "system volume information",
    "windows",
    "recovery",
    "msdownld.tmp",
    "node_modules",
    "venv",
    ".venv",
    "site-packages",
    "__pycache__",
    ".git",
    ".hg",
    ".svn",
    ".cache",
    "temp",
    "tmp",
    "steamlibrary",
    "games",
    "docker",
    "ollamamodels",
    "onedrive",
    "onedrive-bkp",
    "onedrivecache",
    "onedrivetemp",
    "backup",
    "backup-onedrive-settings",
    "backups",
    "$windows.~bt",
    "$windows.~ws",
    "appdata",
}

NAO_DESCER = {
    "models",
    "checkpoints",
    "loras",
    "controlnet",
    "vae",
    "ipadapter",
    "animatediff_models",
    "animatediff_motion_lora",
    "upscale_models",
    "embeddings",
    "custom_nodes",
    "node_modules",
    "venv",
    ".venv",
    ".git",
    "__pycache__",
}

RAIZES_PADRAO: list[tuple[Path, int]] = [
    (Path("D:/PROJETOS-IA"), 5),
    (Path("D:/CRAFT"), 4),
    (Path("D:/"), 5),
    (Path(os.path.expandvars(r"C:\Users\%USERNAME%")), 5),
    (Path(r"C:\Program Files"), 4),
    (Path(r"C:\Program Files (x86)"), 4),
    (Path(r"C:\ProgramData"), 3),
    (Path(os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Programs")), 5),
    (
        Path(
            os.path.expandvars(
                r"C:\Users\%USERNAME%\AppData\Local\Microsoft\WinGet\Packages"
            )
        ),
        5,
    ),
]

PASTAS_COMUNS = [
    r"D:\Comfy\ComfyUI",
    r"D:\Comfy",
    r"D:\ComfyUI",
    r"C:\ComfyUI",
    r"D:\ComfyUI_windows_portable",
    r"D:\PROJETOS-IA\stick-film\stick-film",
    r"D:\CRAFT\EffectCraft",
    r"C:\Program Files\EffectCraft",
    r"D:\PROJETOS-IA\Fabrica-de-videos",
    r"D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI",
    r"C:\Users\Pires\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin",
    r"D:\PROJETOS-IA\animacao\estudio\tools\ffmpeg",
    r"C:\Users\Pires\AppData\Roaming\npm\node_modules",
    r"D:\PROJETOS-IA\remotion",
    r"D:\remotion",
]


def carregar_config(raiz: Path) -> dict:
    caminho = raiz / "config.json"
    if not caminho.is_file():
        return {}
    try:
        return json.loads(caminho.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ler_package(p: Path) -> dict | None:
    pj = p / "package.json"
    if not pj.is_file():
        return None
    try:
        if pj.stat().st_size > 2_000_000:
            return None
        dados = json.loads(pj.read_text(encoding="utf-8-sig", errors="replace"))
        return dados if isinstance(dados, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _deps(dados: dict) -> dict:
    deps: dict = {}
    for chave in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        valor = dados.get(chave)
        if isinstance(valor, dict):
            deps.update(valor)
    return deps


def identificar(p: Path) -> list[tuple[str, str]]:
    """Retorna [(tipo, evidencia)] para uma pasta. Nao escreve nada."""
    achados: list[tuple[str, str]] = []
    try:
        if not p.is_dir():
            return achados
    except OSError:
        return achados

    if (p / "main.py").is_file() and (p / "models").is_dir():
        achados.append(("comfyui", "main.py + models/"))
    if (p / "python_embeded" / "python.exe").is_file() and (
        (p / "main.py").is_file() or (p / "ComfyUI" / "main.py").is_file()
    ):
        achados.append(("comfyui", "python_embeded + main.py"))

    if (p / "ffmpeg.exe").is_file() and (p / "ffprobe.exe").is_file():
        achados.append(("ffmpeg", "ffmpeg.exe + ffprobe.exe"))

    if (p / "effectcraft.exe").is_file() or (p / "effectcraft-cli.exe").is_file():
        achados.append(("effectcraft", "effectcraft.exe / effectcraft-cli.exe"))

    nome = p.name.lower()
    if nome in {"videofactoryai", "fabrica-de-videos"}:
        achados.append(("videofactoryai", "nome da pasta + projeto local"))
    elif (p / "videofactory_gui.py").is_file() and (p / "config.yaml").is_file():
        achados.append(("videofactoryai", "videofactory_gui.py + config.yaml"))

    if (p / "engine" / "render.mjs").is_file() and (p / "engine" / "character.js").is_file():
        achados.append(("motor_bonecos", "engine/render.mjs + engine/character.js"))

    dados = _ler_package(p)
    if dados:
        deps = _deps(dados)
        tem_remotion = any(k == "remotion" or k.startswith("@remotion/") for k in deps)
        tem_three = "three" in deps or "@remotion/three" in deps
        if tem_remotion and tem_three:
            achados.append(("motor_bonecos", "package.json: three + remotion"))
        elif tem_remotion:
            evid = "package.json: remotion"
            if (p / "src" / "Root.tsx").is_file() or (p / "src" / "Root.ts").is_file():
                evid += " + src/Root.tsx"
            achados.append(("remotion", evid))

    return achados


def _adicionar(
    resultados: list[dict],
    vistos: set[tuple[str, str]],
    tipo: str,
    caminho: Path,
    evidencia: str,
    origem: str,
) -> None:
    chave = (tipo, str(caminho).rstrip("\\/").lower())
    if chave in vistos:
        return
    vistos.add(chave)
    resultados.append(
        {
            "tipo": tipo,
            "caminho": str(caminho),
            "evidencia": evidencia,
            "origem": origem,
        }
    )


def descobrir_path(resultados: list[dict], vistos: set[tuple[str, str]]) -> None:
    for exe in ("ffmpeg", "ffprobe"):
        caminho = shutil.which(exe)
        if not caminho:
            continue
        pasta = Path(caminho).parent
        for tipo, evid in identificar(pasta):
            _adicionar(resultados, vistos, tipo, pasta, evid, "PATH")


def descobrir_registro(resultados: list[dict], vistos: set[tuple[str, str]]) -> None:
    try:
        import winreg
    except ImportError:
        return
    chaves = [
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        (
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    padroes = ("comfy", "remotion", "ffmpeg", "effectcraft", "videofactory", "video factory")
    for raiz, sub in chaves:
        try:
            with winreg.OpenKey(raiz, sub) as chave:
                total = winreg.QueryInfoKey(chave)[0]
                for indice in range(total):
                    try:
                        nome = winreg.EnumKey(chave, indice)
                        with winreg.OpenKey(chave, nome) as item:
                            try:
                                display = str(winreg.QueryValueEx(item, "DisplayName")[0])
                            except OSError:
                                continue
                            if not any(p in display.lower() for p in padroes):
                                continue
                            try:
                                local = str(winreg.QueryValueEx(item, "InstallLocation")[0])
                            except OSError:
                                local = ""
                            if not local:
                                continue
                            pasta = Path(local.strip('"'))
                            if not pasta.exists():
                                continue
                            achados = identificar(pasta)
                            if achados:
                                for tipo, evid in achados:
                                    _adicionar(
                                        resultados,
                                        vistos,
                                        tipo,
                                        pasta,
                                        f"{evid} (registro: {display})",
                                        "registro",
                                    )
                    except OSError:
                        continue
        except OSError:
            continue


def descobrir_pastas_comuns(resultados: list[dict], vistos: set[tuple[str, str]]) -> None:
    for texto in PASTAS_COMUNS:
        pasta = Path(os.path.expandvars(texto))
        if not pasta.exists():
            continue
        for tipo, evid in identificar(pasta):
            _adicionar(resultados, vistos, tipo, pasta, evid, "pasta_comum")


def _varrer_pasta(
    raiz: Path,
    max_profundidade: int,
    deadline: float,
    resultados: list[dict],
    vistos: set[tuple[str, str]],
    stats: dict,
) -> None:
    pilha: list[tuple[Path, int]] = [(raiz, 0)]
    while pilha and time.monotonic() < deadline:
        pasta, profundidade = pilha.pop()
        if pasta.is_symlink():
            continue
        stats["pastas"] += 1
        try:
            for tipo, evid in identificar(pasta):
                _adicionar(resultados, vistos, tipo, pasta, evid, "varredura")
            if profundidade >= max_profundidade or pasta.name.lower() in NAO_DESCER:
                continue
            with os.scandir(pasta) as it:
                for contador, entrada in enumerate(it, start=1):
                    if contador % 500 == 0 and time.monotonic() >= deadline:
                        break
                    try:
                        if (
                            entrada.is_dir(follow_symlinks=False)
                            and entrada.name.lower() not in EXCLUIR_DIRS
                        ):
                            pilha.append((Path(entrada.path), profundidade + 1))
                    except OSError:
                        stats["erros"] += 1
        except (PermissionError, OSError):
            stats["erros"] += 1


def varrer_raizes(
    raizes: Iterable[tuple[Path, int]], max_seconds: float = 180.0
) -> tuple[list[dict], dict]:
    inicio = time.monotonic()
    deadline = inicio + max_seconds
    resultados: list[dict] = []
    vistos: set[tuple[str, str]] = set()
    stats = {"pastas": 0, "erros": 0, "duracao_s": 0.0, "concluida": False, "raizes": []}
    for raiz, profundidade in raizes:
        if not raiz.exists():
            continue
        stats["raizes"].append({"caminho": str(raiz), "profundidade": profundidade})
        if time.monotonic() >= deadline:
            break
        _varrer_pasta(raiz, profundidade, deadline, resultados, vistos, stats)
    stats["duracao_s"] = round(time.monotonic() - inicio, 2)
    stats["concluida"] = time.monotonic() < deadline
    return resultados, stats


def descobrir_tudo(
    raiz_projeto: Path = RAIZ,
    max_seconds: float = 180.0,
    fazer_varredura: bool = True,
) -> dict:
    inicio = time.monotonic()
    resultados: list[dict] = []
    vistos: set[tuple[str, str]] = set()

    config = carregar_config(raiz_projeto)
    for nome, valor in (config.get("caminhos") or {}).items():
        if not isinstance(valor, str) or not valor:
            continue
        pasta = Path(os.path.expandvars(valor))
        if not pasta.is_absolute():
            pasta = raiz_projeto / pasta
        if not pasta.exists():
            continue
        for tipo, evid in identificar(pasta):
            _adicionar(resultados, vistos, tipo, pasta, f"{evid} (config: {nome})", "config")

    descobrir_path(resultados, vistos)
    descobrir_registro(resultados, vistos)
    descobrir_pastas_comuns(resultados, vistos)

    stats = {"pastas": 0, "erros": 0, "duracao_s": 0.0, "concluida": True, "raizes": []}
    if fazer_varredura:
        restante = max(1.0, max_seconds - (time.monotonic() - inicio))
        encontrados, stats = varrer_raizes(RAIZES_PADRAO, restante)
        for item in encontrados:
            _adicionar(
                resultados,
                vistos,
                item["tipo"],
                Path(item["caminho"]),
                item["evidencia"],
                item["origem"],
            )
    stats["duracao_total_s"] = round(time.monotonic() - inicio, 2)
    stats["limite_s"] = max_seconds
    return {"versao": 1, "resultados": resultados, "estatisticas": stats}


def formatar_tabela(resultados: list[dict]) -> str:
    if not resultados:
        return "Nenhum programa encontrado."
    largura_tipo = max(len("TIPO"), max(len(r["tipo"]) for r in resultados))
    largura_origem = max(len("ORIGEM"), max(len(r["origem"]) for r in resultados))
    linhas = [
        f"{'TIPO':<{largura_tipo}}  {'ORIGEM':<{largura_origem}}  CAMINHO  |  EVIDENCIA"
    ]
    linhas.append("-" * min(160, len(linhas[0]) + 60))
    for item in sorted(resultados, key=lambda r: (r["tipo"], r["caminho"].lower())):
        linhas.append(
            f"{item['tipo']:<{largura_tipo}}  {item['origem']:<{largura_origem}}  "
            f"{item['caminho']}  |  {item['evidencia']}"
        )
    return "\n".join(linhas)


def salvar_resultado(dados: dict, destino: Path, confirmado: bool = False) -> None:
    payload = {
        "versao": 1,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "confirmado_pelo_usuario": confirmado,
        **dados,
    }
    if confirmado:
        payload["confirmado_em"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
