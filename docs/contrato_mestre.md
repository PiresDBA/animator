# Contrato do projeto

Data de referência: 2026-11-14.
Versão inicial deste consolidação: 1.0.0.

Este documento é a referência primária do projeto. Ele existe para que qualquer
inteligência que continue o trabalho saiba, de forma explícita:

- o que o projeto é,
- o que foi feito até agora,
- o que foi testado,
- quais ferramentas estão em uso,
- quais modelos foram baixados,
- quais vídeos de referência existem,
- onde o trabalho parou,
- e o que ainda precisa ser entregue.

Não adianta fazer algo novo se o contrato não disser isso. Não adianta reinventar
nada se o que já existe puder ser reaproveitado.

## 1. O que é esse projeto

Este é um estúdio local de animação para vídeos infantis.

O trabalho central não é gerar um monte de prévias dispersas, nem montar um estúdio
genérico. O trabalho central é pegar vídeos que são basicamente sequências de imagens
estáticas, com narração e história já prontas, e animar o que tem nessa cena, de forma
que os personagens, brinquedos e elementos ganhem vida dentro de si mesmos, mantendo
o ritmo e o áudio originais.

Para este projeto, o que importa é:

- entrada: vídeos com imagens estáticas, narração e histórias já montados;
- saída: vídeos com animação real dentro da própria cena;
- estilo desejado: visual bonito para criança, com personagens se movendo;
- limite real: a máquina não entrega tudo, então o caminho tem que ser viável localmente;
- regra de ouro: não recriar o que já existe no projeto.

O ponto de partida prático é:

- “O Parque dos Pets.mp4”
- “Fridóca e Luninha no Carnaval Carioca.mp4”
- “O Banquete Canino do Restaurante dos Cães.mp4”

Esses três vídeos foram passados como referência e estão na raiz do projeto.

Os primeiros 10 segundos de “O Parque dos Pets.mp4” foram usados como primeiro
bloco de trabalho e análise.

## 2. O que já existe pronto no sistema

O projeto já tem muita coisa pronta e documentada. O que existe agora é:

### 2.1 Estrutura do repositório

A raiz do trabalho é:

- `D:\PROJETOS-IA\animacao\estudio`

Dentro dele, a estrutura principal é:

- `backend/` — FastAPI, fila SQLite, serviços de projeto, avaliações, prévia, hardware e eventos.
- `frontend/` — interface web em React + Vite + TypeScript + Tailwind + Recharts.
- `pipeline/` — análise, cenas, movimento, profundidade, máscaras, pose, fala,
  roteamento, renderização, montagem, segurança e validação.
- `tecnicas/` — estilos procedurais prontos: anime, cartoon, lego e 3d.
- `remotion/` — projeto Remotion local com composições e renderização.
- `comfy/` — estrutura pronta para fluxos de difusão via ComfyUI.
- `descoberta/` — inventário de hardware, programas e modelos.
- `docs/` — decisões, licenças, limitações, progresso, contratos e evidências.
- `tests/` — testes unitários e de marcos.
- `tools/ffmpeg/` — FFmpeg e FFprobe locais.
- `.venv/` — ambiente Python do projeto.
- `.cache/` — modelos e caches locais.
- `projetos/` — projetos de trabalho com layout definido.
- `saidas/` — saídas de prévias, miniaturas e recibos.
- `tests/golden/` — conjunto de referência sintética.

### 2.2 Backend

O backend é um FastAPI na porta 8765, com:

- estado geral do sistema;
- criação e consulta de projetos;
- fila de jobs com persistência em SQLite;
- endpoints de análise, prévia e avaliações;
- endpoint de vídeo completo com bloqueio explícito quando não há aprovação;
- WebSocket de eventos;
- serviço de hardware e programas.

O arquivo principal é:

- `backend/app.py`

Os serviços são:

- `backend/servicos/fila.py`
- `backend/servicos/projetos.py`
- `backend/servicos/avaliacoes.py`
- `backend/servicos/hardware.py`
- `backend/servicos/previa.py`
- `backend/servicos/eventos.py`
- `backend/servicos/caminhos.py`

O banco de fila é:

- `backend/fila.sqlite3`

### 2.3 Pipeline

O pipeline já tem os módulos principais prontos:

- `pipeline/analisar.py`
- `pipeline/video.py`
- `pipeline/cenas.py`
- `pipeline/movimento.py`
- `pipeline/profundidade.py`
- `pipeline/mascaras.py`
- `pipeline/pose.py`
- `pipeline/fala.py`
- `pipeline/medidas.py`
- `pipeline/cache.py`
- `pipeline/validar.py`
- `pipeline/seguranca.py`
- `pipeline/roteador.py`
- `pipeline/tracking.py`
- `pipeline/previa.py`
- `pipeline/completo.py`
- `pipeline/render_stick.py`
- `pipeline/render_procedural.py`
- `pipeline/render_comfy.py`
- `pipeline/render_esqueleto.py`
- `pipeline/schemas/`

O pipeline já suporta:

- análise de vídeo com extração de quadros e amostragem;
- separação de cenas;
- movimento, profundidade, máscaras, pose e fala como etapas separadas;
- validação de JSON com schema versão 1;
- checagem de segurança infantil;
- roteamento de técnica por cena;
- renderização e montagem de prévias;
- geração de vídeo completo com receipt e portão de aprovação.

O schema principal é:

- `pipeline/schemas/analise_v1.json`

O esquema é validado com `jsonschema` Draft 2020-12.

### 2.4 Técnicas

As técnicas procedurais prontas são:

- `tecnicas/anime.py`
- `tecnicas/cartoon.py`
- `tecnicas/lego.py`
- `tecnicas/tres_d.py`

Essas técnicas já foram implementadas e são usadas pelo renderizador procedural.

### 2.5 Remotion

O Remotion está pronto em:

- `remotion/`

Ele usa as versões fixadas:

- `remotion` 4.0.542
- `@remotion/cli` 4.0.542
- `@remotion/renderer` 4.0.542
- `react` 18.3.1
- `react-dom` 18.3.1
- `typescript` 5.6.3

As composições prontas são:

- `remotion/src/Previa.tsx`
- `remotion/src/Miniatura.tsx`
- `remotion/src/Root.tsx`
- `remotion/src/fontes.ts`
- `remotion/src/index.ts`

O Remotion já gerou:

- `remotion/out/teste_previa.mp4`
- `remotion/out/miniatura.png`
- `remotion/out/previa_vazio.png`

Os scripts disponíveis são:

- `npm run dev`
- `npm run typecheck`
- `npm run still`
- `npm run render`

O arquivo de config do Remotion é:

- `remotion/remotion.config.ts`

Ele define:

- formato JPEG;
- sobrescrita ativa;
- codec H.264;
- renderer Chromium OpenGL Angle.

### 2.6 ComfyUI

A estrutura do ComfyUI já está preparada em:

- `comfy/`

Com a pasta de fluxos:

- `comfy/workflows/`

O CamfyUI instalado como ferramenta externa tem:

- `D:\Comfy\ComfyUI`

Ele tem PyTorch 2.6.0+cu126 e os modelos registrados nele foram inventariados.

### 2.7 Estilos

Os estilos do projeto são:

- `estilos/3d.json`
- `estilos/anime.json`
- `estilos/bonecos.json`
- `estilos/cartoon.json`
- `estilos/lego.json`

Os nomes de exibição são genéricos, sem marcas protegidas.

### 2.8 Frontend

A interface web está pronta em:

- `frontend/`

Ela usa:

- React 18
- React DOM 18
- React Router DOM 6.26.2
- Recharts 2.12.7
- Lucide React 0.441.0
- Tailwind CSS 3.4.13
- Vite 5.4.10
- TypeScript 5.6.3

O build já foi feito e está em:

- `frontend/dist/`

O frontend serve páginas como:

- início,
- novo vídeo,
- prévias e avaliação,
- vídeos completos,
- projetos,
- hardware,
- programas,
- fila,
- configurações,
- ajuda.

### 2.9 Configurações principais

O arquivo:

- `config.json`

já registra:

- entrada principal,
- público,
- estilos iniciais,
- orçamento,
- padrões de trabalho,
- descoberta confirmada,
- caminhos dos programas,
- situação de nuvem,
- fase atual do agente.

O perfil de hardware está em:

- `perfil_hardware.json`

### 2.10 Documentação já existe

Já existem:

- `README.md`
- `docs/decisoes.md`
- `docs/licencas.md`
- `docs/limitacoes.md`
- `docs/contrato_m2.md`
- `docs/progresso.md`
- `docs/evidencias/`

## 3. O que já foi feito

O que já foi feito até agora, de forma consolidada:

- estrutura do projeto criada;
- descoberta de hardware, programas e modelos feita e confirmada;
- teste real de GPU feito;
- licenças levantadas e registradas;
- pipeline de análise feito e validado;
- conjunto de referência sintético criado;
- análise executada nos clipes de referência;
- modelos baixados para o pipeline de análise;
- backend com fila e serviços implementados;
- frontend com React + Tailwind + Recharts implementado;
- Remotion local com composições prontas;
- técnicas procedurais implementadas;
- testes organizados por marco;
- documentação de decisões, licenças e limitações feita;
- vídeos de referência copiados para a raiz do projeto;
- primeiro bloco de trabalho extraído do “O Parque dos Pets.mp4”.

## 4. O que já foi testado

Os testes que já estão no projeto cobrem:

- descoberta de programas;
- varredura somente leitura;
- schema de análise;
- extração de quadros e amostragem;
- detecção de cenas;
- roteamento de técnica;
- avaliações e contrato de avaliação;
- portão de vídeo completo;
- retomada de fila;
- segurança infantil;
- volume e flashes;
- técnicas procedurais;
- backend e estado do sistema.

Os arquivos de teste são:

- `tests/test_descoberta.py`
- `tests/test_analise.py`
- `tests/test_m2.py`
- `tests/test_m3.py`
- `tests/test_m4.py`
- `tests/modelos_smoke.py`

O conjunto de referência é:

- `tests/golden/`

As evidências já geradas estão em:

- `docs/evidencias/`
- `docs/evidencias/m1/`

O trabalho de análise de vídeo já teve JSONs validados e prévias geradas para o
conjunto de referência.

## 5. Ferramentas que já estão sendo usadas

As ferramentas que já estão em uso ou já foram detectadas como disponíveis são:

- FFmpeg local em `tools/ffmpeg/`
- Python 3.12 no projeto
- Node.js 24.14.0
- npm 11.9.0
- git
- nvidia-smi para monitor de GPU
- Remotion local com CLI 4.0.542
- ComfyUI instalado em `D:\Comfy\ComfyUI`
- PyTorch 2.6.0+cu126 no venv do ComfyUI
- stick-film como motor de bonecos
- VideoFactoryAI presente em `D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI`
- EffectCraft presente em `D:\CRAFT\EffectCraft`

O inventário consolidado está em:

- `descoberta/resultado_varredura.json`
- `descoberta/modelos_encontrados.json`
- `perfil_hardware.json`

### 5.1 Ferramentas do sistema detectadas

O sistema detectou entre outros:

- ComfyUI em `D:\Comfy\ComfyUI`
- FFmpeg em vários caminhos, com o local em `tools/ffmpeg`
- motor de bonecos em `D:\PROJETOS-IA\stick-film\stick-film`
- Remotion em `estudio/remotion` e em outros projetos externos
- EffectCraft em `D:\CRAFT\EffectCraft`
- VideoFactoryAI em `D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI`

### 5.2 O que o projeto gasta localmente

O que o projeto gasta localmente hoje é:

- FFmpeg para extração de quadros, montagem e código de áudio;
- Python para o pipeline e backend;
- Node.js e Remotion para renderização de composições;
- ComfyUI para fluxos opcionais de difusão, quando houver benchmark que caiba;
- stick-film para o motor de bonecos;
- GPU local GTX 1060 6 GB para o que couber.

## 6. Modelos que já foram baixados

Os modelos que já foram baixados para o pipeline de análise e registrados são:

- YOLOv8n-pose em `.cache/modelos/yolov8n-pose.pt`
- U2Net em `.cache/rembg/models/u2net/u2net.onnx`
- Depth Anything V2 Small em `.cache/huggingface/...`
- faster-whisper small em `.cache/whisper/...`

Os hashes e tamanhos foram registrados em:

- `docs/licencas.md`

Os modelos do ComfyUI já inventariados são:

- Stable Diffusion 1.5
- DreamShaper 8
- AnimateDiff
- IP-Adapter SD1.5 e IP-Adapter Plus SD1.5
- FLUX.1-schnell fp8
- CLIP ViT-H-14 laion2B

O inventário completo está em:

- `docs/licencas.md`
- `descoberta/modelos_encontrados.json`

Importante: DreamShaper 8 não deve ser usado até a licença ser confirmada.

## 7. O que está registrado em contrato no projeto

O que está em contrato no projeto:

- vIdeo completo só depois de aprovação;
- nada de nuvem nem serviço pago;
- ferramentas locais;
- nomes de exibição genéricos, sem marcas;
- entrada YouTube somente com confirmação de direitos;
- técnicas não verificadas marcadas como experimentais;
- segurança infantil antes de tudo.

Isso está em:

- `docs/contrato_m2.md`
- `docs/decisoes.md`
- `docs/licencas.md`
- `config.json`

## 8. Onde o trabalho parou

O trabalho parou em:

- temos o projeto pronto com pipeline, backend, frontend, Remotion, ComfyUI,
  técnicas, configurações e documentação;
- temos os três vídeos de referência;
- temos o primeiro bloco de 10 segundos do “O Parque dos Pets.mp4” extraído,
  com análise de movimento e testes de animação inicial;
- ainda não temos o contrato consolidado que junta tudo isso em um só lugar
  para evitar que o trabalho se perca.

Ou seja: a base está aqui. O que ainda falta é consolidar isso de forma que qualquer
continuidade saiba exatamente onde parou e o que fazer depois.

## 9. O que tem que ser entregue

O que tem que ser entregue, de forma explícita, é:

### 9.1 Entrada

- os vídeos que já foram passados como referência;
- caso venham outros vídeos, eles devem ser colocados de forma idêntica ao que já existe;
- se o vídeo vier do YouTube, ele só entra com confirmação de direitos;
- se vier do VideoFactoryAI, deve seguir o que já está registrado no projeto para essa
  entrada.

### 9.2 Processamento

- cada vídeo deve ter suas cenas separadas;
- cada cena deve ter o que tem nela identificado;
- cada cena deve ter o que será animado definido;
- a animação deve acontecer dentro da própria cena;
- o áudio e a narração originais devem ser mantidos sempre que existirem;
- o ritmo da história deve ser mantido.

### 9.3 Estilo

- o estilo desejado é animação bonita para criança;
- os personagens principais devem aparecer se mexendo;
- elementos como brinquedos, roda gigante, carrinhos e outros podem ser animados
  quando fazem sentido na cena;
- não é permitido inventar novidade desnecessária só porque o projeto tem ferramentas;
- não é permitido recriar o que já existe no projeto;
- o possível local e viável localmente tem prioridade.

### 9.4 Saída

- a saída é o vídeo animado final;
- a saída deve manter a história e o áudio originais;
- a saída deve ser gerada a partir do que já está pronto no projeto quando possível.

### 9.5 Entregáveis documentais

- o contrato deve servir como ponto único de partida para qualquer continuidade;
- o contrato deve conter o que foi feito, o que foi testado, as ferramentas em uso,
  os modelos baixados e o estado atual do trabalho;
- todo avanço relevante deve ser registrado de forma que não se perca.

## 10. Regras para não se perder

Regras prontas para quem for continuar a partir deste documento:

1. Leia este contrato primeiro.
2. Leia `config.json`.
3. Leia `docs/decisoes.md` e `docs/licencas.md`.
4. Leia `docs/progresso.md` e `docs/contrato_m2.md`.
5. Não recrie o que já existe no pipeline, no backend, no Remotion ou nas técnicas.
6. Não comece do zero sem motivo.
7. Use as ferramentas que já estão instaladas antes de propor outra.
8. Registre qualquer avanço novo neste contrato ou nos documentos dele.
9. Se um vídeo novo entrar, registre-o aqui e nos projetos correspondentes.
10. Se o trabalho parar depois, deixe claro onde parou e qual é o próximo passo.

## 11. Ponto de partida atual

O ponto de partida atual é:

- vídeos de referência na raiz do projeto;
- projeto base pronto em `estudio/`;
- primeiro bloco de trabalho do “O Parque dos Pets.mp4” já extraído;
- análise inicial de movimento feita;
- testes de animação inicial já gerados.

O trabalho seguinte deve continuar a partir do que já existe, não reinventando nada,
e registrado neste contrato para que não se perca.
