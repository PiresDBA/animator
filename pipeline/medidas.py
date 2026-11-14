"""Medicao de tempo e GPU com nvidia-smi."""
from __future__ import annotations

import subprocess
import threading


def _criar_sem_janela() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def gpu_info() -> dict:
    comando = [
        "nvidia-smi",
        "--query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        saida = subprocess.check_output(
            comando,
            text=True,
            encoding="utf-8",
            timeout=5,
            creationflags=_criar_sem_janela(),
        ).strip()
        valores = [x.strip() for x in saida.splitlines()[0].split(",")]
        if len(valores) != 4:
            return {"erro": f"saida inesperada: {saida!r}"}
        usado, total, temperatura, utilizacao = [float(x) for x in valores]
        return {
            "vram_usada_mb": usado,
            "vram_total_mb": total,
            "temp_c": temperatura,
            "util_pct": utilizacao,
        }
    except Exception as exc:
        return {"erro": str(exc)}


class MonitorGPU(threading.Thread):
    def __init__(self, intervalo_s: float = 0.5):
        super().__init__(daemon=True)
        self.intervalo_s = intervalo_s
        self._parar = threading.Event()
        self.amostras: list[dict] = []
        self.erros: list[str] = []

    def run(self) -> None:
        while not self._parar.is_set():
            info = gpu_info()
            if "erro" in info:
                if len(self.erros) < 5:
                    self.erros.append(info["erro"])
            else:
                self.amostras.append(info)
            self._parar.wait(self.intervalo_s)

    def parar(self) -> dict:
        self._parar.set()
        self.join(timeout=5)
        return self.resumo()

    def resumo(self) -> dict:
        if not self.amostras:
            return {
                "amostras": 0,
                "vram_inicio_mb": None,
                "vram_fim_mb": None,
                "vram_pico_mb": None,
                "vram_total_mb": None,
                "temp_max_c": None,
                "util_max_pct": None,
                "nota": "nvidia-smi sem amostras",
                "erros": self.erros[:5],
            }
        vram = [a["vram_usada_mb"] for a in self.amostras]
        total = [a["vram_total_mb"] for a in self.amostras]
        temp = [a["temp_c"] for a in self.amostras]
        util = [a["util_pct"] for a in self.amostras]
        return {
            "amostras": len(self.amostras),
            "vram_inicio_mb": round(float(vram[0]), 1),
            "vram_fim_mb": round(float(vram[-1]), 1),
            "vram_pico_mb": round(float(max(vram)), 1),
            "vram_total_mb": round(float(max(total)), 1),
            "temp_max_c": round(float(max(temp)), 1),
            "util_max_pct": round(float(max(util)), 1),
            "nota": "nvidia-smi mede a GPU inteira; valores incluem outros processos",
            "erros": self.erros[:5],
        }
