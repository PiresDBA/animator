import { Star } from 'lucide-react'
import { ROTULO_CRITERIO, type Criterio } from '../types'

export default function Estrelas({
  criterio,
  valor,
  aoMudar,
  leitura = false,
}: {
  criterio: Criterio
  valor: number
  aoMudar?: (valor: number) => void
  leitura?: boolean
}) {
  return (
    <div className="flex items-center justify-between gap-3 py-1">
      <span id={`rot-${criterio}`} className="text-sm text-slate-300">
        {ROTULO_CRITERIO[criterio]}
      </span>
      <div
        className="flex items-center gap-0.5"
        role={leitura ? 'img' : 'radiogroup'}
        aria-labelledby={`rot-${criterio}`}
        aria-label={leitura ? `${ROTULO_CRITERIO[criterio]}: ${valor} de 5` : undefined}
      >
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            disabled={leitura || !aoMudar}
            onClick={() => aoMudar?.(n)}
            aria-label={`${ROTULO_CRITERIO[criterio]}: ${n} de 5`}
            aria-checked={!leitura ? valor === n : undefined}
            role={leitura ? undefined : 'radio'}
            className={[
              'rounded p-0.5 transition-colors',
              leitura ? 'cursor-default' : 'hover:bg-base-700',
              n <= valor ? 'text-amber-300' : 'text-base-500',
            ].join(' ')}
          >
            <Star
              size={18}
              fill={n <= valor ? 'currentColor' : 'none'}
              aria-hidden="true"
            />
          </button>
        ))}
        <span className="ml-2 w-4 text-right font-mono text-xs text-slate-400">{valor}/5</span>
      </div>
    </div>
  )
}
