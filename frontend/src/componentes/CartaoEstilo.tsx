import { Check, Lock, Ban } from 'lucide-react'
import type { EstiloProjeto } from '../types'

export default function CartaoEstilo({
  estilo,
  selecionado,
  tentativas = 0,
  limiteTentativas = 3,
  onSelecionar,
}: {
  estilo: EstiloProjeto
  selecionado?: boolean
  tentativas?: number
  limiteTentativas?: number
  onSelecionar?: (id: string) => void
}) {
  const bloqueado = !estilo.disponivel
  const esgotado = tentativas >= limiteTentativas
  const podeSelecionar = !bloqueado && !esgotado && Boolean(onSelecionar)

  return (
    <div
      className={[
        'cartao cartao-interativo flex flex-col gap-3 p-4',
        selecionado ? 'border-acento ring-1 ring-acento/50' : '',
        bloqueado ? 'opacity-70' : '',
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-slate-100">{estilo.rotulo}</h3>
          <p className="mt-0.5 font-mono text-[11px] text-slate-500">{estilo.id}</p>
        </div>
        {estilo.disponivel ? (
          <span className="chip border-emerald-500/40 bg-emerald-500/10 text-emerald-300">
            <Check size={12} aria-hidden="true" /> Disponível
          </span>
        ) : (
          <span className="chip border-amber-500/40 bg-amber-500/10 text-amber-300">
            <Ban size={12} aria-hidden="true" /> Indisponível
          </span>
        )}
      </div>

      {estilo.motivo && (
        <p className="flex items-start gap-2 rounded-lg border border-base-700 bg-base-900 px-3 py-2 text-xs text-slate-400">
          <Lock size={13} className="mt-0.5 shrink-0 text-amber-400" aria-hidden="true" />
          <span>{estilo.motivo}</span>
        </p>
      )}

      <div className="mt-auto flex items-center justify-between gap-2">
        <span className="text-[11px] text-slate-500">
          Tentativas: {tentativas}/{limiteTentativas}
        </span>
        <button
          type="button"
          className={selecionado ? 'botao-primario' : 'botao-secundario'}
          disabled={!podeSelecionar}
          onClick={() => onSelecionar?.(estilo.id)}
          aria-pressed={Boolean(selecionado)}
        >
          {selecionado ? 'Selecionado' : bloqueado ? 'Bloqueado' : esgotado ? 'Limite atingido' : 'Selecionar'}
        </button>
      </div>
    </div>
  )
}
