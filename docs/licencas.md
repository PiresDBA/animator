# Licenças e direitos

Verificado em 2026-11-14 nas fontes indicadas. Este documento é um registro
técnico, não um parecer jurídico. Antes de baixar qualquer peso de modelo,
confirmar a licença específica do arquivo (o licenciamento do repositório pode
não cobrir os pesos).

## Regras

- Nada de nomes de estúdios, franquias, personagens ou logotipos em prompts,
  textos ou presets.
- Músicas e vozes de terceiros só com licença comprovada.
- Downloads do YouTube só com confirmação de direitos por vídeo.
- Nenhuma chamada a API de geração ou serviço pago.
- Modelo sem licença registrada aqui não é baixado nem usado.

## Programas e bibliotecas

| Componente | Versão / caminho | Licença | Evidência | Situação |
|---|---|---|---|---|
| Windows 11 Home | 10.0.26100 | Proprietária (EULA Microsoft) | Sistema instalado | Uso local; não redistribuir |
| Driver NVIDIA | 581.57 | Proprietária NVIDIA | `nvidia-smi` | Uso local |
| ComfyUI | 0.18.5 em `D:\Comfy\ComfyUI` | GPL-3.0 | `LICENSE` do repositório local | Ferramenta local; se distribuída modificada, obrigações GPL |
| PyTorch | 2.6.0+cu126 | BSD-3-Clause | Metadados do pacote no venv do ComfyUI | Uso local |
| CUDA / cuDNN | 12.6 | Proprietária NVIDIA | `torch.version.cuda`, `cudnn.version()` | Uso local |
| EffectCraft | 0.24.1 em `D:\CRAFT\EffectCraft` | MIT OR Apache-2.0 | `NOTICE` local | Uso opcional em piloto; marca ArtCraft não é open source |
| FFmpeg | 8.1-full_build (Gyan) em `tools/ffmpeg` | GPLv3 | `ffmpeg -buildconf`: `--enable-gpl --enable-version3 --enable-libx264` | Uso local; distribuição com o binário exige cumprir GPL |
| Python | 3.12.9 | PSF-2.0 | Instalação oficial | Uso local |
| Node.js | 24.14.0 | MIT | Instalação oficial | Uso local |
| Git | 2.53.0 | GPL-2.0 | Instalação oficial | Uso local |
| stick-film (motor local) | `D:\PROJETOS-IA\stick-film\stick-film` | Sem arquivo de licença encontrado | Inspeção da pasta | Projeto do usuário; tratar como proprietário; não redistribuir |
| Remotion | Não instalado | Free License para indivíduos e empresas de até 3 pessoas; licença empresarial acima disso | https://www.remotion.dev/license | Uso declarado: pessoal/educacional; revalidar antes de uso comercial |
| Playwright / Chrome | Não confirmado | Playwright Apache-2.0; Chrome proprietário | A confirmar na instalação | Necessário ao motor stick-film |
| yt-dlp | Não instalado | Unlicense (domínio público) | A confirmar na instalação | Entrada YouTube com direitos confirmados |

## Modelos já instalados no ComfyUI

| Modelo | Arquivo | Licença | Evidência | Situação |
|---|---|---|---|---|
| Stable Diffusion 1.5 | `checkpoints\v1-5-pruned-emaonly.ckpt` | CreativeML OpenRAIL-M | Card oficial `runwayml/stable-diffusion-v1-5` | Permitido com restrições de uso do OpenRAIL-M |
| DreamShaper 8 | `checkpoints\dreamshaper_8.safetensors` | `other` (não detalhada no card HF) | Metadados do card `Lykon/DreamShaper` | **Não usar** até confirmar a licença no card/Civitai do autor |
| AnimateDiff | `animatediff_models\mm_sd_v15_v2.ckpt` | Apache-2.0 (repositório) | `LICENSE.txt` do AnimateDiff | Confirmar card do peso antes do uso |
| IP-Adapter SD1.5 | `ipadapter\ip-adapter_sd15.safetensors` | Apache-2.0 (repositório) | `LICENSE` do IP-Adapter | Confirmar card do peso antes do uso |
| IP-Adapter Plus SD1.5 | `ipadapter\ip-adapter-plus_sd15.safetensors` | Apache-2.0 (repositório) | `LICENSE` do IP-Adapter | Confirmar card do peso antes do uso |
| FLUX.1-schnell fp8 | `diffusion_models\flux1-schnell-fp8-e4m3fn.safetensors` | Apache-2.0 (repositório BFL) | `LICENSE` do repositório `black-forest-labs/flux` | Fora do pipeline padrão; 11,3 GB e pesado para 6 GB de VRAM; confirmar card do peso |
| CLIP ViT-H-14 laion2B | `clip_vision\CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | MIT | Card HF `laion/CLIP-ViT-H-14-laion2B-s32B-b79K` | Suporte ao IP-Adapter |

Não há ControlNet, LCM-LoRA, modelos de segmentação, profundidade, pose ou fala
instalados no ComfyUI no momento desta verificação.

## Modelos planejados (sujeitos a confirmação antes do download)

| Modelo / biblioteca | Licença verificada | Fonte | Observação |
|---|---|---|---|
| rembg | MIT | `LICENSE.txt` do repositório | Código MIT; pesos do U2Net têm licença própria |
| U2-Net | Apache-2.0 | `LICENSE` do repositório | Confirmar o peso usado |
| Depth Anything V2 Small | Apache-2.0 | `LICENSE` do repositório | Confirmar o card do peso |
| LaMa (preenchimento de fundo) | Apache-2.0 | `LICENSE` do repositório | Confirmar o card do peso |
| YOLOv8n-pose | **AGPL-3.0** | `LICENSE` do Ultralytics | Restrição forte: uso em rede/distribuição exige revisão; para uso pessoal local, avaliar |
| MediaPipe | Apache-2.0 | `LICENSE` do repositório | Pose de uma pessoa |
| faster-whisper | MIT | `LICENSE` do repositório | Transcrição local int8 |
| Whisper (pesos) | MIT | Repositório OpenAI | Confirmar o card do peso |
| Rhubarb Lip Sync | MIT | `LICENSE.md` do repositório | Formas de boca |
| RIFE | MIT | `LICENSE` do repositório | Interpolação |
| ControlNet | Apache-2.0 (repositório) | `LICENSE` do repositório | Pesos específicos variam; confirmar cada um |
| LCM-LoRA | MIT (repositório) | `LICENSE` do repositório | Confirmar o card do peso |
| AnimateDiff | Apache-2.0 (repositório) | `LICENSE.txt` do repositório | Confirmar o card do peso |
| IP-Adapter | Apache-2.0 (repositório) | `LICENSE` do repositório | Confirmar o card do peso |

## Restrições que precisam de atenção

1. **YOLOv8n-pose (AGPL-3.0)**: qualquer distribuição do estúdio ou oferta como
   serviço de rede pode acionar obrigações de liberar o código sob AGPL. Para uso
   pessoal/educacional local, o risco é menor, mas deve ser reavaliado antes de
   uso comercial. Alternativa a considerar: MediaPipe para uma pessoa e um
   detector de pose multi-pessoa com licença permissiva.
2. **OpenRAIL-M (SD 1.5)**: exige que o uso respeite as restrições do modelo
   (não gerar conteúdo ilegal, abusivo, de desinformação etc.). O estúdio já
   bloqueia conteúdo impróprio, mas a obrigação deve constar no receipt.
3. **DreamShaper 8**: licença `other` sem detalhe no card; não usar até
   confirmação. O estilo cartoon pode usar apenas SD 1.5 ou outro peso aprovado.
4. **FFmpeg GPLv3**: o binário está no projeto para uso local. Se o app for
   distribuído, é preciso cumprir a GPL ou distribuir o FFmpeg separadamente.
5. **Remotion**: a Free License vale para indivíduos e empresas de até três
   pessoas. O uso declarado é pessoal/educacional; qualquer monetização ou uso
   empresarial precisa de revalidação.
6. **stick-film**: não há licença declarada. É um projeto do usuário; não será
   redistribuído nem incorporado a um pacote público sem decisão explícita.
7. **Marcas**: "LEGO" não aparece na interface; o estilo é exibido como
   "Mosaico de blocos". Nomes de estúdios, franquias e personagens são proibidos
   em prompts e textos.
