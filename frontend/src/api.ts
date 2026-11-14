/**
 * Cliente HTTP do backend local (contrato M2, secao 5).
 *
 * Base: variavel de ambiente VITE_API_BASE (padrao http://127.0.0.1:8765).
 * Erros do backend: {"erro": "codigo", "mensagem": "texto em pt-BR"}.
 */

import type {
  ArquivoAvaliacoes,
  Avaliacao,
  DetalheProjeto,
  Estado,
  Job,
  Previa,
  ProjetoMeta,
} from './types'

export const API_BASE = (
  import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8765'
).replace(/\/+$/, '')

const CHAVE_BASE_MIDIA = 'estudio.baseMidia'

/** Base usada para servir arquivos de midia (mp4/png) do backend. */
export function baseMidia(): string {
  const salvo = localStorage.getItem(CHAVE_BASE_MIDIA)
  return (salvo || API_BASE).replace(/\/+$/, '')
}

export function definirBaseMidia(valor: string): void {
  if (!valor.trim()) localStorage.removeItem(CHAVE_BASE_MIDIA)
  else localStorage.setItem(CHAVE_BASE_MIDIA, valor.trim().replace(/\/+$/, ''))
}

/** URL absoluta de um arquivo relativo a raiz do projeto. */
export function urlMidia(caminho: string | null | undefined): string | null {
  if (!caminho) return null
  if (/^https?:\/\//i.test(caminho)) return caminho
  const limpo = caminho.replace(/\\/g, '/').replace(/^\/+/, '')
  return `${baseMidia()}/${limpo}`
}

/* ------------------------------------------------------------------ */
/* Erros                                                               */
/* ------------------------------------------------------------------ */

export class ErroApi extends Error {
  readonly status: number
  readonly codigo: string

  constructor(status: number, codigo: string, mensagem: string) {
    super(mensagem)
    this.name = 'ErroApi'
    this.status = status
    this.codigo = codigo
  }

  /** Verdadeiro quando o erro e de rede (backend fora do ar). */
  get offline(): boolean {
    return this.status === 0
  }
}

/* ------------------------------------------------------------------ */
/* Nucleo                                                              */
/* ------------------------------------------------------------------ */

async function request<T>(caminho: string, init: RequestInit = {}): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(`${API_BASE}${caminho}`, {
      headers: {
        Accept: 'application/json',
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...(init.headers ?? {}),
      },
      ...init,
    })
  } catch (e) {
    throw new ErroApi(
      0,
      'rede',
      'Não foi possível falar com o backend. Verifique se o serviço está rodando.',
    )
  }

  const texto = await resposta.text()
  let corpo: unknown = null
  if (texto) {
    try {
      corpo = JSON.parse(texto)
    } catch {
      corpo = texto
    }
  }

  if (!resposta.ok) {
    const obj = (corpo ?? {}) as { erro?: string; mensagem?: string }
    throw new ErroApi(
      resposta.status,
      obj.erro ?? `http_${resposta.status}`,
      obj.mensagem ?? `A requisição falhou (HTTP ${resposta.status}).`,
    )
  }
  return corpo as T
}

/* ------------------------------------------------------------------ */
/* Endpoints                                                           */
/* ------------------------------------------------------------------ */

export const api = {
  estado(): Promise<Estado> {
    return request<Estado>('/api/estado')
  },

  projetos(): Promise<ProjetoMeta[]> {
    return request<ProjetoMeta[]>('/api/projetos')
  },

  criarProjeto(nome: string, video: string): Promise<ProjetoMeta> {
    return request<ProjetoMeta>('/api/projetos', {
      method: 'POST',
      body: JSON.stringify({ nome, video }),
    })
  },

  projeto(id: string): Promise<DetalheProjeto> {
    return request<DetalheProjeto>(`/api/projetos/${encodeURIComponent(id)}`)
  },

  analisar(id: string): Promise<{ job_id: string }> {
    return request<{ job_id: string }>(
      `/api/projetos/${encodeURIComponent(id)}/analisar`,
      { method: 'POST' },
    )
  },

  previa(
    id: string,
    corpo: {
      estilo: string
      trecho_inicio: number
      trecho_fim: number
      seed: number
      resolucao: string
    },
  ): Promise<{ job_id: string }> {
    return request<{ job_id: string }>(
      `/api/projetos/${encodeURIComponent(id)}/previa`,
      { method: 'POST', body: JSON.stringify(corpo) },
    )
  },

  previas(id: string): Promise<Previa[]> {
    return request<Previa[]>(`/api/projetos/${encodeURIComponent(id)}/previas`)
  },

  /**
   * Salva uma avaliacao. O contrato (secao 5) pede "objeto da secao 4.2";
   * enviamos o objeto de avaliacao (um item de `avaliacoes`) e o envelope
   * completo fica disponivel em `arquivoAvaliacoes` para quem precisar.
   */
  salvarAvaliacao(avaliacao: Avaliacao): Promise<Avaliacao> {
    return request<Avaliacao>('/api/avaliacoes', {
      method: 'POST',
      body: JSON.stringify(avaliacao),
    })
  },

  arquivoAvaliacoes(projetoId: string): Promise<ArquivoAvaliacoes> {
    return request<ArquivoAvaliacoes>(
      `/api/projetos/${encodeURIComponent(projetoId)}/avaliacoes`,
    )
  },

  /** Bloqueado com 403 "sem_aprovacao" enquanto nenhum estilo for aprovado. */
  gerarCompleto(id: string): Promise<{ ok: boolean }> {
    return request<{ ok: boolean }>(
      `/api/projetos/${encodeURIComponent(id)}/completo`,
      { method: 'POST' },
    )
  },

  fila(): Promise<Job[]> {
    return request<Job[]>('/api/fila')
  },

  cancelarJob(jobId: string): Promise<Job> {
    return request<Job>(`/api/fila/${encodeURIComponent(jobId)}/cancelar`, {
      method: 'POST',
    })
  },
}

/* ------------------------------------------------------------------ */
/* WebSocket de eventos                                                */
/* ------------------------------------------------------------------ */

export type NivelEvento = 'info' | 'aviso' | 'erro'

export interface EventoRecebido {
  tipo: 'log' | 'job' | 'previa' | string
  nivel?: NivelEvento | string
  mensagem?: string
  texto?: string
  projeto?: string
  [campo: string]: unknown
}

export function urlEventos(): string {
  const base = API_BASE.replace(/^http/, 'ws')
  return `${base}/api/eventos`
}
