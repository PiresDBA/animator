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
            "masterpiece, best quality, Makoto Shinkai and Studio Ghibli anime feature film, "
            "vibrant cel shading, lush scenic sky with volumetric clouds, bright golden sunbeams, "
            "crystal clean sharp lineart, expressive anime character with lively fluid motion, "
            "gorgeous colorful anime palette, cinematic composition, highly detailed, 8k"
        ),
        "negativo": (
            "dark, murky, muddy, pitch black, underexposed, realistic photo, 3d render, "
            "lowres, blurry, bad anatomy, deformed limbs, text, watermarks, grainy, glitch, ugly"
        ),
        "denoise": 0.78,
    },
    "cartoon": {
        "positivo": (
            "masterpiece, best quality, Disney Pixar 3D animated movie, "
            "cute charming stylized 3D character, soft studio key light and rim lighting, "
            "subsurface scattering, Octane 3D render, smooth stylized geometry, "
            "vibrant cheerful colors, rich volumetric lighting, cinematic depth of field, 4k"
        ),
        "negativo": (
            "dark, gloomy, flat 2d, sketch, photorealistic human, ugly, bad hands, deformed, "
            "text, watermark, low quality, noisy, monochrome"
        ),
        "denoise": 0.80,
    },
    "lego": {
        "positivo": (
            "masterpiece, best quality, The Lego Movie cinematic animation, "
            "stop-motion plastic miniature aesthetic, shiny plastic minifigure character with glossy reflection, "
            "world completely built of colorful Lego bricks with authentic studs, "
            "tactile glossy materials, tilt-shift macro lens, cinematic studio lighting"
        ),
        "negativo": (
            "human flesh, realistic skin, flat 2d, dark, blurry, deformed, text, watermark, ugly"
        ),
        "denoise": 0.82,
    },
    "3d": {
        "positivo": (
            "masterpiece, best quality, Unreal Engine 5 cinematic animated CGI film, "
            "stylized 3D character with PBR materials, volumetric god rays, "
            "raytraced ambient occlusion and reflections, rich color grading, "
            "Pixar Dreamworks cinematic quality, vivid vibrant colors, 8k render"
        ),
        "negativo": (
            "2d drawing, sketch, flat, murky, dark, noisy, lowres, deformed, bad anatomy, text, watermark"
        ),
        "denoise": 0.78,
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
    duracao_s: float = 2.0,
    fps: int = 12,
    seed: int = 42,
) -> dict[str, Any]:
    """Monta o workflow de AnimateDiff Video-to-Video no formato nativo da API do ComfyUI.

    Utiliza ADE_AnimateDiffUniformContextOptions para permitir processamento com janela
    deslizante estavel e coerencia temporal cinematografica.
    """
    cfg_estilo = PROMPTS_ESTILOS.get(estilo, PROMPTS_ESTILOS["anime"])
    prompt_pos = cfg_estilo["positivo"]
    prompt_neg = cfg_estilo["negativo"]
    denoise = cfg_estilo["denoise"]

    total_frames = max(8, min(24, int(round(duracao_s * fps))))

    prompt = {
        # 1. Carregador de Checkpoint
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "dreamshaper_8.safetensors",
            },
        },
        # 10. Opcoes de Janela de Contexto Uniforme do AnimateDiff
        "10": {
            "class_type": "ADE_AnimateDiffUniformContextOptions",
            "inputs": {
                "context_length": 16,
                "context_stride": 1,
                "context_overlap": 4,
                "context_schedule": "uniform",
                "closed_loop": False,
            },
        },
        # 2. Carregador do AnimateDiff com contexto
        "2": {
            "class_type": "ADE_AnimateDiffLoaderWithContext",
            "inputs": {
                "model": ["1", 0],
                "context_options": ["10", 0],
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
                "custom_width": 384,
                "custom_height": 384,
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
                "cfg": 7.0,
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


def aguardar_conclusao(prompt_id: str, timeout_s: float = 1200.0) -> dict[str, Any] | None:
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
    status_info = historico.get("status", {})
    if status_info.get("status_str") == "error":
        msgs = status_info.get("messages", [])
        print(f"[ComfyUI] Erro na execucao: {msgs}")
        return None

    saidas = historico.get("outputs", {})
    for node_id, dados_node in saidas.items():
        gifs = dados_node.get("gifs", []) or dados_node.get("images", [])
        for item in gifs:
            filename = item.get("filename")
            subfolder = item.get("subfolder", "")
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
    duracao_s: float = 2.0,
    seed: int = 42,
) -> bool:
    """Executa o pipeline completo de renderizacao AnimateDiff em alta fidelidade."""
    if not comfy_disponivel():
        return False

    prompt_grafo = construir_grafo_animatediff(
        caminho_video=caminho_video,
        estilo=estilo,
        duracao_s=duracao_s,
        fps=12,
        seed=seed,
    )

    prompt_id = disparar_geracao(prompt_grafo)
    if not prompt_id:
        return False

    historico = aguardar_conclusao(prompt_id, timeout_s=1200.0)
    if not historico:
        return False

    caminho_gerado = extrair_caminho_video_saida(historico)
    if caminho_gerado and caminho_gerado.is_file() and caminho_gerado.stat().st_size > 50_000:
        import shutil
        destino_mp4.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(caminho_gerado, destino_mp4)
        return True

    return False
