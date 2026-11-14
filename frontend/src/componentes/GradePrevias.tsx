import { urlMidia } from '../api'
import { formatarDuracao, formatarData } from '../format'
import type { Previa } from '../types'
import { ShieldCheck, ShieldAlert, ShieldX, ImageOff } from 'lucide-react'

function SeloSeguranca({ previa }: { previa: Previa }) {
  const s = previa.seguranca
  if (!s) return <span className="chip">Segurança n/d</span>
  const veredito = s.veredito
  if (veredito === 'verde') {
    return (
      <span className="chip border-emerald-500/40 bg-emerald-500/10 text-emerald-300">
        <ShieldCheck size={12} aria-hidden="true" /> Seguro
      </span>
    )
  }
  if (veredito === 'amarelo') {
    return (
      <span className="chip border-amber-500/40 bg-amber-500/10 text-amber-300">
        <ShieldAlert size={12} aria-hidden="true" /> Atenção
      </span>
    )
  }
  return (
    <span className="chip border-rose-500/40 bg-rose-500/10 text-rose-300">
      <ShieldX size={12} aria-hidden="true" /> Reprovado
    </span>
  )
}

export default function GradePrevias({
  previas,
  selecionadas,
  aoSelecionar,
}: {
  previas: Previa[]
  selecionadas: string[]
  aoSelecionar: (id: string) => void
}) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {previas.map((p) => {
        const miniatura = urlMidia(p.miniatura)
        const selecionada = selecionadas.includes(p.previa_id)
        return (
          <article
            key={p.previa_id}
            className={[
              'cartao overflow-hidden transition-colors',
              selecionada ? 'border-acento ring-1 ring-acento/50' : '',
            ].join(' ')}
          >
            <div className="relative aspect-video w-full overflow-hidden bg-base-900">
              {miniatura ? (
                <img
                  src={miniatura}
                  alt={`Miniatura da prévia ${p.estilo_rotulo}`}
                  className="h-full w-full object-cover"
                  loading="lazy"
                  onError={(e) => {
                    ;(e.currentTarget as HTMLImageElement).style.display = 'none'
                  }}
                />
              ) : (
                <div className="grid h-full w-full place-items-center text-slate-600">
                  <ImageOff size={26} aria-hidden="true" />
                </div>
              )}
              <div className="absolute left-2 top-2 flex gap-1.5">
                <span className="chip bg-base-950/85 text-slate-200">{p.estilo_rotulo}</span>
                <SeloSeguranca previa={p} />
              </div>
              <div className="absolute bottom-2 right-2">
                <span className="chip bg-base-950/85 font-mono text-slate-200">
                  {formatarDuracao(p.trecho?.duracao_s ?? 5)}
                </span>
              </div>
            </div>

            <div className="space-y-2 p-3">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-100">{p.previa_id}</p>
                  <p className="font-mono text-[11px] text-slate-500">{p.resolucao ?? '—'} · {p.fps ?? '—'} fps</p>
                </div>
                <span
                  className={[
                    'chip',
                    p.status === 'pronto'
                      ? 'border-emerald-500/40 text-emerald-300'
                      : p.status === 'erro'
                        ? 'border-rose-500/40 text-rose-300'
                        : 'border-amber-500/40 text-amber-300',
                  ].join(' ')}
                >
                  {p.status}
                </span>
              </div>

              {p.erro && <p className="text-xs text-rose-300">{p.erro}</p>}

              <div className="flex items-center justify-between gap-2 text-[11px] text-slate-500">
                <span>Gerada em {formatarData(p.gerado_em)}</span>
                <span className="font-mono">seed {p.params?.seed ?? '—'}</span>
              </div>

              <button
                type="button"
                className={selecionada ? 'botao-primario w-full' : 'botao-secundario w-full'}
                onClick={() => aoSelecionar(p.previa_id)}
                aria-pressed={selecionada}
              >
                {selecionada ? 'Selecionada para comparar' : 'Selecionar'}
              </button>
            </div>
          </article>
        )
      })}
    </div>
  )
}
