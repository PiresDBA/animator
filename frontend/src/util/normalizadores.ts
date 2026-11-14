/**
 * Normalizadores defensivos: o backend e construido em paralelo e a forma
 * exata de `hardware`, `programas` e `fila` em /api/estado pode variar.
 * Aqui convertemos qualquer payload para um formato estavel de interface.
 */

import type { Job, ProjetoMeta } from '../types'
import { rotuloEstilo } from '../format'

export interface InfoGpu {
  nome: string
  vramTotalMib: number | null
  vramUsadaMib: number | null
  temperaturaC: number | null
  utilizacaoPct: number | null
}

export interface InfoHardware {
  cpuNome: string | null
  nucleos: number | null
  threads: number | null
  ramGb: number | null
  gpus: InfoGpu[]
  discoLivreGb: number | null
  sistema: string | null
}

export interface InfoPrograma {
  nome: string
  caminho: string | null
  detalhe: string | null
  disponivel: boolean
}

export interface AmostraHardware {
  tempo: number
  temperaturaC: number | null
  vramUsadaMib: number | null
  utilizacaoPct: number | null
}

function comoObjeto(valor: unknown): Record<string, unknown> | null {
  if (valor && typeof valor === 'object' && !Array.isArray(valor)) {
    return valor as Record<string, unknown>
  }
  return null
}

function numero(valor: unknown): number | null {
  return typeof valor === 'number' && Number.isFinite(valor) ? valor : null
}

function texto(valor: unknown): string | null {
  return typeof valor === 'string' && valor.trim() ? valor : null
}

/* ------------------------------------------------------------------ */
/* Hardware                                                            */
/* ------------------------------------------------------------------ */

function lerGpu(bruto: unknown): InfoGpu | null {
  const o = comoObjeto(bruto)
  if (!o) return null
  const nome = texto(o.nome) ?? texto(o.modelo) ?? 'GPU'
  const vramTotal =
    numero(o.vram_total_mib) ?? numero(o.vram_total_mb) ?? numero(o.vram_total)
  const vramUsada =
    numero(o.vram_usada_mib) ?? numero(o.vram_used_mib) ?? numero(o.vram_usada)
  const temperatura =
    numero(o.temperatura_c) ?? numero(o.temperature_c) ?? numero(o.temperatura)
  const utilizacao =
    numero(o.utilizacao_pct) ?? numero(o.utilization_pct) ?? numero(o.utilizacao)
  return {
    nome,
    vramTotalMib: vramTotal,
    vramUsadaMib: vramUsada,
    temperaturaC: temperatura,
    utilizacaoPct: utilizacao,
  }
}

export function normalizarHardware(bruto: unknown): InfoHardware {
  const vazio: InfoHardware = {
    cpuNome: null,
    nucleos: null,
    threads: null,
    ramGb: null,
    gpus: [],
    discoLivreGb: null,
    sistema: null,
  }
  const raiz = comoObjeto(bruto)
  if (!raiz) return vazio

  const cpu = comoObjeto(raiz.cpu) ?? comoObjeto(raiz.processador)
  const computador = comoObjeto(raiz.computador) ?? comoObjeto(raiz.computer)
  const sistema = comoObjeto(raiz.sistema) ?? comoObjeto(raiz.so)

  const gpus: InfoGpu[] = []
  const listaGpus =
    raiz.gpus ?? (comoObjeto(raiz.gpu) ?? comoObjeto(raiz.gpu_info))?.gpus
  if (Array.isArray(listaGpus)) {
    for (const item of listaGpus) {
      const g = lerGpu(item)
      if (g) gpus.push(g)
    }
  }
  if (gpus.length === 0) {
    const gpuUnico = lerGpu(raiz.gpu ?? raiz.gpu_info)
    if (gpuUnico) gpus.push(gpuUnico)
  }

  const discos = Array.isArray(raiz.discos) ? raiz.discos : []
  const livre = discos
    .map((d) => numero(comoObjeto(d)?.livre_gb))
    .filter((n): n is number => n !== null)

  const discoLivre = livre.length ? Math.min(...livre) : null
  const ramBytes = numero(computador?.ram_bytes)
  const ramGb =
    numero(computador?.ram_gb) ?? (ramBytes !== null ? Math.round(ramBytes / 1024 ** 3) : null)

  return {
    cpuNome: texto(cpu?.nome) ?? texto(cpu?.name),
    nucleos: numero(cpu?.nucleos) ?? numero(cpu?.cores),
    threads: numero(cpu?.threads) ?? numero(cpu?.threads_logicos),
    ramGb,
    gpus,
    discoLivreGb: discoLivre,
    sistema: texto(sistema?.caption) ?? texto(sistema?.nome),
  }
}

/* ------------------------------------------------------------------ */
/* Programas                                                           */
/* ------------------------------------------------------------------ */

export function normalizarProgramas(bruto: unknown): InfoPrograma[] {
  const saida: InfoPrograma[] = []
  const empurrar = (chave: string, valor: unknown) => {
    if (Array.isArray(valor)) {
      for (const item of valor) {
        const o = comoObjeto(item)
        if (!o) continue
        saida.push({
          nome: texto(o.tipo) ?? texto(o.nome) ?? texto(o.id) ?? chave,
          caminho: texto(o.caminho) ?? texto(o.path) ?? texto(o.local),
          detalhe: texto(o.evidencia) ?? texto(o.versao) ?? texto(o.observacao),
          disponivel: o.disponivel !== false,
        })
      }
      return
    }
    const o = comoObjeto(valor)
    if (!o) return
    saida.push({
      nome: texto(o.nome) ?? texto(o.tipo) ?? chave,
      caminho: texto(o.caminho) ?? texto(o.path) ?? texto(o.local),
      detalhe: texto(o.evidencia) ?? texto(o.versao) ?? texto(o.observacao),
      disponivel: o.disponivel !== false,
    })
  }

  if (Array.isArray(bruto)) {
    bruto.forEach((item) => {
      const o = comoObjeto(item)
      if (!o) return
      saida.push({
        nome: texto(o.tipo) ?? texto(o.nome) ?? texto(o.id) ?? 'Programa',
        caminho: texto(o.caminho) ?? texto(o.path) ?? texto(o.local),
        detalhe: texto(o.evidencia) ?? texto(o.versao) ?? texto(o.observacao),
        disponivel: o.disponivel !== false,
      })
    })
  } else {
    const o = comoObjeto(bruto)
    if (o) {
      const itens = o.resultados ?? o.itens ?? o.programas
      if (Array.isArray(itens)) {
        return normalizarProgramas(itens)
      }
      for (const [chave, valor] of Object.entries(o)) {
        empurrar(chave, valor)
      }
    }
  }
  return saida
}

/* ------------------------------------------------------------------ */
/* Fila                                                                */
/* ------------------------------------------------------------------ */

export function normalizarFila(bruto: unknown): Job[] {
  const lista = Array.isArray(bruto) ? bruto : Array.isArray(comoObjeto(bruto)?.jobs) ? (comoObjeto(bruto)?.jobs as unknown[]) : []
  return lista
    .map((item) => {
      const o = comoObjeto(item)
      if (!o) return null
      const id = texto(o.id) ?? texto(o.job_id)
      if (!id) return null
      return {
        id,
        tipo: texto(o.tipo) ?? texto(o.type) ?? 'tarefa',
        projeto: texto(o.projeto) ?? texto(o.project) ?? '',
        status: texto(o.status) ?? 'na_fila',
        progresso: numero(o.progresso) ?? numero(o.progress) ?? 0,
        mensagem: texto(o.mensagem) ?? texto(o.message) ?? '',
        criado_em: texto(o.criado_em) ?? texto(o.created_at) ?? '',
        finished_em: texto(o.finished_em) ?? texto(o.finished_at),
      } satisfies Job
    })
    .filter((j): j is Job => j !== null)
}

/* ------------------------------------------------------------------ */
/* Projetos                                                            */
/* ------------------------------------------------------------------ */

export function normalizarProjetos(bruto: unknown): ProjetoMeta[] {
  if (!Array.isArray(bruto)) return []
  return bruto.map((item) => {
    const o = comoObjeto(item) ?? {}
    const estilosBrutos = Array.isArray(o.estilos) ? o.estilos : []
    return {
      versao: numero(o.versao) ?? 1,
      id: texto(o.id) ?? '',
      nome: texto(o.nome) ?? texto(o.name) ?? 'Projeto sem nome',
      criado_em: texto(o.criado_em) ?? '',
      atualizado_em: texto(o.atualizado_em) ?? '',
      entrada: {
        video: texto(comoObjeto(o.entrada)?.video) ?? '',
        sha256: texto(comoObjeto(o.entrada)?.sha256) ?? '',
        duracao_s: numero(comoObjeto(o.entrada)?.duracao_s) ?? 0,
      },
      status: texto(o.status) ?? 'desconhecido',
      estilos: estilosBrutos.map((e) => {
        const eo = comoObjeto(e) ?? {}
        const id = texto(eo.id) ?? 'estilo'
        return {
          id,
          rotulo: texto(eo.rotulo) ?? rotuloEstilo(id),
          disponivel: eo.disponivel === true,
          motivo: texto(eo.motivo),
        }
      }),
      tentativas: (comoObjeto(o.tentativas) as Record<string, number>) ?? {},
      limite_tentativas: numero(o.limite_tentativas) ?? 3,
      aprovado: o.aprovado === true,
      aprovacao: o.aprovacao ?? null,
    }
  })
}
