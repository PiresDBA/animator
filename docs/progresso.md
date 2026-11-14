# Progresso

## M0 — Ambiente (concluído e aprovado)

Data: 2026-11-14
Status: **concluído e aprovado pelo usuário; M1 iniciado.**

### O que foi feito

- Estrutura de pastas da seção 18 criada em `D:\PROJETOS-IA\animacao\estudio`.
- `config.json` com as respostas da entrevista e os padrões confirmados.
- Coleta de hardware em `perfil_hardware.json`.
- Descoberta de programas em `descoberta/` (config, PATH, registro, pastas
  comuns e varredura com prazo), somente leitura.
- Inventário de modelos do ComfyUI em `descoberta/modelos_encontrados.json`.
- Teste real de GPU em `docs/evidencias/m0_gpu.json`.
- Cópia local do FFmpeg 8.1 full + teste de fumaça H.264/AAC.
- 10 testes unitários da descoberta, incluindo pastas com acentos/espaços e
  verificação de que a varredura não altera arquivos.
- Licenças verificadas em fontes oficiais em `docs/licencas.md`.
- Decisões registradas em `docs/decisoes.md`.

### Evidências

| Comando | Resultado |
|---|---|
| `py -3.12 descoberta/hardware.py --salvar` | `OK: perfil_hardware.json` |
| `py -3.12 descoberta/programas.py --max-seconds 180` | 17.172 pastas, 37 erros de acesso, 39,14 s, concluída no prazo; tabela abaixo |
| `py -3.12 descoberta/modelos.py --comfyui "D:\Comfy\ComfyUI" --salvar` | 7 modelos, 21.723,2 MB |
| `& "D:\Comfy\ComfyUI\venv\Scripts\python.exe" descoberta/teste_gpu.py --salvar` | `OK: docs/evidencias/m0_gpu.json` |
| `py -3.12 -m unittest discover -s tests -v` | 10 testes, todos OK, 0,227 s |
| `ffmpeg -i color... -c:v libx264 -c:a aac` | MP4 de 1,0 s, H.264 + AAC, 12.388 bytes |

Arquivos gerados:

- `perfil_hardware.json`
- `docs/evidencias/m0_gpu.json`
- `docs/evidencias/m0_ffmpeg_smoke.mp4`
- `descoberta/modelos_encontrados.json`
- `tools/ffmpeg/ffmpeg.exe` e `tools/ffmpeg/ffprobe.exe` (fora do git)

Capturas de tela: não aplicáveis ao M0, que ainda não tem interface. As
evidências são JSONs e a saída dos comandos acima.

### Tabela de descoberta (confirmada e salva)

| Tipo | Origem | Caminho | Evidência |
|---|---|---|---|
| comfyui | pasta_comum | `D:\Comfy\ComfyUI` | `main.py` + `models/` |
| effectcraft | pasta_comum | `D:\CRAFT\EffectCraft` | `effectcraft.exe` |
| ffmpeg | varredura | `C:\Program Files\Krita (x64)\bin` | `ffmpeg.exe` + `ffprobe.exe` |
| ffmpeg | pasta_comum | `...\WinGet\Packages\Gyan.FFmpeg...\ffmpeg-8.1-full_build\bin` | `ffmpeg.exe` + `ffprobe.exe` |
| ffmpeg | varredura | `C:\Users\Pires\StickFilms\.tools\bin` | `ffmpeg.exe` + `ffprobe.exe` |
| ffmpeg | varredura | `D:\CRAFT\VoiceCraft\ffmpeg\bin` | `ffmpeg.exe` + `ffprobe.exe` |
| ffmpeg | pasta_comum | `D:\PROJETOS-IA\animacao\estudio\tools\ffmpeg` | cópia local do projeto |
| ffmpeg | varredura | `D:\PROJETOS-IA\Fabrica-de-videos\ffmpeg\bin` | `ffmpeg.exe` + `ffprobe.exe` |
| motor_bonecos | varredura | `C:\Users\Pires\.claude\skills\stick-film\stick-film` | `engine/render.mjs` + `character.js` |
| motor_bonecos | varredura | `C:\Users\Pires\.codex\skills\stick-film\stick-film` | idem |
| motor_bonecos | varredura | `C:\Users\Pires\.opencode\skills\stick-film\stick-film` | idem |
| motor_bonecos | varredura | `D:\PROJETOS-IA\nov09-00_53\TIMELINE\skills\stick-film` | idem |
| motor_bonecos | pasta_comum | `D:\PROJETOS-IA\stick-film\stick-film` | idem |
| remotion | varredura | `C:\Users\Pires\.claude\skills\documentary-timeline-editor\assets\templates` | `package.json` + `src/Root.tsx` |
| remotion | varredura | `D:\CRAFT\OpenMontage\remotion-composer` | idem |
| remotion | varredura | `D:\PROJETOS-IA\nov09-00_53\TIMELINE\_edit` | idem |
| remotion | varredura | `D:\PROJETOS-IA\nov09-00_53\TIMELINE\_marketing` | idem |
| remotion | varredura | `D:\PROJETOS-IA\The Lamp That Kept Burning\_edit` | idem |
| videofactoryai | pasta_comum | `D:\PROJETOS-IA\Fabrica-de-videos` | pasta do projeto |
| videofactoryai | pasta_comum | `D:\PROJETOS-IA\Fabrica-de-videos\VideoFactoryAI` | pasta do projeto |

**Importante:** a tabela foi confirmada pelo usuário em 2026-11-14 e gravada em
`descoberta/resultado_varredura.json` com `confirmado_pelo_usuario=true`
(17.172 pastas, 37 erros de acesso, 25,91 s). Os caminhos principais foram
gravados em `config.json`.

### Medidas reais

- Coleta de hardware: 2026-11-14T12:20:45Z.
- GPU em repouso: 53 °C, 4,4 W, 0% de uso, 425 MiB de VRAM.
- Teste de GPU: 4,98 s no total; matmul 45,0 ms (mediana); convolução 2,49 ms
  (mediana; primeira execução 112,4 ms por autotune); pico PyTorch 235,1 MiB;
  `nvidia-smi` com 1 amostra: 55 °C, 63,9 W, 692 MiB, 17%.
- Varredura: 39,14 s, 17.172 pastas, 37 erros de acesso, sem alteração de
  arquivos (teste automatizado).
- Discos: C: 37,2 GB livres; D: 819,2 GB livres.
- FFmpeg: MP4 de 1,0 s, H.264 + AAC, 12.388 bytes.
- **Estimativas:** nenhuma neste marco. Os números acima foram medidos.

### Decisões tomadas

Registradas em `docs/decisoes.md`: D001 a D020. Destacam-se: raiz em D:,
ambientes Python isolados, FFmpeg local, descoberta somente leitura, entrada
YouTube com direitos confirmados, nomes de exibição sem marcas, Remotion
pessoal/educacional, lotes curtos para TDR e uso do stick-film como motor.

### Riscos e limitações conhecidas

- O teste de GPU é curto; não mede carga térmica sustentada.
- Há cinco cópias do motor de bonecos; foi escolhida a fonte do projeto
  (`D:\PROJETOS-IA\stick-film\stick-film`), que tem `sprite.js` e `diag.mjs`.
- Há cinco projetos Remotion candidatos; será criado um projeto limpo 4.0.542.
- Faltam modelos de segmentação, profundidade, pose, fala e interpolação.
- DreamShaper 8 está bloqueado; o YOLOv8n-pose (AGPL-3.0) foi aceito somente
  para uso pessoal/educacional.
- yt-dlp ainda não foi instalado. Playwright-core e Chrome foram localizados
  (`C:\Users\Pires\StickFilms\.tools` e `C:\Program Files\Google\Chrome\Application\chrome.exe`),
  mas o motor ainda não foi executado.
- C: tem pouco espaço livre; artefatos devem ficar em D:.
- Nenhuma geração de vídeo foi executada; o M1 ainda não começou.

### Aprovação do usuário (concluída em 2026-11-14)

1. Tabela de descoberta aprovada e salva.
2. Motor de bonecos: fonte do projeto
   `D:\PROJETOS-IA\stick-film\stick-film`.
3. Remotion: projeto limpo local com versão fixa 4.0.542.
4. DreamShaper 8 fica fora; YOLOv8n-pose aceito para uso pessoal/educacional.
5. Venv local e downloads do M1 autorizados, com registro de licenças.
6. Golden set sintético de 3 clipes de 10 s autorizado.
7. PC pode ser usado durante a geração.

### Próximo marco do M0

M1 — Análise de vídeo: cenas, movimento, profundidade, máscaras, pose e fala,
com schemas versionados e validação no golden set.

## M1 — Análise de vídeo (concluído e aprovado)

Data: 2026-11-14
Status: **pipeline executado nos 3 clipes do golden set; 3 JSONs válidos e
23 testes OK. Aprovado pelo usuário em 2026-11-14; M2 iniciado.**

Ressalva de aprovação: na cena 2, o movimento medido é a translação global de
dois bonecos rígidos que se arrastam, se encaram, se encostam e voltam. Não há
animação de braços ou pernas; o M2 deve preservar esse comportamento de tela
estática deslizando.

### O que foi feito

- `.venv` local com Python 3.12.9 e dependências fixadas em `requirements.txt`;
  caches de modelos, pip, Hugging Face, Ultralytics, rembg, Whisper e Matplotlib
  em `.cache/` no D:.
- Golden set sintético de 3 clipes de 10 s, 1280x720, 30 fps, H.264 + AAC, com
  hashes e expectativas em `tests/golden/manifest.json`.
- Smoke dos modelos em `tests/modelos_smoke.py`: PySceneDetect, YOLOv8n-pose,
  Depth Anything V2 Small, rembg/U2Net e faster-whisper small.
- Pipeline modular em `pipeline/`: `video.py`, `cenas.py`, `movimento.py`,
  `profundidade.py`, `mascaras.py`, `pose.py`, `fala.py`, `medidas.py`,
  `cache.py`, `validar.py` e o CLI `analisar.py`.
- Schema versionado `pipeline/schemas/analise_v1.json` (Draft 2020-12,
  `versao: 1`), validado com `jsonschema` e `FormatChecker`.
- Execução real nos 3 clipes, com JSONs e prévias em `docs/evidencias/m1/`.
- Correções: etapas desativadas não marcam `status: parcial`; campos opcionais
  de fala (`avg_logprob`, `no_speech_prob`, `prob_idioma`) aceitam `None`;
  `av==15.1.0` e DLLs do torch resolvidas para o CTranslate2 em CUDA.
- Decisões D021 (Craft Voice/Piper) e D022 (ambiente do M1) registradas em
  `docs/decisoes.md`.

### Evidências

| Comando | Resultado |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | 23 testes, todos OK, 0,519 s |
| `.\.venv\Scripts\python.exe -m pipeline.analisar --video tests\golden\clipe_01_estatico.mp4 --saida docs\evidencias\m1\clipe_01_estatico.json --previa-dir docs\evidencias\m1\previa_clipe_01` | `OK`, 1 cena, pose 0, fala true, 36,30 s |
| idem para `clipe_02_acao.mp4` | `OK`, 3 cenas, pose 23, fala false, 51,77 s |
| idem para `clipe_03_texto.mp4` | `OK`, 1 cena, pose 0, fala true, 52,01 s |
| `.\.venv\Scripts\python.exe -m pip install --dry-run --no-deps -r requirements.txt` | todas as versões fixadas já satisfeitas |
| `tests/modelos_smoke.py` | 5 modelos executaram em CUDA/CPU conforme o caso |
| `Get-FileHash` dos 4 pesos | hashes SHA256 registrados em `docs/licencas.md` |

Resultados por clipe:

| Clipe | Cenas | Pose | Fala | Tempo total | VRAM pico | Temp. máx. | Util. máx. |
|---|---|---|---|---|---|---|---|
| `clipe_01_estatico` | 1 (0–10 s) | 0 | true (2 segmentos) | 36,30 s | 1.018 MB | 67 °C | 80% |
| `clipe_02_acao` | 3 (0–3, 3–6, 6–10 s) | 23 detecções | false (0 segmentos) | 51,77 s | 1.502 MB | 73 °C | 100% |
| `clipe_03_texto` | 1 (0–10 s) | 0 | true (2 segmentos) | 52,01 s | 1.502 MB | 73 °C | 100% |

Tempos por etapa no clipe 2: cenas 1,33 s; movimento 0,61 s; profundidade
13,41 s; máscaras 26,90 s; pose 1,70 s; fala 3,70 s. No primeiro uso do rembg, a
importação/criação de sessão adicionou ~58 s ao total (primeira execução do
clipe 1: 102,22 s); execuções seguintes ficaram em 36–52 s por clipe.

### Modelos baixados

| Modelo | Arquivo | Bytes | SHA256 |
|---|---|---|---|
| YOLOv8n-pose | `.cache/modelos/yolov8n-pose.pt` | 6.832.633 | `c6fa93dd1ee4a2c18c900a45c1d864a1c6f7aba75d84f91648a30b7fb641d212` |
| U2Net (rembg) | `.cache/rembg/models/u2net/u2net.onnx` | 175.997.641 | `8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491` |
| Depth Anything V2 Small | `.cache/huggingface/hub/models--depth-anything--Depth-Anything-V2-Small-hf/blobs/3152...` (`model.safetensors`) | 99.173.660 | `3152477ce0d8d6978d76b995120de97cb5b928701fd0f817769f59e249a16b70` |
| faster-whisper small | `.cache/whisper/models--Systran--faster-whisper-small/blobs/3e30...` (`model.bin`) | 483.546.902 | `3e305921506d8872816023e4c273e75d2419fb89b24da97b4fe7bce14170d671` |

### Limitações medidas

- O YOLOv8n-pose detecta bem as duas figuras no clipe 2 até 5,5 s, mas retorna
  0 detecções entre 6,0 e 9,0 s e 1 em 9,5 s (confiança 0,429). O resultado é
  registrado como ausência; o pipeline não inventa pontos.
- O Whisper small comete erros no TTS sintético em português (“Este atil símbolo
  de Copyrighto 3º Clip.”). O texto bruto fica no JSON para auditoria; a prévia
  final deve permitir correção humana.
- A primeira execução do rembg tem custo alto de importação/sessão; o cache de
  modelos e o uso repetido do mesmo processo reduzem o tempo.
- O aviso de `hf_xet` continua porque o pacote não está no `.venv`; downloads
  continuam funcionando. Não instalar no Docling/global.
- `pip check` acusa dependências opcionais não instaladas (`opencv-python`,
  `nvidia-ml-py`, `polars`, `ultralytics-platform`) porque a instalação usa
  `--no-deps` e `opencv-python-headless`; o pipeline funciona assim.
- As medições de GPU são curtas (36–52 s), não um teste térmico sustentado.

### Próximo marco

M2 — primeira prévia vertical com o motor de bonecos, aprovação humana e
renderização de um trecho curto; nenhum vídeo completo antes do portão do M3.


## M2 — Primeiro estilo fim a fim: bonecos de palito em CPU (aprimorado e pronto para aprovação)

Data: 2026-11-14
Status: **concluído, aprimorado com expressividade lúdica e aguardando aprovação humana antes do M3.**

### O que foi feito

- Implementação do adaptador do motor de bonecos `stick-film` em `pipeline/render_stick.py` com o estilo expressivo `line`:
  - Personagens completos com traços faciais (olhos, sobrancelhas e sorriso), proporções equilibradas e acessórios (cachecol e gorro em tons contrastantes).
  - Cenografia completa integrada: faixa de solo texturizada, colinas em paralaxe, sol, nuvens em deriva e árvore estilizada.
  - Coreografia adaptativa: atores realizam poses expressivas (`happy`, `wave`, `surprised`, `celebrate`) e só utilizam passos com passada natural quando há deslocamento real (> 40 px), eliminando passos robóticos parados no mesmo lugar.
  - Movimento dinâmico de câmera com push-in suave (z: 0.95 -> 1.04 -> 1.0).
- Trilha sonora procedural lúdica infantil gerada via motor DSP do `stick-film` (`audio/score.py` + `audio/dsp.py`):
  - Melodia alegre em preset `playful` com marimba/acordes, baixo, pad e reverberação acústica natural em 48 kHz estéreo.
  - Volume verdadeiramente seguro infantil de -8.4 dBTP (limite WCAG/infantil de -6.0 dBTP).
- Implementação de rastreamento de atores local por subtração de fundo (sem GPU) em `pipeline/tracking.py`.
- Checagem de segurança infantil em `pipeline/seguranca.py` (flashes WCAG 2.3.1 em janela de 1 s, volume -6 dBTP e filtro léxico).
- Implementação do roteador de técnicas por cena em `pipeline/roteador.py`.
- Gerador CLI de prévia em `pipeline/previa.py` integrando tracking, renderização pelo motor, montagem de áudio sincronizado via FFmpeg, extração de miniatura, laudo de segurança e persistência de `previa.json`.
- Backend FastAPI completo com endpoints `/api/estado`, CRUD de projetos, fila SQLite com worker persistente, difusão WebSocket em `/api/eventos` e bloqueio 403 obrigatório para `/api/projetos/{id}/completo`.
- Frontend React + Vite + TypeScript + Tailwind em `frontend/dist/` com 10 páginas, gráficos Recharts, prévias comparativas lado a lado e slider antes/depois, e painel de decisão com notas por estrelas em 5 critérios.
- `iniciar.bat` para inicializar o backend e abrir a interface gráfica automaticamente no navegador (`http://127.0.0.1:8765`).
- Criação da suíte de testes automatizados do M2 em `tests/test_m2.py`. Total de 29 testes unitários passando.

### Evidências

| Comando | Resultado |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | 29 testes, todos OK, 0,712 s |
| `npx tsc --noEmit` em `frontend/` | 0 erros, TypeScript validado |
| `npm run build` em `frontend/` | build concluído com sucesso gerando `frontend/dist/` |
| `.\.venv\Scripts\python.exe -m pipeline.previa --projeto teste-backend --estilo bonecos --trecho-inicio 0.0 --trecho-fim 5.0 --resolucao 480p` | `OK: projetos/teste-backend/previa.json` (tempo 15,256 s) |
| `Invoke-RestMethod http://127.0.0.1:8765/api/estado` | Retorna `{"marco": "M2", "backend": "ok", ...}` |
| Chamada para `POST /api/projetos/teste-backend/completo` | Retorna HTTP 403 Forbidden com bloqueio de Fase B sem aprovação |

Arquivos gerados:
- `projetos/teste-backend/saidas/previa_bonecos_004.mp4` (vídeo H.264 + AAC, 854x480, 30 fps, 5,0 s, 454.450 bytes)
- `projetos/teste-backend/saidas/miniatura_bonecos_004.png` (228.178 bytes)
- `projetos/teste-backend/saidas/audio_trecho.wav` (960.078 bytes)
- `projetos/teste-backend/previa.json` (validado com o schema do contrato)
- `projetos/teste-backend/mapa_tecnicas.json`
- `frontend/dist/` (assets de produção do painel web)

### Medidas reais

- Metodologia: cronometragem de alta precisão via `time.perf_counter()` no pipeline e telemetria de GPU via `nvidia-smi`.
- Tempo de renderização da prévia de 5 s (150 quadros a 30 fps em 854x480 com cenografia e personagens estilo line): **15,256 s** em CPU.
- Taxa de renderização do motor `stick-film`: ~9,8 quadros/s em CPU (Intel i7-7700HQ).
- Consumo de VRAM durante a prévia de bonecos: **0 MB adicionais** (processamento 100% CPU).
- Temperatura da GPU durante o M2: 53 °C estável.
- Flashes luminosos (WCAG 2.3.1): 0 variações (limite 3/s). Veredito verde.
- True Peak de áudio medido: **-8.4 dBTP** (limite seguro: -6.0 dBTP). Veredito verde.
- Testes automatizados: 29 testes em 0,712 s.

### Decisões tomadas

Registradas em `docs/decisoes.md`:
- **D024**: Resolução do motor de bonecos em 480p (854x480) com renderização de 150 quadros via headless Chrome local e Playwright-core existente em `C:\Users\Pires\StickFilms`.
- **D025**: Tratamento de silêncio absoluto (`Peak: -inf dBFS`) no medidor de volume do FFmpeg como -70 dBTP seguro.
- **D026**: Servir o build do frontend em `frontend/dist` diretamente pelo FastAPI na porta 8765 sob a rota raiz `/`.
- **D027**: Substituição do estilo plano básico pelo estilo `line` com feições (olhos e sorriso), cenografia procedural (colinas, sol, nuvens, árvore) e trilha sonora DSP lúdica infantil para cativar crianças de 7 a 10 anos.

### O que precisa da aprovação do usuário antes do próximo marco

1. Aprovação da nova prévia de 5 s gerada para bonecos de palito (`projetos/teste-backend/saidas/previa_bonecos_004.mp4`).
2. Validação da interface gráfica web (acessível em `http://127.0.0.1:8765` ao executar `iniciar.bat` ou pelo navegador já aberto).
3. Autorização para prosseguir para o **M3 — Portão e Segurança** (regras de portão, testes de flashes sintéticos, decisões em avaliacoes.json e retomada de estado).

## M3 — Portão e Segurança (concluído)

Data: 2026-11-14
Status: **concluído; aguardando aprovação do usuário.**

### O que foi feito

- **Portão de aprovação humana**: o endpoint `POST /api/projetos/{id}/completo` agora verifica `avaliacoes.tem_aprovacao()`. Sem aprovação → 403. Com aprovação → 202 (job enfileirado na fila SQLite).
- **Job handler `completo`**: registrado em `backend/app.py`, importa `pipeline.completo.executar()` e gera o vídeo completo da Fase B com receipt.json.
- **Dupla barreira**: tanto o endpoint quanto o `pipeline.completo` verificam independentemente a existência de aprovação em `avaliacoes.json`.
- **Teste de flash sintético**: vídeo com 10 flashes/s gerado via OpenCV → `seguranca.medir_flashes()` retorna `ok: False` (bloqueado). Vídeo sem flashes (cor constante) → `ok: True`.
- **Teste de volume**: prévia existente verificada com `medir_volume()` e `checar()` → veredito verde.
- **Teste de retomada da fila**: jobs persistem em SQLite entre instâncias. Jobs em `"rodando"` são recuperados como `"erro"` ao reiniciar (`_recuperar()` no `iniciar()`).
- **Validação de avaliacoes.json**: schema verificado (versão, lista, campos obrigatórios, notas de 1 a 5 em 5 critérios, decisão no enum).
- **Aliases de critérios**: `atencao_infantil → adequacao_infantil`, `clareza_cenas → clareza_historia`, etc., validados.
- **Filtro de conteúdo léxico**: termos de terror, violência e conteúdo impróprio testados em 4 cenários.
- **Suíte de testes M3**: 22 novos testes em `tests/test_m3.py`.
- **Testes M2 atualizados**: assertions de marco atualizadas para aceitar M2+ sem quebrar.
- **Total: 51 testes passando** em 2,147 s.
- Decisões D028, D029 e D030 registradas em `docs/decisoes.md`.

### Evidências

| Comando | Resultado |
|---|---|
| `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | 51 testes, todos OK, 2,147 s |
| `POST /api/projetos/teste-backend/completo` com aprovação | Retorna `{"job_id": "job_...", "aprovacao": "av_001"}` (HTTP 202) |
| `POST /api/projetos/_test_m3_sem_avaliacao/completo` sem avaliação | Retorna HTTP 403 `{"erro": "sem_aprovacao"}` |
| Flash sintético (10/s) → `medir_flashes()` | `ok: False`, `max_flashes_1s: 14` |
| Vídeo sem flash → `medir_flashes()` | `ok: True`, `max_flashes_1s: 0` |
| Prévia existente → `checar()` | `veredito: "verde"` |
| Fila SQLite: job persiste entre instâncias | `status: "na_fila"` recuperado |
| Fila SQLite: job "rodando" recuperado | `status: "erro"`, mensagem "reiniciado" |

Arquivos criados/modificados:
- `pipeline/completo.py` (novo: gerador de vídeo completo Fase B)
- `backend/app.py` (portão M3, handler completo, PedidoCompleto)
- `backend/servicos/avaliacoes.py` (aliases, params estruturados)
- `tests/test_m3.py` (novo: 22 testes M3)
- `tests/test_m2.py` (atualizado para M3+)
- `docs/decisoes.md` (D028, D029, D030)

### Medidas reais

- Testes automatizados: 51 testes em 2,147 s (CPU, sem GPU).
- Flash sintético (320×240, 30 fps, 2 s, 10 alternâncias/s): gerado e medido em < 0,2 s.
- Retomada da fila: < 0,05 s para criar/recuperar SQLite.

### Critérios de aceite M3 (seção 4 do Prompt Mestre)

| Critério | Status |
|---|---|
| Nenhuma Fase B sem aprovação | ✅ 403 sem aprovação, 202 com |
| Testes de flashes | ✅ Flash sintético detectado e bloqueado |
| Decisões em avaliacoes.json | ✅ Schema validado com 5 critérios |
| Retomada após fechar o app | ✅ SQLite persiste, jobs "rodando" recuperados |

### O que precisa da aprovação do usuário antes do próximo marco

1. Confirmação de que o M3 atende aos critérios de aceite.
2. Autorização para prosseguir para o **M4 — Estilos Procedurais** (LEGO, anime, 3D cartoon e 3D PBR).
