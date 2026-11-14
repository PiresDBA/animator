import { Film, Sparkles, User } from 'lucide-react'
import type { Cena, MapaTecnicas } from '../types'
import { rotuloEstilo } from '../format'

/**
 * Storyboard: um cartao por cena com a tecnica escolhida e o motivo.
 * Os dados vem de /api/projetos/{id} -> mapa_tecnicas.
 */
export default function Storyboard({
  cenas,
  mapa,
}: {
  cenas: Cena[]
  mapa: MapaTecnicas | null
}) {
  const cenasMapa = mapa?.cenas ?? []
  if (cenasMapa.length === 0) {
    return (
      <p className="rounded-lg border border-base-700 bg-base-900 px-3 py-4 text-sm text-slate-400">
        O storyboard aparece depois que o roteador de técnicas roda. Ele escolhe, cena a cena,
        a técnica mais adequada e explica o motivo.
      </p>
    )
  }

  const descricaoCena = (id: string): string => {
    const c = cenas.find((x) => x.id === id) as Record<string, unknown> | undefined
    if (!c) return ''
    const campos = ['descricao', 'texto', 'resumo', 'legenda']
    for (const campo of campos) {
      const valor = c[campo]
      if (typeof valor === 'string' && valor.trim()) return valor
    }
    return ''
  }

  return (
    <ol className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {cenasMapa.map((c, i) => {
        const descricao = descricaoCena(c.id)
        return (
          <li key={c.id} className="cartao flex flex-col gap-2 p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="chip font-mono text-slate-300">{c.id}</span>
              <span className="chip border-acento/40 bg-acento/10 text-acento">
                <Sparkles size={12} aria-hidden="true" />
                {rotuloEstilo(c.tecnica)}
              </span>
            </div>
            {descricao && (
              <p className="line-clamp-3 text-sm text-slate-300">{descricao}</p>
            )}
            <p className="flex items-start gap-2 rounded-lg bg-base-900 px-3 py-2 text-xs text-slate-400">
              <User size={13} className="mt-0.5 shrink-0 text-slate-500" aria-hidden="true" />
              <span>
                <span className="font-medium text-slate-300">Por que esta técnica: </span>
                {c.motivo || 'Sem motivo registrado.'}
              </span>
            </p>
            <span className="mt-auto flex items-center gap-1 text-[11px] text-slate-600">
              <Film size={12} aria-hidden="true" /> Cena {i + 1} de {cenasMapa.length}
            </span>
          </li>
        )
      })}
    </ol>
  )
}
