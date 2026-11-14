import { useRef, useState } from 'react'
import { urlMidia } from '../api'
import { formatarData } from '../format'
import type { Previa } from '../types'
import { ImageOff, Play } from 'lucide-react'

/**
 * "Antes e depois" em slider: o video original fica a esquerda e a previa
 * a direita, com um divisor arrastavel.
 */
export default function SliderAntesDepois({
  antes,
  depois,
}: {
  antes: { rotulo: string; caminho: string | null }
  depois: { rotulo: string; caminho: string | null }
}) {
  const [posicao, setPosicao] = useState(50)
  const [arrastando, setArrastando] = useState(false)
  const caixaRef = useRef<HTMLDivElement | null>(null)

  const urlAntes = urlMidia(antes.caminho)
  const urlDepois = urlMidia(depois.caminho)

  const mover = (clientX: number) => {
    const caixa = caixaRef.current
    if (!caixa) return
    const r = caixa.getBoundingClientRect()
    if (r.width === 0) return
    const p = ((clientX - r.left) / r.width) * 100
    setPosicao(Math.min(100, Math.max(0, p)))
  }

  const onMouseDown = (e: React.MouseEvent) => {
    setArrastando(true)
    mover(e.clientX)
  }

  const onMouseMove = (e: React.MouseEvent) => {
    if (arrastando) mover(e.clientX)
  }

  const onMouseUp = () => setArrastando(false)

  const onTeclado = (e: React.KeyboardEvent) => {
    const passo = e.shiftKey ? 10 : 2
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      setPosicao((p) => Math.max(0, p - passo))
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      setPosicao((p) => Math.min(100, p + passo))
    }
  }

  return (
    <div className="space-y-2">
      <div
        ref={caixaRef}
        className="relative aspect-video w-full select-none overflow-hidden rounded-lg border border-base-700 bg-base-900"
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        {/* Depois (base) */}
        {urlDepois ? (
          <img
            src={urlDepois}
            alt={`Depois: ${depois.rotulo}`}
            className="absolute inset-0 h-full w-full object-cover"
            draggable={false}
          />
        ) : (
          <div className="absolute inset-0 grid place-items-center text-slate-600">
            <ImageOff size={26} aria-hidden="true" />
          </div>
        )}

        {/* Antes (recorta pela esquerda) */}
        <div
          className="absolute inset-0 overflow-hidden"
          style={{ width: `${posicao}%` }}
          aria-hidden="true"
        >
          {urlAntes ? (
            <img
              src={urlAntes}
              alt=""
              className="h-full object-cover"
              style={{ width: '100%', maxWidth: 'none' }}
              draggable={false}
            />
          ) : (
            <div className="grid h-full w-full place-items-center bg-base-800 text-slate-600">
              <ImageOff size={26} />
            </div>
          )}
        </div>

        {/* divisor */}
        <div
          className="pointer-events-none absolute inset-y-0 z-10 w-0.5 bg-acento"
          style={{ left: `${posicao}%` }}
        />
        <button
          type="button"
          role="slider"
          aria-label="Divisor antes e depois"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(posicao)}
          onKeyDown={onTeclado}
          onMouseDown={(e) => {
            e.stopPropagation()
            setArrastando(true)
          }}
          className="absolute top-1/2 z-20 grid h-8 w-8 -translate-x-1/2 -translate-y-1/2 place-items-center
            rounded-full border border-acento bg-base-950 text-acento"
          style={{ left: `${posicao}%` }}
        >
          <Play size={13} className="rotate-90" aria-hidden="true" />
        </button>

        <span className="absolute left-2 top-2 z-10 chip bg-base-950/85 text-slate-200">
          Antes: {antes.rotulo}
        </span>
        <span className="absolute right-2 top-2 z-10 chip bg-base-950/85 text-slate-200">
          Depois: {depois.rotulo}
        </span>
      </div>
      <p className="text-xs text-slate-500">
        Arraste o divisor ou use as setas do teclado. Isso não altera a prévia salva.
      </p>
    </div>
  )
}

export function ComparacaoLadoALado({
  a,
  b,
}: {
  a: Previa | null
  b: Previa | null
}) {
  if (!a || !b) return null
  const lado = (p: Previa, titulo: string) => (
    <div className="space-y-2">
      <p className="rotulo">{titulo}</p>
      <div className="aspect-video overflow-hidden rounded-lg border border-base-700 bg-base-900">
        {urlMidia(p.miniatura) ? (
          <img
            src={urlMidia(p.miniatura) as string}
            alt={`Miniatura de ${p.estilo_rotulo}`}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="grid h-full w-full place-items-center text-slate-600">
            <ImageOff size={24} aria-hidden="true" />
          </div>
        )}
      </div>
      <dl className="space-y-1 text-xs text-slate-400">
        <div className="flex justify-between gap-2">
          <dt>Estilo</dt>
          <dd className="text-slate-200">{p.estilo_rotulo}</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Tempo</dt>
          <dd className="text-slate-200">{p.tempo_geracao_s?.toFixed(1) ?? '—'} s</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Resolução</dt>
          <dd className="text-slate-200">{p.resolucao ?? '—'}</dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Trecho</dt>
          <dd className="text-slate-200">
            {p.trecho ? `${p.trecho.inicio_s.toFixed(1)}–${p.trecho.fim_s.toFixed(1)} s` : '—'}
          </dd>
        </div>
        <div className="flex justify-between gap-2">
          <dt>Gerada</dt>
          <dd className="text-slate-200">{formatarData(p.gerado_em)}</dd>
        </div>
      </dl>
    </div>
  )

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {lado(a, 'Prévia A')}
      {lado(b, 'Prévia B')}
    </div>
  )
}
