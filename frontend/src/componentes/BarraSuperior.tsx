import { useEffect, useState } from 'react'
import {
  Cpu,
  Boxes,
  PlugZap,
  Plug,
  Radio,
  Menu,
  WifiOff,
  RefreshCw,
} from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { formatarNumero } from '../format'

function Ponto({ ok, atencao }: { ok: boolean; atencao?: boolean }) {
  const cor = ok ? 'bg-emerald-400' : atencao ? 'bg-amber-400' : 'bg-rose-500'
  return <span className={`inline-block h-2 w-2 rounded-full ${cor}`} aria-hidden="true" />
}

export default function BarraSuperior({ onMenu }: { onMenu: () => void }) {
  const { online, erroBackend, hardware, programas, estado, statusConexao } = useEstudio()
  const [hora, setHora] = useState(() => new Date())

  useEffect(() => {
    const t = window.setInterval(() => setHora(new Date()), 1000)
    return () => window.clearInterval(t)
  }, [])

  const gpu = hardware.gpus[0]
  const programasOk = programas.filter((p) => p.disponivel).length

  return (
    <header className="sticky top-0 z-20 border-b border-base-800 bg-base-900/95 backdrop-blur">
      <div className="flex h-14 items-center gap-3 px-3 lg:px-6">
        <button
          type="button"
          className="rounded-md p-2 text-slate-300 hover:bg-base-800 lg:hidden"
          onClick={onMenu}
          aria-label="Abrir menu"
        >
          <Menu size={18} />
        </button>

        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-x-4 gap-y-1 text-xs sm:text-[13px]">
          {/* Backend */}
          <span
            className="flex items-center gap-2 text-slate-300"
            title={online ? `Backend conectado (${estado?.backend ?? 'ok'})` : erroBackend ?? 'Offline'}
          >
            {online ? (
              <PlugZap size={15} className="text-emerald-400" aria-hidden="true" />
            ) : (
              <Plug size={15} className="text-rose-400" aria-hidden="true" />
            )}
            <Ponto ok={online} />
            <span className="font-medium">
              {online ? `Backend ${estado?.backend ?? 'ok'}` : 'Backend offline'}
            </span>
            {estado?.marco && <span className="chip">marco {estado.marco}</span>}
          </span>

          {/* Hardware */}
          <span
            className="flex items-center gap-2 text-slate-400"
            title={gpu ? `GPU: ${gpu.nome}` : 'Sem GPU detectada'}
          >
            <Cpu size={15} aria-hidden="true" />
            <Ponto ok={Boolean(gpu)} atencao={Boolean(gpu && gpu.temperaturaC && gpu.temperaturaC > 80)} />
            <span>
              {gpu
                ? `${gpu.nome} · ${gpu.temperaturaC !== null ? `${formatarNumero(gpu.temperaturaC, 0)} °C` : 'temp. n/d'}`
                : 'GPU n/d'}
            </span>
          </span>

          {/* Programas */}
          <span className="flex items-center gap-2 text-slate-400" title="Programas locais detectados">
            <Boxes size={15} aria-hidden="true" />
            <Ponto ok={programasOk > 0} />
            <span>
              {programas.length > 0
                ? `${formatarNumero(programasOk)}/${formatarNumero(programas.length)} programas`
                : 'Programas n/d'}
            </span>
          </span>

          {/* WebSocket */}
          <span
            className={[
              'flex items-center gap-2',
              statusConexao === 'conectado'
                ? 'text-slate-400'
                : statusConexao === 'offline'
                  ? 'text-rose-400'
                  : 'text-amber-400',
            ].join(' ')}
            title="Canal de eventos ao vivo"
          >
            {statusConexao === 'conectado' ? (
              <Radio size={15} aria-hidden="true" />
            ) : statusConexao === 'offline' ? (
              <WifiOff size={15} aria-hidden="true" />
            ) : (
              <RefreshCw size={15} className="animate-spin" aria-hidden="true" />
            )}
            <span>
              {statusConexao === 'conectado'
                ? 'Eventos ao vivo'
                : statusConexao === 'offline'
                  ? 'Sem eventos'
                  : 'Conectando eventos'}
            </span>
          </span>
        </div>

        <time
          className="hidden shrink-0 font-mono text-xs text-slate-400 sm:block"
          dateTime={hora.toISOString()}
        >
          {new Intl.DateTimeFormat('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
          }).format(hora)}
        </time>
      </div>

      {!online && (
        <div
          role="status"
          className="border-t border-rose-500/30 bg-rose-500/10 px-4 py-1.5 text-xs text-rose-200 lg:px-6"
        >
          <strong className="font-semibold">Backend offline.</strong>{' '}
          {erroBackend ??
            'Sem resposta da API local. Os dados abaixo podem estar desatualizados ou vazios.'}{' '}
          A base da API pode ser ajustada em Configurações.
        </div>
      )}
    </header>
  )
}
