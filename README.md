# Estúdio de Animação Local

Estúdio local para transformar um vídeo (arquivo local, YouTube com direitos
confirmados ou projeto da VideoFactoryAI) em versões animadas para crianças de
7 a 10 anos, com prévia obrigatória e aprovação humana antes de qualquer vídeo
completo.

## Estado atual: M0

- Estrutura do projeto criada.
- Descoberta de hardware, programas e modelos implementada (somente leitura).
- Teste real de GPU implementado.
- Licenças levantadas em `docs/licencas.md`.
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
  pipeline/         etapas de ingestão, análise, prévia e composição
  tecnicas/         rig, parallax, mosaico, contornos, toon3d, bonecos, difusão
  estilos/          presets dos cinco estilos
  remotion/         composições de cena (a partir do M2)
  comfy/            workflows de difusão (opcional, condicionado ao benchmark)
  projetos/         um diretório por projeto, com JSONs versionados
  saidas/           MP4s, miniaturas e recibos
  tests/            testes unitários, de segurança, de interface e golden set
  tools/ffmpeg/     FFmpeg 8.1 local (GPLv3; binários fora do git)
  docs/             decisões, progresso, licenças, limitações
```

## Comandos de M0

```powershell
# Perfil de hardware (grava perfil_hardware.json)
py -3.12 descoberta\hardware.py --salvar

# Descoberta de programas (somente leitura; --salvar após confirmar a tabela)
py -3.12 descoberta\programas.py --max-seconds 180

# Inventário de modelos do ComfyUI
py -3.12 descoberta\modelos.py --comfyui "D:\Comfy\ComfyUI" --salvar

# Teste real de GPU usando o PyTorch do ComfyUI
& "D:\Comfy\ComfyUI\venv\Scripts\python.exe" descoberta\teste_gpu.py --salvar

# Testes da descoberta
py -3.12 -m unittest discover -s tests -v
```

## Hardware de referência

- Windows 11, i7-7700HQ (4C/8T), 32 GB RAM.
- NVIDIA GTX 1060 6 GB (Pascal, sm_61), driver 581.57.
- ComfyUI com PyTorch 2.6.0+cu126.
- Disco D: com espaço; C: tem pouco espaço livre.

## Próximo marco

M1: análise de vídeo (cenas, movimento, profundidade, máscaras, pose e fala)
com schema validado, usando o golden set de 3 clipes de 10 s.
