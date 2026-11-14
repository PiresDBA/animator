import { useCallback, useEffect, useRef, useState } from 'react'
import { GripVertical } from 'lucide-react'
import { formatarTempo } from '../format'

/**
 * Linha do tempo com marcador arrastavel do trecho de 5 s.
 * O marcador pode ser movido pelo mouse, pelo teclado (setas) ou pelo
 * campo numerico, respeitando o limite de tentativas.
 */
export default function LinhaDoTempo({
  duracaoTotal,
  inicio,
  duracaoPrevia = 5,
  onChange,
}: {
  duracaoTotal: number
  inicio: number
  duracaoPrevia?: number
  onChange: (inicio: number) => void
}) {
  const trilhoRef = useRef<HTMLDivElement | null>(null)
  const [arrastando, setArrastando] = useState(false)
  const [posicaoLocal, setPosicaoLocal] = useState(inicio)

  useEffect(() => {
    if (!arrastando) setPosicaoLocal(inicio)
  }, [inicio, arrastando])

  const duracaoSegura = Math.max(duracaoTotal, duracaoPrevia)
  const maxInicio = Math.max(0, duracaoSegura - duracaoPrevia)

  const posicao = Math.min(Math.max(posicaoLocal, 0), maxInicio)
  const percentual = duracaoSegura > 0 ? (posicao / duracaoSegura) * 100 : 0
  const larguraTrecho = duracaoSegura > 0 ? (duracaoPrevia / duracaoSegura) * 100 : 0

  const aplicar = useCallback(
    (novo: number) => {
      const limitado = Math.min(Math.max(novo, 0), maxInicio)
      setPosicaoLocal(limitado)
      onChange(Number(limitado.toFixed(2)))
    },
    [maxInicio, onChange],
  )

  const aoMover = useCallback(
    (clientX: number) => {
      const trilho = trilhoRef.current
      if (!trilho) return
      const caixa = trilho.getBoundingClientRect()
      if (caixa.width === 0) return
      const proporcao = (clientX - caixa.left) / caixa.width
      aplicar(proporcao * duracaoSegura)
    },
    [aplicar, duracaoSegura],
  )

  useEffect(() => {
    if (!arrastando) return
    const aoMoverMouse = (e: MouseEvent) => aoMover(e.clientX)
    const aoMoverToque = (e: TouchEvent) => {
      const toque = e.touches[0]
      if (toque) aoMover(toque.clientX)
    }
    const aoSoltar = () => setArrastando(false)
    window.addEventListener('mousemove', aoMoverMouse)
    window.addEventListener('touchmove', aoMoverToque, { passive: true })
    window.addEventListener('mouseup', aoSoltar)
    window.addEventListener('touchend', aoSoltar)
    return () => {
      window.removeEventListener('mousemove', aoMoverMouse)
      window.removeEventListener('touchmove', aoMoverToque)
      window.removeEventListener('mouseup', aoSoltar)
      window.removeEventListener('touchend', aoSoltar)
    }
  }, [arrastando, aoMover])

  const aoTeclado = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    const passo = e.shiftKey ? 5 : 0.5
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      aplicar(posicao - passo)
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      aplicar(posicao + passo)
    } else if (e.key === 'Home') {
      e.preventDefault()
      aplicar(0)
    } else if (e.key === 'End') {
      e.preventDefault()
      aplicar(maxInicio)
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-3 text-xs text-slate-400">
        <span className="font-mono">00:00</span>
        <span>
          Trecho de {duracaoPrevia} s ·{' '}
          <span className="font-mono text-slate-200">
            {formatarTempo(posicao)} – {formatarTempo(posicao + duracaoPrevia)}
          </span>
        </span>
        <span className="font-mono">{formatarTempo(duracaoSegura)}</span>
      </div>

      <div
        ref={trilhoRef}
        className="relative h-12 w-full select-none rounded-lg border border-base-700 bg-base-900"
        onMouseDown={(e) => {
          if ((e.target as HTMLElement).closest('[data-alca]')) return
          setArrastando(true)
          aoMover(e.clientX)
        }}
      >
        {/* faixa do trecho selecionado */}
        <div
          className="absolute inset-y-0 rounded bg-acento/20"
          style={{
            left: `${percentual}%`,
            width: `${Math.min(larguraTrecho, 100 - percentual)}%`,
          }}
        />
        {/* marcador arrastavel */}
        <button
          type="button"
          data-alca="marcador"
          role="slider"
          aria-label="Início do trecho de prévia"
          aria-valuemin={0}
          aria-valuemax={Number(maxInicio.toFixed(2))}
          aria-valuenow={Number(posicao.toFixed(2))}
          aria-valuetext={`${formatarTempo(posicao)} até ${formatarTempo(posicao + duracaoPrevia)}`}
          onKeyDown={aoTeclado}
          onMouseDown={(e) => {
            e.stopPropagation()
            setArrastando(true)
          }}
          onTouchStart={(e) => {
            e.stopPropagation()
            setArrastando(true)
          }}
          className="absolute top-0 z-10 flex h-full w-6 -translate-x-1/2 cursor-grab items-center justify-center
            rounded border border-acento bg-acento/25 text-acento active:cursor-grabbing"
          style={{ left: `${percentual}%` }}
        >
          <GripVertical size={14} aria-hidden="true" />
        </button>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-400" htmlFor="inicio-trecho">
          Início (s)
        </label>
        <input
          id="inicio-trecho"
          type="number"
          min={0}
          max={Number(maxInicio.toFixed(2))}
          step={0.5}
          value={posicao.toFixed(1)}
          onChange={(e) => aplicar(Number(e.target.value))}
          className="campo w-28 py-1"
        />
        <span className="text-xs text-slate-500">
          Arraste o marcador ou use as setas do teclado (Shift = 5 s).
        </span>
      </div>
    </div>
  )
}
