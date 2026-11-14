import { useMemo, useState } from 'react'
import { Filter, Trash2, Terminal } from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { formatarDataHoraCurta } from '../format'

const NIVEIS = ['todos', 'info', 'aviso', 'erro'] as const
type Nivel = (typeof NIVEIS)[number]

const CORES: Record<string, string> = {
  info: 'text-slate-300',
  aviso: 'text-amber-300',
  erro: 'text-rose-300',
}

export default function LogAoVivo({ limite = 200 }: { limite?: number }) {
  const { eventos, limparEventos } = useEstudio()
  const [nivel, setNivel] = useState<Nivel>('todos')

  const filtrados = useMemo(() => {
    const base = nivel === 'todos' ? eventos : eventos.filter((e) => e.nivel === nivel)
    return base.slice(0, limite)
  }, [eventos, nivel, limite])

  const contagens = useMemo(
    () => ({
      info: eventos.filter((e) => e.nivel === 'info').length,
      aviso: eventos.filter((e) => e.nivel === 'aviso').length,
      erro: eventos.filter((e) => e.nivel === 'erro').length,
    }),
    [eventos],
  )

  return (
    <section className="cartao overflow-hidden" aria-label="Log ao vivo">
      <header className="flex flex-wrap items-center gap-3 border-b border-base-800 px-4 py-2">
        <span className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <Terminal size={15} className="text-acento" aria-hidden="true" />
          Log ao vivo
        </span>
        <span className="text-[11px] text-slate-500">
          {contagens.info} info · {contagens.aviso} aviso · {contagens.erro} erro
        </span>
        <div className="ml-auto flex items-center gap-2">
          <span className="flex items-center gap-1 text-[11px] text-slate-400">
            <Filter size={13} aria-hidden="true" /> Nível
          </span>
          <div className="flex gap-1" role="group" aria-label="Filtrar log por nível">
            {NIVEIS.map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setNivel(n)}
                aria-pressed={nivel === n}
                className={[
                  'rounded-md px-2 py-1 text-[11px] font-medium capitalize transition-colors',
                  nivel === n
                    ? 'bg-acento text-base-950'
                    : 'bg-base-800 text-slate-300 hover:bg-base-700',
                ].join(' ')}
              >
                {n}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="rounded-md p-1.5 text-slate-400 hover:bg-base-800 hover:text-slate-100"
            onClick={limparEventos}
            aria-label="Limpar log"
            title="Limpar log"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </header>

      <div className="max-h-[320px] overflow-y-auto px-4 py-2 font-mono text-xs">
        {filtrados.length === 0 ? (
          <p className="py-6 text-center text-slate-500">
            Nenhum evento por enquanto. Os logs do pipeline aparecem aqui em tempo real.
          </p>
        ) : (
          <ul className="space-y-0.5">
            {filtrados.map((e) => (
              <li key={e.id} className="flex gap-3">
                <span className="shrink-0 text-slate-600">{formatarDataHoraCurta(e.timestamp)}</span>
                <span
                  className={`w-12 shrink-0 uppercase ${CORES[e.nivel] ?? 'text-slate-400'}`}
                >
                  {e.nivel}
                </span>
                <span className="min-w-0 break-words text-slate-300">{e.mensagem}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
