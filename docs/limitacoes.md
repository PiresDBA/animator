# Limitações e riscos conhecidos

Atualizado no M1 (2026-11-14). Números abaixo são medições locais; estimativas
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
- **M1 medido** no `.venv` do projeto, com monitor de 0,5 s:
  - clipe 1: 1.018 MB de pico, 67 °C, 80% de utilização, 36,30 s;
  - clipes 2 e 3: 1.502 MB de pico, 73 °C, 100% de utilização, 51,77 s e
    52,01 s.
- **Limitação**: os testes do M0/M1 provam que o sm_61 funciona, mas não são um
  teste térmico sustentado. O pico de 1.502 MB de 6.144 MB não garante folga
  para vídeos longos, difusão ou modelos maiores. O monitor de 0,5 s também
  pode perder picos curtos.
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
  (8855ED62CBFD12E5…). A fonte do projeto foi aprovada em D016.
- Remotion: não instalado dentro do projeto. Há projetos existentes com
  Remotion 4.0.542 e 4.0.484; será criado um projeto local com versão fixada no
  M2.
- VideoFactoryAI: `D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI`.
- yt-dlp ainda não foi instalado. Playwright-core e Chrome existem em
  `C:\Users\Pires\StickFilms\.tools` e `C:\Program Files\Google\Chrome\Application\chrome.exe`;
  o motor ainda não foi executado.

## Modelos

- 7 modelos no ComfyUI, 21.723,2 MB no total:
  SD 1.5, DreamShaper 8, FLUX.1-schnell fp8, AnimateDiff mm_sd_v15_v2,
  IP-Adapter SD1.5, IP-Adapter Plus SD1.5 e CLIP ViT-H-14.
- O M1 baixou e usou, em `.cache/`: YOLOv8n-pose (6,8 MB), U2Net
  (176,0 MB), Depth Anything V2 Small (99,2 MB) e faster-whisper small
  (483,5 MB). Tamanhos e SHA256 estão em `docs/licencas.md`.
- **Ainda faltam** MediaPipe, Rhubarb, RIFE, LaMa, ControlNet, LCM-LoRA e
  modelos de difusão adicionais. Cada download exige confirmação de licença.
- DreamShaper 8 tem licença `other` não detalhada; não será usado até
  confirmação.
- YOLOv8n-pose é AGPL-3.0; o uso é somente pessoal/educacional. Qualquer
  distribuição ou monetização exige reavaliação.
- FLUX.1-schnell tem 11,3 GB e não é o caminho padrão para 6 GB de VRAM.

## Análise de vídeo (M1)

- O YOLOv8n-pose é instável em bonecos geométricos sintéticos. No clipe 1 e no
  clipe 3 (boneco parado/cartela) ele retorna 0 detecções — o pipeline registra
  ausência e não inventa pontos. No clipe 2, detecta 2 pessoas até 5,5 s, 0
  entre 6,0 e 9,0 s e 1 em 9,5 s (confiança 0,429), mesmo com as duas figuras
  visíveis. A confiança oscila perto do limiar de 0,20.
- O Whisper small comete erros no TTS sintético em português: “Este atil símbolo
  de Copyrighto 3º Clip.” e “Atiolisa local comete o parágrafo agora”. Isso é
  texto de entrada, não uma transcrição perfeita; a prévia final precisa de
  correção humana antes de legendar.
- O limiar de cena 27,0 e `min_cena_frames=15` funcionaram nos 3 clipes
  sintéticos. Vídeos reais com transições suaves, granulação ou movimento de
  câmera precisam de reajuste e validação.
- Profundidade e máscaras são descritivas neste marco; ainda não são usadas para
  recortar, compor ou fazer parallax. A qualidade em vídeo real não foi medida.
- A primeira execução do rembg tem custo de importação/criação de sessão de
  ~58 s (clipe 1: 102,22 s). Com o cache quente, o mesmo clipe levou 36,30 s.
- `pip check` acusa `opencv-python`, `nvidia-ml-py`, `polars` e
  `ultralytics-platform` ausentes porque a instalação usa `--no-deps` e
  `opencv-python-headless`. O pipeline funciona; não instalar `opencv-python`
  junto com o headless.
- O aviso de `hf_xet` (“Xet Storage ... not installed”) é esperado; o download
  HTTP normal funciona. Não instalar `hf_xet` no Docling/global.
- O pipeline materializa todos os quadros amostrados em memória antes de
  analisar. A 2 fps, um vídeo longo pode consumir vários GB de RAM; o golden set
  tem só 20 quadros por clipe. Antes de vídeos reais, reduzir `--fps-amostra` ou
  refatorar para processamento em streaming.
- O `probe` calcula SHA256 do arquivo inteiro a cada execução; isso adiciona I/O
  proporcional ao tamanho do vídeo.
- O golden set é sintético; nenhum vídeo real, com pessoas, fala ou ruído, foi
  analisado ainda. Os números de pose/fala não devem ser generalizados.

## Ambiente Windows

- O `python` do PATH é o venv do Docling; para o projeto usar `py -3.12` ou o
  caminho absoluto do Python 3.12.9. O `pipeline` deve ser executado com
  `.\.venv\Scripts\python.exe`.
- Caches de modelos e pip ficam em `.cache/` no D:; o
  `C:\Users\Pires\AppData\Roaming\Ultralytics\settings.json` foi criado pelo
  Ultralytics fora do projeto e não é removido automaticamente.
- Caminhos longos e suporte a Unicode: o projeto usa `pathlib`, mas o suporte a
  caminhos >260 caracteres do Windows não foi habilitado (exige mudança de
  registro). Evitar caminhos muito longos.
- Antivírus: nenhuma exclusão foi aplicada. Se a varredura/geração ficar lenta,
  o usuário pode excluir `D:\PROJETOS-IA\animacao\estudio` manualmente.
- `multiprocessing` deve usar `if __name__ == "__main__"` em todos os scripts.

## Escopo ainda não implementado

- O M1 cobre análise de vídeo e golden set; nenhuma prévia animada, render
  Remotion ou vídeo completo foi produzido.
- Interface gráfica, backend FastAPI, fila SQLite, portão de aprovação e testes
  de flashes/volume/conteúdo entram do M2 em diante.
- O motor de bonecos ainda não foi executado; Playwright/Chrome não foram
  verificados em um render real.
- EffectCraft não foi testado como piloto.
- Não há medição de tempo de render Remotion, FFmpeg em vídeo real, leitura/
  escrita do disco de projetos nem benchmark de difusão. O planejador não pode
  prometer prazos até esses números existirem.

## Riscos de licença e direitos

- Remotion: uso pessoal/educacional declarado; revalidar antes de monetizar.
- FFmpeg GPLv3 e ComfyUI GPL-3.0: obrigações se houver distribuição.
- Craft Voice/Piper: versão e licença local ainda não foram registradas; a voz
  `pt_BR-faber-medium` é usada apenas localmente no golden set (D021).
- `av==15.1.0` e o conjunto CTranslate2/faster-whisper não devem ser atualizados
  sem revalidar a transcrição; ver D022.
- Pesos de modelos podem ter licença diferente do repositório; confirmar antes
  de baixar/usar.
- YouTube: cada download exige confirmação de direitos; nada de nuvem.
- Nomes protegidos: "LEGO" só aparece em identificadores internos do contrato;
  a interface usa "Mosaico de blocos".
