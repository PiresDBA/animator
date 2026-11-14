# Contrato do M2 (primeiro estilo fim a fim: bonecos de palito)

Data: 2026-11-14. Este documento fixa os contratos de arquivo, CLI e API do M2.
Quem implementa (pipeline, backend, frontend) deve seguir este documento ao pé
da letra; mudanças de contrato exigem atualizar este arquivo.

## 1. Escopo do M2

- Entrada: vídeo local já analisado pelo M1 (JSON de análise validado pelo schema
  `pipeline/schemas/analise_v1.json`).
- Estilo habilitado: **bonecos de palito** (motor `stick-film`), render em CPU.
- Saída: prévia de 5 s com áudio original sincronizado, checagem de segurança
  (verde/amarelo/vermelho) e exibição na interface web.
- Regra do portão: **nenhum vídeo completo** é produzido no M2. O endpoint de
  vídeo completo responde 403 com o motivo "aguardando aprovação".

## 2. Layout de um projeto

    projetos/<id>/
      meta.json            # status, entrada, estilos, timestamps
      cenas.json           # cenas (copiado/derivado da análise)
      movimento.json       # métricas de movimento por amostra
      mapa_tecnicas.json   # técnica escolhida por cena + motivo
      previa.json          # prévias geradas (lista)
      avaliacoes.json      # decisões humanas
      receipt.json         # versão, hashes, parâmetros
      camadas/             # assets por cena
      saidas/              # prévia.mp4, miniatura.png, frames/, filme/

## 3. CLI do pipeline (invocado pelo backend como subprocesso)

Todos rodam com `.\.venv\Scripts\python.exe -m <modulo>` na raiz do projeto.

| Comando | Entrada | Saída | Código |
|---|---|---|---|
| `pipeline.analisar` | `--video PATH --saida PATH --previa-dir PATH` | JSON de análise | 0 |
| `pipeline.previa` | `--projeto ID --estilo bonecos [--trecho-inicio S] [--trecho-fim S] [--seed N] [--resolucao 480p]` | `previa.json` + `saidas/previa_<estilo>_<n>.mp4` + `saidas/miniatura_<estilo>_<n>.png` | 0 |
| `pipeline.seguranca` | `--video PATH --saida PATH [--descricao TEXTO]` | JSON de segurança | 0 |
| `pipeline.roteador` | `--projeto ID` | `mapa_tecnicas.json` | 0 |

Regras de CLI:

- Saída em stdout: uma linha `OK: <caminho>` em sucesso; `ERRO: <mensagem>` em
  falha (exit code 1). Nada de traceback no stdout.
- Todo caminho gravado em JSON é **relativo à raiz do projeto**, com `/`.
- Nenhum comando escreve fora de `projetos/<id>/`, `saidas/` ou `.cache/`.

## 4. Formatos dos JSONs do M2

### 4.1 `previa.json`

```json
{
  "versao": 1,
  "projeto": "id-do-projeto",
  "previa_id": "bonecos_001",
  "estilo": "bonecos",
  "estilo_rotulo": "Bonecos de palito",
  "status": "pronto",
  "arquivo": "projetos/id-do-projeto/saidas/previa_bonecos_001.mp4",
  "miniatura": "projetos/id-do-projeto/saidas/miniatura_bonecos_001.png",
  "trecho": {"inicio_s": 0.0, "fim_s": 5.0, "duracao_s": 5.0},
  "resolucao": "854x480",
  "fps": 30,
  "gerado_em": "2026-11-14T00:00:00+00:00",
  "tempo_geracao_s": 0.0,
  "seguranca": {
    "veredito": "verde",
    "flashes": {"max_flashes_1s": 0, "limite": 3, "ok": true},
    "volume": {"true_peak_dbtp": -7.2, "limite_dbtp": -6.0, "ok": true},
    "conteudo": {"classificacao": "infantil", "ok": true, "motivo": null},
    "mensagens": []
  },
  "mapa_tecnicas": {"cenas": [{"id": "c01", "tecnica": "bonecos", "motivo": "..."}]},
  "params": {"seed": 7, "resolucao": "480p", "modo": "rapido", "versao_preset": 1},
  "erro": null
}
```

`seguranca.veredito` ∈ `verde` | `amarelo` | `vermelho`.
`previa.status` ∈ `pronto` | `erro` | `rodando`.

### 4.2 `avaliacoes.json`

```json
{
  "versao": 1,
  "avaliacoes": [
    {
      "id": "av_001",
      "previa_id": "bonecos_001",
      "estilo": "bonecos",
      "data": "2026-11-14T00:00:00+00:00",
      "decisao": "aprovar",
      "notas": {"fidelidade": 4, "identidade_visual": 3, "fluidez": 4, "adequacao_infantil": 5, "clareza_historia": 4},
      "comentario": "texto opcional",
      "params": {"seed": 7, "resolucao": "480p", "modo": "rapido", "versao_preset": 1,
                 "trecho_inicio": 0.0, "trecho_fim": 5.0},
      "observacao_responsavel": null
    }
  ]
}
```

`decisao` ∈ `aprovar` | `ajustar` | `reprovar`.
`notas` ∈ 1..5 nas cinco chaves: `fidelidade`, `identidade_visual`, `fluidez`,
`adequacao_infantil`, `clareza_historia`.

### 4.3 `meta.json`

```json
{
  "versao": 1,
  "id": "id-do-projeto",
  "nome": "meu projeto",
  "criado_em": "...",
  "atualizado_em": "...",
  "entrada": {"video": "caminho/absoluto.mp4", "sha256": "...", "duracao_s": 60.0},
  "status": "analisado",
  "estilos": [{"id": "bonecos", "rotulo": "Bonecos de palito", "disponivel": true, "motivo": null},
              {"id": "lego", "rotulo": "Mosaico de blocos", "disponivel": false, "motivo": "disponível a partir do M4"}],
  "tentativas": {"bonecos": 0},
  "limite_tentativas": 3,
  "aprovado": false,
  "aprovacao": null
}
```

## 5. API HTTP (FastAPI, porta 8765)

Base: `http://127.0.0.1:8765`. Respostas em JSON UTF-8. Erros no formato
`{"erro": "codigo", "mensagem": "texto em pt-BR"}`.

| Método | Rota | Entrada | Saída |
|---|---|---|---|
| GET | `/api/estado` | – | `{ "marco": "M2", "backend": "ok", "fila": {...}, "hardware": {...}, "programas": {...} }` |
| GET | `/api/projetos` | – | lista de `meta.json` |
| POST | `/api/projetos` | `{ "nome": str, "video": str }` | `meta.json` criado |
| GET | `/api/projetos/{id}` | – | `{ "meta": {...}, "cenas": [...], "previa": {...}, "avaliacoes": [...], "mapa_tecnicas": {...} }` |
| POST | `/api/projetos/{id}/analisar` | – | `{ "job_id": str }` |
| POST | `/api/projetos/{id}/previa` | `{ "estilo": str, "trecho_inicio": float, "trecho_fim": float, "seed": int, "resolucao": "480p" }` | `{ "job_id": str }` |
| GET | `/api/projetos/{id}/previas` | – | lista de prévias |
| POST | `/api/avaliacoes` | objeto da seção 4.2 | avaliação salva |
| POST | `/api/projetos/{id}/completo` | – | **403** `{"erro":"sem_aprovacao","mensagem":"Nenhum estilo aprovado..."}` |
| GET | `/api/fila` | – | lista de jobs `{ id, tipo, projeto, status, progresso, mensagem, criado_em, finished_em }` |
| POST | `/api/fila/{job_id}/cancelar` | – | job cancelado |
| GET | `/api/eventos` | WebSocket | eventos `{ "tipo": "log"|"job"|"previa", ... }` |

Fila: SQLite em `backend/fila.sqlite3`. Estados de job: `na_fila`, `rodando`,
`pronto`, `erro`, `cancelado`. WebSocket envia log por nível
(`info`/`aviso`/`erro`) e atualização de job.

## 6. Frontend (React + Vite + TypeScript + Tailwind)

- Vite em `frontend/`, porta de dev 5173, build em `frontend/dist/`.
- O backend serve `frontend/dist/` como estático quando o build existe.
- Dependências: react 18, react-dom 18, typescript 5, vite 5, tailwindcss 3.4,
  lucide-react, recharts.
- Tema escuro por padrão, acento azul-ciano (`#22d3ee`), textos em pt-BR,
  formatação pt-BR, contraste WCAG AA, funciona a partir de 1366x768.
- Páginas: Início, Novo vídeo (4 passos: entrada, estilos, prévia, revisão),
  Prévias e avaliação, Vídeos completos, Projetos (linha do tempo do pipeline),
  Hardware (benchmark e monitor ao vivo), Programas, Fila, Configurações, Ajuda.
- Componentes obrigatórios: barra lateral recolhível; barra superior com status
  de hardware, programas e backend; cartões de estilo com selo de disponibilidade
  e motivo quando indisponível; linha do tempo com marcador de 5 s arrastável;
  grade de prévias; painel de decisão com três botões (Aprovar, Ajustar,
  Reprovar) e notas de 1 a 5 por estrela; gráfico de radar (notas), gráfico de
  barras (tempos), gráfico de linhas (temperatura e VRAM); storyboard com um
  cartão por cena (técnica + motivo); log ao vivo com filtro por nível; estados
  vazios e skeletons.
- "Gerar vídeo completo" fica bloqueado sem aprovação, com o motivo escrito.
- Nada de marca protegida em textos: "Mosaico de blocos", não "LEGO".

## 7. Projeto Remotion local

`remotion/` com `remotion` e `@remotion/cli` fixados em **4.0.542**.
Composições M2: `Miniatura` (1280x720, 1 quadro) e `Previa` (usa
`OffthreadVideo` sobre o MP4 da prévia). `delayRender`/`continueRender` para
imagens. Render de still para gerar a miniatura final.
