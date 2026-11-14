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

### Próximo marco

M1 — Análise de vídeo: cenas, movimento, profundidade, máscaras, pose e fala,
com schemas versionados e validação no golden set.
