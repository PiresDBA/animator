# Limitações e riscos conhecidos

Atualizado no M0 (2026-11-14). Números abaixo são medições locais; estimativas
são rotuladas como tal.

## Hardware medido

- Windows 11 Home Single Language, build 26100, 64 bits.
- Acer Predator G3-572, Intel i7-7700HQ (4 núcleos, 8 threads), 31,89 GB de RAM.
- NVIDIA GTX 1060 6 GB, driver 581.57, capacidade sm_61 (Pascal), 10 SMs.
- Em repouso: 53–55 °C, 4,1–4,4 W, 0% de utilização, ~393–425 MiB de VRAM usada.
- Discos: C: 37,2 GB livres de 446 GB; D: 819,2 GB livres de 1.861,9 GB.

## GPU

- PyTorch 2.6.0+cu126, CUDA 12.6, cuDNN 9.5.1, no venv do ComfyUI.
- Teste real: matmul 4096×4096 float32 em 45,0 ms (mediana de 3); convolução
  64×32×3×3 sobre 512×512 em 2,49 ms (mediana; a primeira execução levou
  112,4 ms por causa do autotune do cuDNN).
- Pico de VRAM alocada pelo PyTorch: 235,1 MiB; reservada: 280,0 MiB.
- `nvidia-smi` durante o teste: 55 °C, 63,9 W, 692 MiB usados, 17% de utilização,
  com **1 amostra** (teste curto de 4,98 s).
- **Limitação**: esse teste prova que o sm_61 funciona, mas não é um teste
  térmico sustentado. A temperatura e a potência de carga contínua só serão
  conhecidas no benchmark do M1/M2. O monitor de 0,25 s coletou apenas 1 amostra
  porque o workload terminou em menos de 1 s.
- Risco de TDR em kernels longos; o pipeline deve dividir o trabalho em lotes e
  medir cada lote.

## Programas descobertos

- ComfyUI 0.18.5 em `D:\Comfy\ComfyUI` (GPL-3.0).
- EffectCraft 0.24.1 em `D:\CRAFT\EffectCraft` (MIT OR Apache-2.0).
- FFmpeg 8.1 full em `tools/ffmpeg` (GPLv3); teste de fumaça gerou MP4 H.264 +
  AAC de 1,0 s. O FFmpeg **não está no PATH**; o projeto usa a cópia local.
- Motor de bonecos: cinco cópias encontradas. Quatro têm o mesmo
  `engine/render.mjs` (hash 958691540FA4EFBD…); a cópia em
  `D:\PROJETOS-IA\stick-film\stick-film` tem `render.mjs` diferente
  (8855ED62CBFD12E5…). **Escolha pendente de aprovação.**
- Remotion: não instalado dentro do projeto. Há projetos existentes com
  Remotion 4.0.542 e 4.0.484; será criado um projeto local com versão fixada.
- VideoFactoryAI: `D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI`.
- yt-dlp ainda não foi instalado. Playwright-core e Chrome existem em
  `C:\Users\Pires\StickFilms\.tools` e `C:\Program Files\Google\Chrome\Application\chrome.exe`;
  o motor ainda não foi executado.

## Modelos

- 7 modelos no ComfyUI, 21.723,2 MB no total:
  SD 1.5, DreamShaper 8, FLUX.1-schnell fp8, AnimateDiff mm_sd_v15_v2,
  IP-Adapter SD1.5, IP-Adapter Plus SD1.5 e CLIP ViT-H-14.
- **Faltam** ControlNet, LCM-LoRA, segmentação (rembg/U2Net), profundidade
  (Depth Anything V2), pose (YOLOv8n-pose/MediaPipe), fala (faster-whisper/
  Rhubarb) e RIFE. Esses downloads dependem de confirmação de licença.
- DreamShaper 8 tem licença `other` não detalhada; não será usado até
  confirmação.
- YOLOv8n-pose é AGPL-3.0; o uso precisa ser reavaliado antes de qualquer
  distribuição ou monetização.
- FLUX.1-schnell tem 11,3 GB e não é o caminho padrão para 6 GB de VRAM.

## Ambiente Windows

- O `python` do PATH é o venv do Docling; para o projeto usar `py -3.12` ou o
  caminho absoluto do Python 3.12.9.
- Caminhos longos e suporte a Unicode: o projeto usa `pathlib`, mas o suporte a
  caminhos >260 caracteres do Windows não foi habilitado (exige mudança de
  registro). Evitar caminhos muito longos até o M1.
- Antivírus: nenhuma exclusão foi aplicada. Se a varredura/geração ficar lenta,
  o usuário pode excluir `D:\PROJETOS-IA\animacao\estudio` manualmente.
- `multiprocessing` deve usar `if __name__ == "__main__"` em todos os scripts.

## Escopo ainda não implementado

- Nenhuma análise de vídeo, prévia ou render foi executada; o M0 é só
  descoberta e validação de ambiente.
- Interface gráfica, backend FastAPI, fila SQLite, portão de aprovação, testes
  de flashes/volume/conteúdo e golden set entram nos próximos marcos.
- O motor de bonecos não foi executado; Playwright/Chrome ainda não foram
  verificados.
- EffectCraft não foi testado como piloto.
- Não há medição de tempo de render Remotion, FFmpeg em vídeo real, leitura/
  escrita do disco de projetos nem benchmark de difusão. O planejador não pode
  prometer prazos até esses números existirem.

## Riscos de licença e direitos

- Remotion: uso pessoal/educacional declarado; revalidar antes de monetizar.
- FFmpeg GPLv3 e ComfyUI GPL-3.0: obrigações se houver distribuição.
- Pesos de modelos podem ter licença diferente do repositório; confirmar antes
  de baixar/usar.
- YouTube: cada download exige confirmação de direitos; nada de nuvem.
- Nomes protegidos: "LEGO" só aparece em identificadores internos do contrato;
  a interface usa "Mosaico de blocos".
