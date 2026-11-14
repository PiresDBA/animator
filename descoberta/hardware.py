#!/usr/bin/env python3
"""Coleta o perfil de hardware local sem alterar o sistema.

Uso:
    py -3.12 descoberta/hardware.py
    py -3.12 descoberta/hardware.py --salvar

Somente leitura: consulta WMI/CIM, nvidia-smi e discos. Nao instala nada.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

PS_SISTEMA = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
[pscustomobject]@{
  sistema = [pscustomobject]@{
    caption = $os.Caption
    version = $os.Version
    build = $os.BuildNumber
    arch = $os.OSArchitecture
  }
  computador = [pscustomobject]@{
    fabricante = $cs.Manufacturer
    modelo = $cs.Model
    ram_bytes = [int64]$cs.TotalPhysicalMemory
  }
  cpu = [pscustomobject]@{
    nome = $cpu.Name
    nucleos = $cpu.NumberOfCores
    threads = $cpu.NumberOfLogicalProcessors
  }
} | ConvertTo-Json -Compress -Depth 5
"""


def _run(cmd: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as exc:  # noqa: BLE001 - diagnostico precisa do motivo real
        return -1, "", str(exc)


def _json_ps(script: str) -> dict:
    code, out, err = _run(
        ["powershell", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script]
    )
    if code != 0:
        raise RuntimeError(f"PowerShell falhou: {err or out}")
    if not out:
        raise RuntimeError("PowerShell nao retornou JSON")
    return json.loads(out)


def _num(valor: object) -> float | None:
    if valor is None:
        return None
    texto = str(valor).strip().replace(",", ".")
    if texto in {"", "[N/A]", "N/A"}:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def coletar_gpu() -> dict:
    if not shutil.which("nvidia-smi"):
        return {"disponivel": False, "motivo": "nvidia-smi nao encontrado no PATH", "gpus": []}
    campos = "name,driver_version,memory.total,memory.used,temperature.gpu,power.draw,utilization.gpu"
    code, out, err = _run(
        ["nvidia-smi", f"--query-gpu={campos}", "--format=csv,noheader,nounits"], timeout=15
    )
    if code != 0:
        return {"disponivel": False, "motivo": err or out, "gpus": []}
    gpus = []
    for linha in out.splitlines():
        partes = [p.strip() for p in linha.split(",")]
        if len(partes) < 7:
            continue
        gpus.append(
            {
                "nome": partes[0],
                "driver": partes[1],
                "vram_total_mib": _num(partes[2]),
                "vram_usada_mib": _num(partes[3]),
                "temperatura_c": _num(partes[4]),
                "potencia_w": _num(partes[5]),
                "utilizacao_pct": _num(partes[6]),
            }
        )
    return {"disponivel": bool(gpus), "gpus": gpus, "medido_em_repouso": True}


def coletar_discos() -> list[dict]:
    try:
        raizes = list(os.listdrives())
    except AttributeError:
        raizes = [f"{letra}:\\" for letra in "CDEFGHIJKLMNOPQRSTUVWXYZ"]
    discos = []
    for raiz in raizes:
        if not Path(raiz).exists():
            continue
        try:
            uso = shutil.disk_usage(raiz)
        except OSError:
            continue
        discos.append(
            {
                "raiz": raiz,
                "total_gb": round(uso.total / 1024**3, 1),
                "usado_gb": round(uso.used / 1024**3, 1),
                "livre_gb": round(uso.free / 1024**3, 1),
            }
        )
    return discos


def coletar_ferramentas() -> dict:
    ferramentas = {}
    for nome in ("python", "py", "node", "npm", "git", "ffmpeg", "ffprobe", "nvidia-smi"):
        caminho = shutil.which(nome)
        item = {"caminho": caminho, "versao": None}
        if caminho:
            if nome == "nvidia-smi":
                code, out, _ = _run([caminho, "--version"], timeout=10)
                item["versao"] = out.splitlines()[0] if code == 0 and out else None
            elif nome == "npm":
                code, out, _ = _run(["cmd", "/c", "npm", "--version"], timeout=15)
                item["versao"] = out if code == 0 else None
            else:
                code, out, _ = _run([caminho, "--version"], timeout=10)
                item["versao"] = out.splitlines()[0] if code == 0 and out else None
        ferramentas[nome] = item
    return ferramentas


def coletar() -> dict:
    sistema = _json_ps(PS_SISTEMA)
    ram_bytes = int(sistema["computador"]["ram_bytes"])
    return {
        "versao": 1,
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origem": "descoberta/hardware.py",
        "sistema": sistema["sistema"],
        "computador": {
            "fabricante": sistema["computador"]["fabricante"],
            "modelo": sistema["computador"]["modelo"],
            "ram_bytes": ram_bytes,
            "ram_gb": round(ram_bytes / 1024**3, 2),
        },
        "cpu": sistema["cpu"],
        "gpu": coletar_gpu(),
        "discos": coletar_discos(),
        "ferramentas": coletar_ferramentas(),
        "python_do_script": {
            "executavel": sys.executable,
            "versao": platform.python_version(),
            "plataforma": platform.platform(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta perfil de hardware (somente leitura).")
    parser.add_argument("--salvar", action="store_true", help="grava perfil_hardware.json")
    parser.add_argument(
        "--saida",
        type=Path,
        default=RAIZ / "perfil_hardware.json",
        help="caminho do JSON de saida quando --salvar",
    )
    args = parser.parse_args()

    perfil = coletar()
    texto = json.dumps(perfil, ensure_ascii=False, indent=2)
    if args.salvar:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto + "\n", encoding="utf-8")
        print(f"OK: {args.saida}")
    else:
        print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
