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

## Pendências de decisão

- Definir se o EffectCraft entra no piloto do M5/M6.
- Manter o DreamShaper 8 fora até a licença dos pesos ser esclarecida.
- Se houver distribuição do projeto, substituir o YOLOv8n-pose por alternativa
  permissiva e revisar as obrigações GPL do FFmpeg e AGPL do YOLO.
