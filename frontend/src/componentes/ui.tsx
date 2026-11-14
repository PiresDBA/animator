import type { ReactNode } from 'react'
import { Inbox, Loader2, TriangleAlert } from 'lucide-react'

export function Esqueleto({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-base-800 ${className}`}
      aria-hidden="true"
    />
  )
}

export function EsqueletoCartao({ linhas = 3 }: { linhas?: number }) {
  return (
    <div className="cartao p-4" role="status" aria-label="Carregando">
      <Esqueleto className="h-4 w-2/5" />
      <div className="mt-3 space-y-2">
        {Array.from({ length: linhas }).map((_, i) => (
          <Esqueleto key={i} className={`h-3 ${i % 2 === 0 ? 'w-full' : 'w-4/5'}`} />
        ))}
      </div>
      <span className="sr-only">Carregando conteúdo</span>
    </div>
  )
}

export function EsqueletoGrade({ quantidade = 4 }: { quantidade?: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3" role="status">
      {Array.from({ length: quantidade }).map((_, i) => (
        <div key={i} className="cartao overflow-hidden">
          <Esqueleto className="h-36 w-full rounded-none" />
          <div className="space-y-2 p-4">
            <Esqueleto className="h-4 w-3/5" />
            <Esqueleto className="h-3 w-2/3" />
          </div>
        </div>
      ))}
      <span className="sr-only">Carregando</span>
    </div>
  )
}

export function EstadoVazio({
  titulo,
  descricao,
  acao,
  icone,
}: {
  titulo: string
  descricao: string
  acao?: ReactNode
  icone?: ReactNode
}) {
  return (
    <div className="cartao flex flex-col items-center gap-3 px-6 py-12 text-center">
      <div className="grid h-12 w-12 place-items-center rounded-full bg-base-800 text-slate-400">
        {icone ?? <Inbox size={22} aria-hidden="true" />}
      </div>
      <h3 className="text-base font-semibold text-slate-100">{titulo}</h3>
      <p className="max-w-md text-sm text-slate-400">{descricao}</p>
      {acao}
    </div>
  )
}

export function AvisoErro({
  mensagem,
  acao,
}: {
  mensagem: string
  acao?: ReactNode
}) {
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-100"
    >
      <TriangleAlert size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        <p className="break-words">{mensagem}</p>
        {acao && <div className="mt-2">{acao}</div>}
      </div>
    </div>
  )
}

export function AvisoInfo({
  mensagem,
  titulo,
}: {
  mensagem: string
  titulo?: string
}) {
  return (
    <div
      role="note"
      className="rounded-xl border border-acento/30 bg-acento/10 px-4 py-3 text-sm text-slate-200"
    >
      {titulo && <p className="mb-1 font-semibold text-acento">{titulo}</p>}
      <p className="break-words">{mensagem}</p>
    </div>
  )
}

export function Carregando({ texto = 'Carregando' }: { texto?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-400" role="status">
      <Loader2 size={16} className="animate-spin" aria-hidden="true" />
      {texto}…
    </div>
  )
}

export function TituloSecao({
  titulo,
  descricao,
  acao,
}: {
  titulo: string
  descricao?: string
  acao?: ReactNode
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">{titulo}</h1>
        {descricao && <p className="mt-1 max-w-3xl text-sm text-slate-400">{descricao}</p>}
      </div>
      {acao}
    </div>
  )
}
