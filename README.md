# Estúdio de Animação Local

Estúdio local para transformar um vídeo (arquivo local, YouTube com direitos
confirmados ou projeto da VideoFactoryAI) em versões animadas para crianças de
7 a 10 anos, com prévia obrigatória e aprovação humana antes de qualquer vídeo
completo.

## Estado atual: M0 aprovado; M1 concluído tecnicamente, aguardando aprovação

- Estrutura do projeto criada.
- Descoberta de hardware, programas e modelos implementada (somente leitura) e
  tabela confirmada pelo usuário.
- Teste real de GPU implementado.
- Licenças levantadas em `docs/licencas.md` e atualizadas com os modelos do M1.
- M1: análise de vídeo concluída no golden set sintético de 3 clipes de 10 s;
  3 JSONs validados, 23 testes OK e prévias em `docs/evidencias/m1/`.
- Dependências fixadas em `requirements.txt`; modelos e caches em `.cache/`.
- Nenhuma geração de vídeo foi executada ainda.
- A interface gráfica entra a partir do M2; `iniciar.bat` ainda é um painel de
  diagnóstico, não o app final.

## Regras do projeto

1. Segurança infantil antes de tudo.
2. Nenhum vídeo completo sem aprovação explícita do usuário.
3. 100% local: sem APIs de geração, sem serviços pagos, sem envio de dados.
4. Nada de nomes de estúdios, franquias ou personagens protegidos na interface.
5. Entrada do YouTube somente com confirmação de direitos por vídeo.
6. Técnica não verificada na máquina é marcada como experimental.

## Estrutura

```
estudio/
  backend/          FastAPI, websocket, fila SQLite, serviços (a partir do M1)
  frontend/         React + Vite + TypeScript + Tailwind (a partir do M2)
  descoberta/       hardware.py, programas.py, varredura.py, modelos.py, teste_gpu.py
  pipeline/         análise do M1: vídeo, cenas, movimento, profundidade,
                    máscaras, pose, fala, schema e CLI
  tecnicas/         rig, parallax, mosaico, contornos, toon3d, bonecos, difusão
  estilos/          presets dos cinco estilos
  remotion/         composições de cena (a partir do M2)
  comfy/            workflows de difusão (opcional, condicionado ao benchmark)
  projetos/         um diretório por projeto, com JSONs versionados
  saidas/           MP4s, miniaturas e recibos
  tests/            testes unitários, de segurança, de interface e golden set
  tools/ffmpeg/     FFmpeg 8.1 local (GPLv3; binários fora do git)
  .cache/           modelos e caches locais (fora do git)
  docs/             decisões, progresso, licenças, limitações e evidências
```

## Comandos de M0

```powershell
# Perfil de hardware (grava perfil_hardware.json)
py -3.12 descoberta\hardware.py --salvar

# Descoberta de programas (somente leitura; salva após confirmar a tabela)
py -3.12 descoberta\programas.py --max-seconds 180 --salvar --confirmado

# Inventário de modelos do ComfyUI
py -3.12 descoberta\modelos.py --comfyui "D:\Comfy\ComfyUI" --salvar

# Teste real de GPU usando o PyTorch do ComfyUI
& "D:\Comfy\ComfyUI\venv\Scripts\python.exe" descoberta\teste_gpu.py --salvar

# Testes da descoberta
py -3.12 -m unittest discover -s tests -v
```

## Comandos do M1

```powershell
# Criar o ambiente e instalar as versões fixadas (torch cu126 + av 15.1.0)
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: --no-deps -r requirements.txt

# Analisar um clipe do golden set
.\.venv\Scripts\python.exe -m pipeline.analisar `
  --video tests\golden\clipe_02_acao.mp4 `
  --saida docs\evidencias\m1\clipe_02_acao.json `
  --previa-dir docs\evidencias\m1\previa_clipe_02

# Etapas individuais podem ser desativadas para testes rápidos
.\.venv\Scripts\python.exe -m pipeline.analisar --video tests\golden\clipe_01_estatico.mp4 `
  --sem-profundidade --sem-mascara --sem-pose --sem-fala --sem-previas

# Testes unitários (descoberta + análise)
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

O CLI grava um JSON validado pelo schema `pipeline/schemas/analise_v1.json` e
prévias de profundidade, máscara e pose. Por padrão usa CUDA se disponível,
`fps_amostra=2.0`, `limiar_cena=27.0` e faster-whisper `small` em português.

## Hardware de referência

- Windows 11, i7-7700HQ (4C/8T), 32 GB RAM.
- NVIDIA GTX 1060 6 GB (Pascal, sm_61), driver 581.57.
- ComfyUI com PyTorch 2.6.0+cu126.
- Disco D: com espaço; C: tem pouco espaço livre.

## Marco atual

M1 concluído tecnicamente: análise de vídeo (cenas, movimento, profundidade,
máscaras, pose e fala) com schema validado no golden set de 3 clipes de 10 s.
O ambiente Python fica em `.venv` e os modelos em `.cache/`; falta a aprovação
humana para iniciar o M2 (primeira prévia vertical com o motor de bonecos).
