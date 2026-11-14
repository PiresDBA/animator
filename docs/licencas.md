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
| Craft Voice / Piper | Local em `D:\CRAFT\VoiceCraft` | A confirmar na instalação | D021; golden set usou provider `piper` | Voz local `pt_BR-faber-medium`; não usar provedores cloud |

## Dependências Python do M1

Versões exatas em `requirements.txt`. A instalação usa `--no-deps` e
`opencv-python-headless`; por isso o `pip check` pode listar dependências
opcionais ausentes (ver `docs/limitacoes.md`).

| Componente | Versão | Licença | Evidência | Situação |
|---|---|---|---|---|
| PyTorch | 2.6.0+cu126 | BSD-3-Clause | Metadados do pacote no `.venv` | Uso local; CUDA 12.6 |
| torchvision | 0.21.0+cu126 | BSD-3-Clause | Metadados do pacote no `.venv` | Uso local |
| Transformers | 4.49.0 | Apache-2.0 | Metadados do pacote no `.venv` | Pipeline de profundidade |
| Ultralytics | 8.4.212 | **AGPL-3.0** | Metadados do pacote | Uso pessoal/educacional; ver D018 |
| ultralytics-thop | 2.2.5 | AGPL-3.0 | Metadados do pacote | Dependência do Ultralytics |
| faster-whisper | 1.2.1 | MIT | Metadados do pacote | Transcrição local |
| CTranslate2 | 4.9.0 | MIT | Metadados do pacote | Backend do faster-whisper |
| PyAV (`av`) | 15.1.0 | BSD-3-Clause | Metadados do pacote | Fixado por D022 |
| rembg | 2.0.87 | MIT | Metadados do pacote | Código MIT; pesos U2Net à parte |
| onnxruntime | 1.32.0 | MIT | Metadados do pacote | Backend do rembg |
| PySceneDetect | 0.7.3 | BSD-3-Clause | Metadados do pacote | Detecção de cenas |
| OpenCV headless | 5.0.0.93 | Apache-2.0 | Metadados do pacote | Substitui `opencv-python` |
| NumPy | 2.5.4 | BSD-3-Clause | Metadados do pacote | Base numérica |
| Pillow | 13.0.0 | HPND | Metadados do pacote | Imagens |
| jsonschema | 4.26.0 | MIT | Metadados do pacote | Validação do schema v1 |
| huggingface_hub | 0.36.2 | Apache-2.0 | Metadados do pacote | Download de modelos |
| tokenizers | 0.21.4 | Apache-2.0 | Metadados do pacote | Tokenização do Whisper |
| safetensors | 0.8.0 | Apache-2.0 | Metadados do pacote | Pesos do Depth Anything |
| SciPy | 1.18.1 | BSD-3-Clause | Metadados do pacote | Dependência transitiva |
| scikit-image | 0.26.0 | BSD-3-Clause | Metadados do pacote | Dependência do rembg |
| Numba | 0.68.1 | BSD-2-Clause | Metadados do pacote | Dependência transitiva |
| Matplotlib | 3.11.2 | Licença Matplotlib (PSF) | Metadados do pacote | Dependência do Ultralytics |
| pandas | 3.1.1 | BSD-3-Clause | Metadados do pacote | Dependência do Ultralytics |
| psutil | 7.2.2 | BSD-3-Clause | Metadados do pacote | Dependência do Ultralytics |
| PyMatting | 1.1.16 | MIT | Metadados do pacote | Dependência do rembg |
| pooch | 1.9.0 | BSD-3-Clause | Metadados do pacote | Dependência do scikit-image |
| tqdm | 4.70.1 | MPL-2.0 AND MIT | Metadados do pacote | Barras de progresso |
| requests | 2.34.2 | Apache-2.0 | Metadados do pacote | HTTP local para downloads |

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
instalados no ComfyUI no momento desta verificação. Os modelos do M1 ficam em
`.cache/`, fora do ComfyUI.

## Modelos baixados no M1

| Modelo | Arquivo / cache | Bytes | SHA256 | Licença | Fonte e situação |
|---|---|---|---|---|---|
| YOLOv8n-pose | `.cache/modelos/yolov8n-pose.pt` | 6.832.633 | `c6fa93dd1ee4a2c18c900a45c1d864a1c6f7aba75d84f91648a30b7fb641d212` | **AGPL-3.0** | Ultralytics; uso pessoal/educacional (D018); não distribuir o peso nem código derivado |
| U2Net (rembg) | `.cache/rembg/models/u2net/u2net.onnx` | 175.997.641 | `8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491` | Apache-2.0 | U2-Net via rembg; peso baixado localmente |
| Depth Anything V2 Small | `.cache/huggingface/hub/models--depth-anything--Depth-Anything-V2-Small-hf/blobs/3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70` (`model.safetensors`) | 99.173.660 | `3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70` | Apache-2.0 | Card `depth-anything/Depth-Anything-V2-Small-hf` |
| faster-whisper small | `.cache/whisper/models--Systran--faster-whisper-small/blobs/3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` (`model.bin`) | 483.546.902 | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` | MIT | Conversão `Systran/faster-whisper-small` dos pesos OpenAI Whisper (MIT) |

Observações:

- Os tamanhos e hashes foram medidos localmente com `Get-FileHash` (SHA256) em
  2026-11-14. O nome do blob do Hugging Face já é o SHA256 do arquivo.
- Os pesos ficam fora do git (`*.pt`, `*.onnx`, `*.safetensors` e `.cache/` são
  ignorados). Este documento é o registro de auditoria.
- O `hf_xet` não está instalado no `.venv`; os downloads continuam funcionando
  pelo método HTTP normal.

## Outros modelos planejados (sujeitos a confirmação antes do download)

| Modelo / biblioteca | Licença verificada | Fonte | Observação |
|---|---|---|---|
| LaMa (preenchimento de fundo) | Apache-2.0 | `LICENSE` do repositório | Confirmar o card do peso |
| MediaPipe | Apache-2.0 | `LICENSE` do repositório | Pose de uma pessoa |
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
8. **Craft Voice/Piper**: a versão e a licença do executável local ainda não
   foram registradas; o uso atual é apenas local, no golden set. Registrar antes
   de distribuir áudios ou o aplicativo (D021).
9. **av 15.1.0**: pin obrigatório enquanto faster-whisper 1.2.1 e CTranslate2
   4.9.0 forem usados; revalidar antes de atualizar (D022).
