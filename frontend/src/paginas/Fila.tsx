import { useEffect, useState } from 'react'
import { ListOrdered, RefreshCw, XCircle } from 'lucide-react'
import { api, ErroApi } from '../api'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { AvisoErro, EstadoVazio, EsqueletoCartao, TituloSecao } from '../componentes/ui'
import { formatarDataHoraCurta, formatarNumero } from '../format'
import type { Job } from '../types'

const CORES: Record<string, string> = {
  na_fila: 'text-slate-300 border-base-600',
  rodando: 'text-acento border-acento/50',
  pronto: 'text-emerald-300 border-emerald-500/40',
  erro: 'text-rose-300 border-rose-500/40',
  cancelado: 'text-slate-500 border-base-600',
}

function Barra({ job }: { job: Job }) {
  const pct = Math.min(100, Math.max(0, job.progresso ?? 0))
  return (
    <div
      className="h-1.5 w-full overflow-hidden rounded-full bg-base-700"
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(pct)}
      aria-label={`Progresso do job ${job.id}`}
    >
      <div
        className="h-full rounded-full bg-acento transition-[width] duration-300"
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}

export default function Fila() {
  const { fila, recarregarFila, online } = useEstudio()
  const [erro, setErro] = useState<string | null>(null)
  const [cancelando, setCancelando] = useState<string | null>(null)

  useEffect(() => {
    const t = window.setInterval(() => void recarregarFila(), 4000)
    return () => window.clearInterval(t)
  }, [recarregarFila])

  const cancelar = async (id: string) => {
    setCancelando(id)
    setErro(null)
    try {
      await api.cancelarJob(id)
      await recarregarFila()
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : 'Não foi possível cancelar o job.')
    } finally {
      setCancelando(null)
    }
  }

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <TituloSecao
        titulo="Fila"
        descricao="Tarefas do pipeline: análise, geração de prévias e renderizações. A fila é persistida em SQLite pelo backend."
        acao={
          <button type="button" className="botao-secundario" onClick={() => void recarregarFila()}>
            <RefreshCw size={16} aria-hidden="true" /> Atualizar
          </button>
        }
      />

      {erro && <AvisoErro mensagem={erro} />}
      {!online && (
        <AvisoErro mensagem="Backend offline: a fila exibida é a última carregada e pode estar desatualizada." />
      )}

      {fila.length === 0 ? (
        <EstadoVazio
          titulo="Fila vazia"
          descricao="Nenhuma tarefa na fila agora. Ao gerar uma prévia, o job aparece aqui com progresso e mensagens."
          icone={<ListOrdered size={22} aria-hidden="true" />}
        />
      ) : (
        <ul className="space-y-3">
          {fila.map((job) => (
            <li key={job.id} className="cartao p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 text-sm font-semibold text-slate-100">
                    <span className="truncate">{job.tipo}</span>
                    <span
                      className={[
                        'chip',
                        CORES[job.status] ?? 'border-base-600 text-slate-300',
                      ].join(' ')}
                    >
                      {job.status}
                    </span>
                  </p>
                  <p className="mt-1 font-mono text-[11px] text-slate-500">
                    {job.id}
                    {job.projeto ? ` · ${job.projeto}` : ''}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400">
                    {formatarNumero(job.progresso)}%
                  </span>
                  {(job.status === 'na_fila' || job.status === 'rodando') && (
                    <button
                      type="button"
                      className="botao-perigo"
                      disabled={cancelando === job.id}
                      onClick={() => void cancelar(job.id)}
                    >
                      <XCircle size={15} aria-hidden="true" /> Cancelar
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-3">
                <Barra job={job} />
              </div>

              {job.mensagem && (
                <p className="mt-2 break-words text-xs text-slate-400">{job.mensagem}</p>
              )}
              <p className="mt-1 text-[11px] text-slate-600">
                Criado em {formatarDataHoraCurta(job.criado_em)}
                {job.finished_em ? ` · concluído em ${formatarDataHoraCurta(job.finished_em)}` : ''}
              </p>
            </li>
          ))}
        </ul>
      )}

      {fila.length === 0 && !online && <EsqueletoCartao linhas={2} />}
    </div>
  )
}
