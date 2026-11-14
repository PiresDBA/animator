"""Cliente de Renderizacao de Animacao em Alta Fidelidade via ComfyUI.

Utiliza AnimateDiff (mm_sd_v15_v2.ckpt) + DreamShaper 8 (dreamshaper_8.safetensors)
e VideoHelperSuite para transformar o video em animacao estilizada de cinema.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HOST_COMFY = "127.0.0.1:8188"

PROMPTS_ESTILOS = {
    "anime": {
        "positivo": (
            "masterpiece, best quality, makoto shinkai anime movie aesthetic, "
            "beautiful 2d animated cel, sharp lineart, vibrant studio ghibli lighting, "
            "expressive character, highly detailed anime scenery, cinematic"
        ),
        "negativo": "photorealistic, realistic, 3d, blurry, lowres, watermark, text, deformed, extra limbs, ugly",
        "denoise": 0.62,
    },
    "cartoon": {
        "positivo": (
            "masterpiece, best quality, cute 3d pixar disney movie render, "
            "stylized 3d character, subsurface scattering, soft studio lighting, "
            "raytracing, octane render, smooth surfaces, charming expressions"
        ),
        "negativo": "photorealistic, real person, 2d, sketch, flat, blurry, low quality, deformed, extra limbs",
        "denoise": 0.65,
    },
    "lego": {
        "positivo": (
            "masterpiece, best quality, lego movie stop-motion animation, "
            "character as plastic lego minifigure, toy world made of shiny lego bricks with studs, "
            "miniature tilt-shift photography, depth of field, cinematic lighting"
        ),
        "negativo": "human, flesh, photorealistic person, blurry, lowres, watermark, deformed, bad anatomy",
        "denoise": 0.68,
    },
    "3d": {
        "positivo": (
            "masterpiece, best quality, unreal engine 5 cinematic 3d render, "
            "cinematic pbr materials, volumetric lighting, raytraced shadows, "
            "detailed textures, photorealistic cgi film quality, 8k"
        ),
        "negativo": "cartoon, 2d, drawing, sketch, blurry, low quality, artifacts, watermark, deformed",
        "denoise": 0.58,
    },
}


def comfy_disponivel() -> bool:
    """Verifica se o servidor ComfyUI esta acessivel."""
    try:
        url = f"http://{HOST_COMFY}/system_stats"
        req = urllib.request.Request(url, headers={"User-Agent": "EstudioAnimacao/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def construir_grafo_animatediff(
    caminho_video: Path,
    estilo: str = "anime",
    duracao_s: float = 3.0,
    fps: int = 15,
    seed: int = 42,
) -> dict[str, Any]:
    """Monta o workflow de AnimateDiff Video-to-Video no formato nativo da API do ComfyUI."""
    cfg_estilo = PROMPTS_ESTILOS.get(estilo, PROMPTS_ESTILOS["anime"])
    prompt_pos = cfg_estilo["positivo"]
    prompt_neg = cfg_estilo["negativo"]
    denoise = cfg_estilo["denoise"]

    total_frames = max(8, min(48, int(round(duracao_s * fps))))

    prompt = {
        # 1. Carregador de Checkpoint
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "dreamshaper_8.safetensors",
            },
        },
        # 2. Carregador do AnimateDiff
        "2": {
            "class_type": "ADE_AnimateDiffLoaderWithContext",
            "inputs": {
                "model": ["1", 0],
                "model_name": "mm_sd_v15_v2.ckpt",
                "beta_schedule": "sqrt_linear (AnimateDiff)",
            },
        },
        # 3. Carregador de Vídeo
        "3": {
            "class_type": "VHS_LoadVideoPath",
            "inputs": {
                "video": str(caminho_video.resolve()).replace("\\", "/"),
                "force_rate": float(fps),
                "custom_width": 512,
                "custom_height": 512,
                "frame_load_cap": total_frames,
                "skip_first_frames": 0,
                "select_every_nth": 1,
            },
        },
        # 4. VAE Encode dos frames originais
        "4": {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": ["3", 0],
                "vae": ["1", 2],
            },
        },
        # 5. Prompt Positivo
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": prompt_pos,
            },
        },
        # 6. Prompt Negativo
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "clip": ["1", 1],
                "text": prompt_neg,
            },
        },
        # 7. KSampler guiado por AnimateDiff
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["5", 0],
                "negative": ["6", 0],
                "latent_image": ["4", 0],
                "seed": seed,
                "steps": 14,
                "cfg": 6.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": denoise,
            },
        },
        # 8. VAE Decode
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["7", 0],
                "vae": ["1", 2],
            },
        },
        # 9. Combinador de Vídeo MP4
        "9": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["8", 0],
                "frame_rate": float(fps),
                "loop_count": 0,
                "filename_prefix": f"studio_{estilo}",
                "format": "video/h264-mp4",
                "pingpong": False,
                "save_output": True,
            },
        },
    }
    return prompt


def disparar_geracao(prompt_grafo: dict[str, Any]) -> str:
    """Envia o prompt para o ComfyUI e retorna o prompt_id."""
    url = f"http://{HOST_COMFY}/prompt"
    dados = json.dumps({"prompt": prompt_grafo}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=dados,
        headers={"Content-Type": "application/json", "User-Agent": "EstudioAnimacao/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        resultado = json.loads(resp.read().decode("utf-8"))
        return resultado.get("prompt_id")


def aguardar_conclusao(prompt_id: str, timeout_s: float = 300.0) -> dict[str, Any] | None:
    """Aguarda o fim da execucao consultando o historico do ComfyUI."""
    inicio = time.time()
    url = f"http://{HOST_COMFY}/history/{prompt_id}"
    while time.time() - inicio < timeout_s:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "EstudioAnimacao/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                dados = json.loads(resp.read().decode("utf-8"))
                if prompt_id in dados:
                    return dados[prompt_id]
        except Exception:
            pass
        time.sleep(2.0)
    return None


def extrair_caminho_video_saida(historico: dict[str, Any]) -> Path | None:
    """Localiza o arquivo de video MP4 gerado na saida do VHS_VideoCombine."""
    saidas = historico.get("outputs", {})
    for node_id, dados_node in saidas.items():
        gifs = dados_node.get("gifs", []) or dados_node.get("images", [])
        for item in gifs:
            filename = item.get("filename")
            subfolder = item.get("subfolder", "")
            tipo = item.get("type", "output")
            if filename and filename.endswith(".mp4"):
                comfy_out = Path(r"D:\Comfy\ComfyUI\output")
                caminho = comfy_out / subfolder / filename
                if caminho.is_file():
                    return caminho
    return None


def renderizar_animacao_alta_qualidade(
    caminho_video: Path,
    estilo: str,
    destino_mp4: Path,
    duracao_s: float = 3.0,
    seed: int = 42,
) -> bool:
    """Executa o pipeline completo de renderizacao AnimateDiff em alta fidelidade."""
    if not comfy_disponivel():
        return False

    prompt_grafo = construir_grafo_animatediff(
        caminho_video=caminho_video,
        estilo=estilo,
        duracao_s=duracao_s,
        fps=15,
        seed=seed,
    )

    prompt_id = disparar_geracao(prompt_grafo)
    if not prompt_id:
        return False

    historico = aguardar_conclusao(prompt_id, timeout_s=360.0)
    if not historico:
        return False

    caminho_gerado = extrair_caminho_video_saida(historico)
    if caminho_gerado and caminho_gerado.is_file():
        import shutil
        destino_mp4.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(caminho_gerado, destino_mp4)
        return True

    return False
