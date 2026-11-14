/**
 * Tipos do contrato M2 (docs/contrato_m2.md, secoes 4 e 5).
 * Campos que o backend ainda pode evolve sao mantidos como `unknown`
 * e normalizados na camada de apresentacao.
 */

/* ------------------------------------------------------------------ */
/* Projeto (meta.json - secao 4.3)                                     */
/* ------------------------------------------------------------------ */

export interface EstiloProjeto {
  id: string
  rotulo: string
  disponivel: boolean
  motivo: string | null
}

export interface EntradaProjeto {
  video: string
  sha256: string
  duracao_s: number
}

export interface ProjetoMeta {
  versao: number
  id: string
  nome: string
  criado_em: string
  atualizado_em: string
  entrada: EntradaProjeto
  status: string
  estilos: EstiloProjeto[]
  tentativas: Record<string, number>
  limite_tentativas: number
  aprovado: boolean
  aprovacao: unknown | null
}

/* ------------------------------------------------------------------ */
/* Previa (previa.json - secao 4.1)                                    */
/* ------------------------------------------------------------------ */

export interface TrechoPrevia {
  inicio_s: number
  fim_s: number
  duracao_s: number
}

export interface SegurancaFlashes {
  max_flashes_1s: number
  limite: number
  ok: boolean
}

export interface SegurancaVolume {
  true_peak_dbtp: number
  limite_dbtp: number
  ok: boolean
}

export interface SegurancaConteudo {
  classificacao: string
  ok: boolean
  motivo: string | null
}

export interface Seguranca {
  veredito: 'verde' | 'amarelo' | 'vermelho' | string
  flashes: SegurancaFlashes
  volume: SegurancaVolume
  conteudo: SegurancaConteudo
  mensagens: string[]
}

export interface ParamsPrevia {
  seed: number
  resolucao: string
  modo: string
  versao_preset: number
}

export interface CenaMapaTecnica {
  id: string
  tecnica: string
  motivo: string
}

export interface MapaTecnicas {
  cenas: CenaMapaTecnica[]
}

export interface Previa {
  versao: number
  projeto: string
  previa_id: string
  estilo: string
  estilo_rotulo: string
  status: 'pronto' | 'erro' | 'rodando' | string
  arquivo: string | null
  miniatura: string | null
  trecho: TrechoPrevia
  resolucao: string
  fps: number
  gerado_em: string
  tempo_geracao_s: number
  seguranca: Seguranca | null
  mapa_tecnicas: MapaTecnicas | null
  params: ParamsPrevia | null
  erro: string | null
}

/* ------------------------------------------------------------------ */
/* Avaliacao (avaliacoes.json - secao 4.2)                              */
/* ------------------------------------------------------------------ */

export type Decisao = 'aprovar' | 'ajustar' | 'reprovar'

export const CRITERIOS = [
  'fidelidade',
  'identidade_visual',
  'fluidez',
  'adequacao_infantil',
  'clareza_historia',
] as const

export type Criterio = (typeof CRITERIOS)[number]

export type Notas = Record<Criterio, number>

export const ROTULO_CRITERIO: Record<Criterio, string> = {
  fidelidade: 'Fidelidade ao original',
  identidade_visual: 'Identidade visual',
  fluidez: 'Fluidez da animação',
  adequacao_infantil: 'Adequação infantil',
  clareza_historia: 'Clareza da história',
}

export interface Avaliacao {
  id: string
  previa_id: string
  estilo: string
  data: string
  decisao: Decisao
  notas: Notas
  comentario: string
  params: Record<string, unknown> & {
    seed?: number
    resolucao?: string
    modo?: string
    versao_preset?: number
    trecho_inicio?: number
    trecho_fim?: number
  }
  observacao_responsavel: string | null
}

/** Envelope do arquivo avaliacoes.json (secao 4.2). */
export interface ArquivoAvaliacoes {
  versao: number
  avaliacoes: Avaliacao[]
}

/* ------------------------------------------------------------------ */
/* Cena e detalhe de projeto (secao 5)                                 */
/* ------------------------------------------------------------------ */

export interface Cena {
  id: string
  [campo: string]: unknown
}

export interface DetalheProjeto {
  meta: ProjetoMeta
  cenas: Cena[]
  previa: Previa | null
  avaliacoes: Avaliacao[]
  mapa_tecnicas: MapaTecnicas | null
}

/* ------------------------------------------------------------------ */
/* Fila (secao 5)                                                      */
/* ------------------------------------------------------------------ */

export type StatusJob = 'na_fila' | 'rodando' | 'pronto' | 'erro' | 'cancelado' | string

export interface Job {
  id: string
  tipo: string
  projeto: string
  status: StatusJob
  progresso: number
  mensagem: string
  criado_em: string
  finished_em: string | null
}

/* ------------------------------------------------------------------ */
/* Estado geral (secao 5)                                              */
/* ------------------------------------------------------------------ */

export interface Estado {
  marco: string
  backend: string
  fila: unknown
  hardware: unknown
  programas: unknown
}

/* ------------------------------------------------------------------ */
/* Eventos do WebSocket /api/eventos                                   */
/* ------------------------------------------------------------------ */

export interface EventoLog {
  id: string
  tipo: 'log' | 'job' | 'previa' | string
  nivel: 'info' | 'aviso' | 'erro' | string
  mensagem: string
  timestamp: string
  projeto?: string
}

/* ------------------------------------------------------------------ */
/* Estilos da interface (estilos/*.json)                               */
/* ------------------------------------------------------------------ */

export interface EstiloCatalogo {
  id: string
  rotulo: string
  descricao: string
  disponivel: boolean
  motivo: string | null
}
