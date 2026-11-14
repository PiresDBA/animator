# Decisões

Registro cronológico. Toda decisão técnica não óbvia entra aqui.

## D001 — Raiz do projeto

- Data: 2026-11-14
- Decisão: manter o repositório em `D:\PROJETOS-IA\animacao\estudio`.
- Motivo: D: tem espaço livre suficiente; C: está com pouco espaço.
- Alternativa descartada: usar C:, que tem apenas ~37 GB livres.

## D002 — Fase A primeiro, todos os estilos habilitados por configuração

- Data: 2026-11-14
- Decisão: os cinco estilos ficam listados em `config.json` e em `estilos/`, mas
  a Fase A começa por análise + bonecos de palito. LEGO/anime/cartoon/3D entram
  no M4. A Fase B (vídeo completo) só é liberada após o portão do M3.
- Motivo: cumprir o portão de aprovação e provar o pipeline sem GPU.

## D003 — Ambientes Python isolados

- Data: 2026-11-14
- Decisão: um venv por componente Python; nada é instalado globalmente.
- Exceção de M0: o teste de GPU usa o venv já existente do ComfyUI
  (`D:\Comfy\ComfyUI\venv`), que tem PyTorch 2.6.0+cu126. Nenhum arquivo foi
  instalado ou alterado fora do projeto.
- Motivo: evitar conflito de dependências e preservar a instalação do usuário.

## D004 — FFmpeg local

- Data: 2026-11-14
- Decisão: copiar `ffmpeg.exe` e `ffprobe.exe` do build Gyan 8.1 full
  (instalado via WinGet) para `tools/ffmpeg/`.
- Versão: 8.1-full_build-www.gyan.dev, build GPL (`--enable-gpl
  --enable-version3 --enable-libx264`).
- Motivo: o FFmpeg não está no PATH e o build é estável e completo. A cópia
  torna o caminho reprodutível; os binários ficam fora do git.
- Consequência: se o projeto for distribuído com esse binário, obrigações GPL
  se aplicam. Uso local não distribui o binário.

## D005 — Descoberta somente leitura e confirmação antes de salvar

- Data: 2026-11-14
- Decisão: `descoberta/varredura.py` não escreve nada durante a varredura. O
  resultado só é gravado com `--salvar` e nasce com
  `confirmado_pelo_usuario=false`.
- Prazo padrão: 180 s, com parada antecipada.
- Exclusões: Windows, Recycle Bin, System Volume Information, backups, jogos,
  Docker, OneDrive, node_modules, venvs e caches.

## D006 — Entrada YouTube com direitos confirmados

- Data: 2026-11-14
- Decisão: a entrada principal é YouTube, mas cada download exige confirmação
  explícita de direitos e usa yt-dlp local. Nada é enviado para a nuvem.
- Alternativa descartada: baixar sem confirmação; violaria os termos da
  plataforma e a regra de direitos do projeto.

## D007 — Nomes de exibição sem marcas protegidas

- Data: 2026-11-14
- Decisão: o estilo "LEGO" aparece na interface como **Mosaico de blocos**.
  "Anime", "Cartoon 3D" e "3D" são descrições genéricas. Nenhum nome de estúdio,
  franquia, personagem ou logotipo entra em prompts, textos ou arquivos de
  estilo.
- Motivo: seção 13 e 19 do contrato.

## D008 — Licença do Remotion

- Data: 2026-11-14
- Situação declarada pelo usuário: pessoal/educacional.
- Decisão: registrar essa situação e usar a Free License do Remotion, que a
  documentação oficial descreve como gratuita para indivíduos e empresas de até
  três pessoas. Revalidar antes de qualquer uso comercial ou distribuição.
- Remotion ainda não está instalado; a instalação será local ao projeto.

## D009 — D: para artefatos; C: apenas para ferramentas

- Data: 2026-11-14
- Decisão: projetos, saídas, caches e modelos grandes ficam em D:. C: não
  recebe artefatos de vídeo.
- Medição: C: 37,3 GB livres; D: 819,6 GB livres no momento da coleta.

## D010 — Sem limite prático de tempo, mas com lotes curtos

- Data: 2026-11-14
- Decisão: o usuário não definiu limite prático de geração e pode usar o PC
  durante o processamento. Ainda assim, kernels longos serão divididos em lotes
  curtos para reduzir risco de TDR, com tempo medido por lote.

## D011 — Motor de bonecos é o stick-film local

- Data: 2026-11-14
- Decisão: usar `D:\PROJETOS-IA\stick-film\stick-film` como motor de bonecos.
  Ele é um engine Node.js/Playwright próprio (não usa o par
  `three`+`remotion` descrito na assinatura genérica). O adaptador
  `pipeline/render_stick.py` lerá o motor e passará poses sem reescrevê-lo.
- Pendência: executar o motor no M2. Playwright-core e Chrome foram localizados
  em `C:\Users\Pires\StickFilms\.tools` e `C:\Program Files\Google\Chrome\Application\chrome.exe`.

## D012 — Stack GPU validada no M0

- Data: 2026-11-14
- Decisão: usar como referência o PyTorch 2.6.0+cu126 do venv do ComfyUI, que
  reporta CUDA disponível e capacidade sm_61 na GTX 1060.
- O teste real (matmul + convolução) e as medições ficam em
  `docs/evidencias/teste_gpu.json` e no relatório do M0.

## D013 — Público 7 a 10 anos

- Data: 2026-11-14
- Decisão: ritmo médio, cortes moderados e linguagem adequada à faixa. O
  checklist de observação com a criança é opcional e só com consentimento do
  responsável.

## D014 — Entrada e padrões confirmados

- Data: 2026-11-14
- Entrada principal: YouTube, com confirmação de direitos por vídeo.
- Padrões confirmados: 60 s, 720p, áudio original, legendas queimadas, 16:9 e
  9:16, interface web local com tema escuro e acento azul-ciano, 3 tentativas
  por estilo.
- Orçamento: sem limite prático declarado; PC disponível durante a geração.

## D015 — M0 aprovado e descoberta persistida

- Data: 2026-11-14
- Decisão: o usuário aprovou a tabela de descoberta. O resultado foi salvo em
  `descoberta/resultado_varredura.json` com `confirmado_pelo_usuario=true`, e os
  caminhos confirmados foram gravados em `config.json`.
- Evidência: 17.172 pastas, 37 erros de acesso, 25,91 s, concluída no prazo.
- Caminhos principais: ComfyUI, EffectCraft, FFmpeg local, motor stick-film,
  Remotion local (a criar) e VideoFactoryAI.

## D016 — Motor de bonecos: fonte do projeto

- Data: 2026-11-14
- Decisão: usar `D:\PROJETOS-IA\stick-film\stick-film`.
- Motivo: é a única cópia com `engine/sprite.js` e `engine/diag.mjs`; o README
  do projeto é mais completo que o das cópias instaladas em `.claude`, `.codex`
  e `.opencode`.
- Consequência: o adaptador `pipeline/render_stick.py` lerá esse motor sem
  reescrevê-lo. As cópias instaladas ficam apenas como referência.

## D017 — Remotion limpo, versão fixa 4.0.542

- Data: 2026-11-14
- Decisão: criar um projeto Remotion mínimo em `estudio/remotion` com
  `remotion` e `@remotion/cli` fixados em 4.0.542.
- Motivo: evita herdar código, dependências e licenças de terceiros dos cinco
  projetos candidatos. O OpenMontage 4.0.484 fica apenas como referência.
- Consequência: o projeto local precisa ser criado e testado no M2.

## D018 — Licenças: DreamShaper fora; YOLO aceito com restrição

- Data: 2026-11-14
- Decisão: o DreamShaper 8 permanece bloqueado até a licença dos pesos ser
  esclarecida. O YOLOv8n-pose (AGPL-3.0) é aceito somente para uso
  pessoal/educacional, sem distribuir o modelo nem o código derivado.
- Alternativa: se houver distribuição, trocar por um detector de pose
  permissivo e revalidar a qualidade.
- Consequência: o inventário e os avisos do projeto devem marcar essa restrição.

## D019 — Golden set sintético

- Data: 2026-11-14
- Decisão: gerar localmente 3 clipes de 10 s (personagem estático, ação com duas
  figuras e cartela de texto), sem material de terceiros.
- Motivo: elimina risco de direitos e permite testar o pipeline de forma
  reproduzível.
- Limitação: clipes sintéticos não validam a qualidade de pose e fala em vídeos
  reais; o M1 deve reportar "sem detecção" quando for o caso, sem inventar
  resultados.

## D020 — Venv e downloads do M1 autorizados

- Data: 2026-11-14
- Decisão: criar `.venv` dentro do projeto e instalar dependências e modelos
  somente ali, sem instalação global. O cache do pip fica em D: ou é desativado
  para não pressionar C:.
- Regra: registrar licença, versão, tamanho e hash de cada modelo baixado antes
  de usá-lo no pipeline.

## D021 — Voz local com Craft Voice/Piper

- Data: 2026-11-14
- Decisão: usar o Craft Voice local em `D:\CRAFT\VoiceCraft`, endpoint
  `http://127.0.0.1:8090/api/tts`, provider `piper`, voz
  `pt_BR-faber-medium` e profile `infantil`.
- Motivo: voz em português totalmente local, adequada ao público 7–10 anos, sem
  enviar texto para serviços de nuvem. O golden set já foi gerado com essa voz;
  `tests/golden/manifest.json` registra 5,72 s e 4,94 s de síntese.
- Alternativa descartada: provedores de voz em nuvem do próprio VoiceCraft ou
  APIs pagas, por violarem a regra 100% local.
- Consequência: o VoiceCraft precisa estar em execução para sintetizar. Se
  estiver indisponível, o pipeline deve bloquear e pedir intervenção, não trocar
  silenciosamente para um serviço externo. Registrar versão e licença antes de
  distribuir áudios ou o app.

## D022 — Ambiente do M1: av fixo, DLLs do torch e caches em D:

- Data: 2026-11-14
- Decisão: fixar `av==15.1.0`, adicionar a pasta `torch/lib` ao `PATH` e chamar
  `os.add_dll_directory` antes de carregar o faster-whisper, e manter todos os
  caches de modelos/pip em `.cache/` no D:.
- Motivo: `av 19.0.2` removeu `metadata_errors`, usado pelo faster-whisper
  1.2.1; `av 14.4.0` não tem wheel cp312 para Windows e tentou compilar do
  source. O CTranslate2 em CUDA não encontrava `cublas64_12.dll` sem a pasta
  `torch/lib`. As duas falhas foram reproduzidas e corrigidas.
- Instalação: `requirements.txt` com versões exatas, índice cu126 para
  torch/torchvision e `--no-deps` porque `opencv-python-headless` substitui
  `opencv-python`. O `pip check` pode acusar dependências opcionais; isso é
  esperado e está documentado em `docs/limitacoes.md`.
- Consequência: não atualizar `av`, `faster-whisper` ou `ctranslate2` sem
  revalidar a transcrição em CUDA e CPU. Se o CUDA falhar, o código cai para CPU
  em vez de interromper a análise.

## D023 — Aprovação do M1 e movimento estático do M2

- Data: 2026-11-14
- Decisão: o M1 está aprovado. O M2 deve renderizar dois bonecos rígidos que
  deslizam pelo chão, se encaram, se encostam e retornam, sem ciclo de caminhada
  e sem animação de braços ou pernas.
- Motivo: o usuário confirmou que, na cena 2 do golden set, o “movimento” era
  apenas a translação global das duas figuras. A métrica do M1 mede fluxo
  óptico e diferença de quadros, não articulação; portanto, um valor alto de
  movimento não implica membros animados.
- Implementação: usar pose congelada sobre um deslocamento controlado no motor
  de bonecos; desativar `squash`, `drag`, `blur`, piscadas e passos automáticos.
  O resultado deve ser validado por stills e por uma prévia curta antes de
  qualquer vídeo completo.
- Consequência: a documentação e o relatório do M2 devem distinguir
  “translação global” de “movimento articulado”.

## D024 — Motor de bonecos em 480p e headless Chrome local

- Data: 2026-11-14
- Decisão: executar `render.mjs frames` usando o Node.js e o Playwright-core localizado em `C:\Users\Pires\StickFilms`, gerando 150 quadros a 30 fps em resolução 854x480 na CPU.
- Motivo: estilo 100% em CPU sem necessidade de GPU, garantindo que o primeiro estilo funcione mesmo em computadores sem aceleração gráfica.

## D025 — Suporte a silêncio absoluto no medidor de volume (-6 dBTP)

- Data: 2026-11-14
- Decisão: tratar valores `-inf dBFS` reportados pelo filtro `ebur128` do FFmpeg como silêncio absoluto seguro (-70.0 dBTP), atribuindo veredito verde na ausência de áudio ofensivo ou elevado.
- Motivo: clipes sintéticos ou trechos sem voz não devem ser penalizados com aviso amarelo quando não há qualquer risco de volume excessivo.

## D026 — Integração e hospedagem da interface estática via FastAPI

- Data: 2026-11-14
- Decisão: o backend FastAPI monta e serve a pasta `frontend/dist` na raiz `/` e a pasta do projeto em `/media`, unificando a inicialização do app em um único processo e porta (8765).

## D027 — Aprimoramento visual lúdico: estilo line, cenografia e trilha DSP

- Data: 2026-11-14
- Decisão: substituir a representação geométrica vazia dos bonecos pelo estilo nativo `line` do stick-film com feições expressivas (olhos e sorriso), acessórios infantis (cachecol e gorro), cenografia procedural (colinas, sol, nuvens e árvore), coreografia expressiva (aceno, alegria e comemoração em vez de passos no mesmo lugar) e sonorização procedural lúdica via `audio/score.py` e `audio/dsp.py` do motor.
- Motivo: atender ao critério de sucesso do Prompt Mestre ("prender a atenção de uma criança de 7 a 10 anos"), eliminando a rigidez robótica e o ruído sintético anterior, mantendo 100% de processamento local em CPU e limite de volume estritamente seguro (-8.4 dBTP <= -6.0 dBTP).
- Motivo: simplifica o uso para o usuário, permitindo abrir o estúdio diretamente pelo `iniciar.bat` sem necessidade de múltiplos servidores locais abertos em paralelo.

## Pendências de decisão

- Definir se o EffectCraft entra no piloto do M5/M6.
- Manter o DreamShaper 8 fora até a licença dos pesos ser esclarecida.
- Se houver distribuição do projeto, substituir o YOLOv8n-pose por alternativa
  permissiva e revisar as obrigações GPL do FFmpeg e AGPL do YOLO.

## D028 — Portão M3: liberação condicional do vídeo completo

- Data: 2026-11-14
- Decisão: o endpoint `POST /api/projetos/{id}/completo` verifica `avaliacoes.tem_aprovacao()` e, se houver pelo menos uma avaliação com `decisao: "aprovar"` para o projeto, enfileira um job do tipo `"completo"` que chama `pipeline.completo.executar()`. Sem aprovação, retorna 403. O `pipeline.completo` faz a mesma verificação lendo `avaliacoes.json` diretamente como dupla barreira de segurança.
- Motivo: atender ao contrato M3 (seção 4, Portão e Segurança) — nenhuma Fase B sem aprovação humana formal. A dupla barreira (backend + pipeline) garante que mesmo execução via CLI respeita o portão.
- Alternativa descartada: liberar automaticamente com base em notas médias ≥ 3 (violaria a prioridade #2 de aprovação humana explícita).

## D029 — Recuperação de jobs após reinício do backend

- Data: 2026-11-14
- Decisão: ao chamar `fila.iniciar()`, o método `_recuperar()` marca todos os jobs em status `"rodando"` como `"erro"` com a mensagem "Job interrompido: o backend foi reiniciado." Isso garante que o usuário saiba que um job foi interrompido e pode reenfileirá-lo.
- Motivo: jobs que ficaram em `"rodando"` quando o processo caiu nunca vão terminar sozinhos. Marcá-los como erro é a opção mais segura e transparente.

## D030 — Teste de flash sintético com vídeo OpenCV gerado

- Data: 2026-11-14
- Decisão: o teste `test_flash_sintetico_bloqueado` gera um vídeo com 10 alternâncias preto/branco por segundo (320×240, 30 fps, 2 s) via `cv2.VideoWriter` e verifica que `seguranca.medir_flashes()` o bloqueia (`ok: False`). O teste `test_flash_seguro_passa` gera um vídeo com cor constante (cinza 128) e confirma que passa.
- Motivo: testar a detecção de flashes sem depender de vídeos externos, com total reprodutibilidade.

## D031 — Mosaico LEGO procedural (CPU + k-means + pinos 3D)

- Data: 2026-11-14
- Decisão: implementar o estilo LEGO em `tecnicas/lego.py` reduzindo a imagem para 80 colunas, quantizando via k-means com ancoragem na paleta clássica de 16 cores LEGO e ampliando com interpolação nearest-neighbor, desenhando pinos circulares com brilho e sombra direcional.
- Motivo: atende integralmente à Seção 7 do Prompt Mestre com 100% de processamento local em CPU e respeito estrito ao limite de paleta.

## D032 — Traço Anime com XDoG e cel-shading bilateral

- Data: 2026-11-14
- Decisão: implementar `tecnicas/anime.py` usando XDoG (Extended Difference of Gaussians) com parâmetros $\sigma=0.6, \kappa=1.6, \gamma=0.97, \epsilon=-0.05$ seguido de filtro bilateral no espaço Lab e quantização em 10 cores com realce sutil de saturação.
- Motivo: produzir traços nítidos contínuos e blocos planos de cor típicos de animação tradicional japonesa sem necessidade de redes de difusão.

## D033 — Cartoon 3D estilizado com rampa toon e inverted hull

- Data: 2026-11-14
- Decisão: implementar `tecnicas/cartoon.py` estimando normais de superfície e aplicando sombreamento difuso quantizado em rampa de 4 patamares (0.35, 0.55, 0.80, 1.0) análogo ao MeshToonMaterial, com silhueta escura calculada por detecção de ângulo rasante de visão e descontinuidade de profundidade (inverted hull).
- Motivo: reproduzir o visual de malha 3D toon do Three.js de forma ultra-rápida em CPU.

## D034 — 3D PBR com luz direcional, oclusão ambiental e DoF

- Data: 2026-11-14
- Decisão: implementar `tecnicas/tres_d.py` com cálculo de normais e mapa de oclusão ambiental (AO) por concavidade local, iluminação mista (luz solar direta pontual + iluminação ambiente hemisférica céu/chão), reflexos especulares físicos microfacet e profundidade de campo (DoF/bokeh suave).
- Motivo: entregar renderização 3D PBR com sombras comprovadas sem difusão e com tempo de processamento inferior a 25 s por trecho de 5 s.

## D035 — Orquestrador procedural unificado (pipeline/render_procedural.py)

- Data: 2026-11-14
- Decisão: unificar o processamento dos 4 estilos procedurais em `pipeline/render_procedural.py` com pool de threads multithreading para paralelismo de quadros na CPU, compartilhando a montagem de áudio sincronizado e codificação FFmpeg do `render_stick`.
- Motivo: consistência de pipeline, modularidade e reaproveitamento dos padrões já validados no M2.
