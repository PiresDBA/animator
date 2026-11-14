#!/usr/bin/env python3
"""Teste real de GPU: tensor + convolucao, com tempo, VRAM e temperatura.

Executar com um Python que tenha PyTorch (por exemplo, o venv do ComfyUI):
    D:\\Comfy\\ComfyUI\\venv\\Scripts\\python.exe descoberta/teste_gpu.py --salvar

Mede o que aconteceu; nao estima. O teste e curto de proposito para nao
provocar TDR no driver.
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def smi() -> dict:
    try:
        saida = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,power.draw,memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        partes = [p.strip() for p in saida.strip().splitlines()[0].split(",")]
        if len(partes) < 5:
            return {"erro": f"nvidia-smi inesperado: {saida!r}"}
        valores = []
        for item in partes[:5]:
            try:
                valores.append(float(item))
            except ValueError:
                valores.append(None)
        return {
            "temperatura_c": valores[0],
            "potencia_w": valores[1],
            "vram_usada_mib": valores[2],
            "vram_total_mib": valores[3],
            "utilizacao_pct": valores[4],
        }
    except Exception as exc:  # noqa: BLE001 - queremos o motivo no relatorio
        return {"erro": str(exc)}


class Monitor(threading.Thread):
    def __init__(self, intervalo: float = 0.5) -> None:
        super().__init__(daemon=True)
        self.intervalo = intervalo
        self.parar = threading.Event()
        self.amostras: list[dict] = []

    def run(self) -> None:
        while not self.parar.is_set():
            amostra = {"t_rel_s": round(time.monotonic(), 3)}
            amostra.update(smi())
            self.amostras.append(amostra)
            self.parar.wait(self.intervalo)

    def resumo(self) -> dict:
        def valores(chave: str) -> list[float]:
            return [
                a[chave]
                for a in self.amostras
                if isinstance(a.get(chave), (int, float))
            ]

        temps = valores("temperatura_c")
        potencias = valores("potencia_w")
        vram = valores("vram_usada_mib")
        util = valores("utilizacao_pct")
        return {
            "amostras": len(self.amostras),
            "temperatura_max_c": max(temps) if temps else None,
            "temperatura_mediana_c": round(statistics.median(temps), 1) if temps else None,
            "potencia_max_w": max(potencias) if potencias else None,
            "potencia_mediana_w": round(statistics.median(potencias), 1) if potencias else None,
            "vram_max_mib": max(vram) if vram else None,
            "utilizacao_max_pct": max(util) if util else None,
        }


def medir(fn, repeticoes: int = 3) -> dict:
    import torch

    tempos: list[float] = []
    for _ in range(repeticoes):
        torch.cuda.synchronize()
        inicio = torch.cuda.Event(enable_timing=True)
        fim = torch.cuda.Event(enable_timing=True)
        inicio.record()
        fn()
        fim.record()
        torch.cuda.synchronize()
        tempos.append(inicio.elapsed_time(fim))
    return {
        "repeticoes": repeticoes,
        "tempos_ms": [round(t, 3) for t in tempos],
        "mediana_ms": round(statistics.median(tempos), 3),
        "minimo_ms": round(min(tempos), 3),
        "maximo_ms": round(max(tempos), 3),
    }


def executar() -> dict:
    inicio_wall = time.monotonic()
    resultado: dict = {
        "versao": 1,
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origem": "descoberta/teste_gpu.py",
        "baseline_smi": smi(),
    }
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        resultado["erro"] = f"PyTorch indisponivel: {exc}"
        return resultado

    resultado.update(
        {
            "python": sys.version.splitlines()[0],
            "torch": torch.__version__,
            "cuda_build": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "cuda_disponivel": torch.cuda.is_available(),
        }
    )
    if not torch.cuda.is_available():
        resultado["erro"] = "torch.cuda.is_available() == False"
        return resultado

    try:
        torch.cuda.init()
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        capacidade = torch.cuda.get_device_capability(0)
        resultado["gpu"] = {
            "nome": props.name,
            "capacidade_sm": f"{capacidade[0]}.{capacidade[1]}",
            "vram_total_mib": round(props.total_memory / 1024**2, 1),
            "multiprocessadores": props.multi_processor_count,
        }

        torch.manual_seed(1234)
        a_pequeno = torch.randn(256, 256, device="cuda", dtype=torch.float32)
        b_pequeno = torch.randn(256, 256, device="cuda", dtype=torch.float32)
        c_gpu = a_pequeno @ b_pequeno
        c_cpu = a_pequeno.cpu() @ b_pequeno.cpu()
        torch.testing.assert_close(c_gpu.cpu(), c_cpu, rtol=2e-3, atol=2e-3)
        resultado["corretude"] = {
            "teste": "matmul 256x256 float32 GPU vs CPU",
            "ok": bool(torch.isfinite(c_gpu).all().item()),
            "rtol": 2e-3,
            "atol": 2e-3,
        }

        for _ in range(2):
            x = torch.randn(512, 512, device="cuda", dtype=torch.float32)
            _ = x @ x
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats()

        monitor = Monitor(intervalo=0.25)
        monitor.start()

        a = torch.randn(4096, 4096, device="cuda", dtype=torch.float32)
        b = torch.randn(4096, 4096, device="cuda", dtype=torch.float32)
        resultado["matmul_4096"] = medir(lambda: a @ b)

        entrada = torch.randn(1, 32, 512, 512, device="cuda", dtype=torch.float32)
        peso = torch.randn(64, 32, 3, 3, device="cuda", dtype=torch.float32)
        resultado["conv2d_64x32x3x3_512"] = medir(
            lambda: torch.nn.functional.conv2d(entrada, peso, padding=1)
        )

        torch.cuda.synchronize()
        monitor.parar.set()
        monitor.join(timeout=2.0)

        resultado["vram_torch_pico_mib"] = round(
            torch.cuda.max_memory_allocated() / 1024**2, 1
        )
        resultado["vram_torch_reservada_mib"] = round(
            torch.cuda.max_memory_reserved() / 1024**2, 1
        )
        resultado["monitor"] = monitor.resumo()
        resultado["duracao_total_s"] = round(time.monotonic() - inicio_wall, 2)
        resultado["ok"] = True
    except Exception as exc:  # noqa: BLE001
        resultado["erro"] = f"{type(exc).__name__}: {exc}"
        resultado["ok"] = False
    return resultado


def main() -> int:
    parser = argparse.ArgumentParser(description="Teste real de GPU (matmul + convolucao).")
    parser.add_argument("--salvar", action="store_true")
    parser.add_argument(
        "--saida", type=Path, default=RAIZ / "docs" / "evidencias" / "teste_gpu.json"
    )
    args = parser.parse_args()

    dados = executar()
    texto = json.dumps(dados, ensure_ascii=False, indent=2)
    if args.salvar:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto + "\n", encoding="utf-8")
        print(f"OK: {args.saida}")
    else:
        print(texto)
    return 0 if dados.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
