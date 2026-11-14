/**
 * Provedor global do estudio: estado do backend, projetos, fila e o log ao vivo
 * alimentado pelo WebSocket /api/eventos (com reconexao e backoff).
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { api, ErroApi, urlEventos, type EventoRecebido } from '../api'
import type { EventoLog, Job, ProjetoMeta, Estado } from '../types'
import {
  normalizarFila,
  normalizarHardware,
  normalizarProgramas,
  normalizarProjetos,
  type AmostraHardware,
  type InfoHardware,
  type InfoPrograma,
} from '../util/normalizadores'

export type StatusConexao = 'conectado' | 'conectando' | 'desconectado' | 'offline'

interface ValorContexto {
  online: boolean
  erroBackend: string | null
  estado: Estado | null
  hardware: InfoHardware
  programas: InfoPrograma[]
  projetos: ProjetoMeta[]
  fila: Job[]
  carregandoProjetos: boolean
  recarregarProjetos: () => Promise<void>
  recarregarFila: () => Promise<void>
  statusConexao: StatusConexao
  eventos: EventoLog[]
  limparEventos: () => void
  amostras: AmostraHardware[]
  projetoAtual: string | null
  definirProjetoAtual: (id: string | null) => void
}

const Contexto = createContext<ValorContexto | null>(null)

const CHAVE_PROJETO = 'estudio.projetoAtual'
const LIMITE_EVENTOS = 400

export function ProvedorEstudio({ children }: { children: ReactNode }) {
  const [online, setOnline] = useState(false)
  const [erroBackend, setErroBackend] = useState<string | null>(null)
  const [estado, setEstado] = useState<Estado | null>(null)
  const [hardware, setHardware] = useState<InfoHardware>(() => normalizarHardware(null))
  const [programas, setProgramas] = useState<InfoPrograma[]>([])
  const [projetos, setProjetos] = useState<ProjetoMeta[]>([])
  const [fila, setFila] = useState<Job[]>([])
  const [carregandoProjetos, setCarregandoProjetos] = useState(true)
  const [statusConexao, setStatusConexao] = useState<StatusConexao>('conectando')
  const [eventos, setEventos] = useState<EventoLog[]>([])
  const [amostras, setAmostras] = useState<AmostraHardware[]>([])
  const [projetoAtual, definirProjetoAtual] = useState<string | null>(() =>
    localStorage.getItem(CHAVE_PROJETO),
  )

  const contadorEventos = useRef(0)

  const definirProjeto = useCallback((id: string | null) => {
    definirProjetoAtual(id)
    if (id) localStorage.setItem(CHAVE_PROJETO, id)
    else localStorage.removeItem(CHAVE_PROJETO)
  }, [])

  const recarregarProjetos = useCallback(async () => {
    setCarregandoProjetos(true)
    try {
      const lista = await api.projetos()
      setProjetos(normalizarProjetos(lista))
    } catch (e) {
      if (e instanceof ErroApi && e.offline) setOnline(false)
    } finally {
      setCarregandoProjetos(false)
    }
  }, [])

  const recarregarFila = useCallback(async () => {
    try {
      const lista = await api.fila()
      setFila(normalizarFila(lista))
    } catch {
      /* silencioso: a pagina Fila mostra o estado offline */
    }
  }, [])

  /* ---------------------------------------------------------------- */
  /* Sonda do backend                                                  */
  /* ---------------------------------------------------------------- */

  const sondar = useCallback(async () => {
    try {
      const e = await api.estado()
      setEstado(e)
      setOnline(true)
      setErroBackend(null)
      const hw = normalizarHardware(e.hardware)
      setHardware(hw)
      setProgramas(normalizarProgramas(e.programas))
      const f = normalizarFila(e.fila)
      if (f.length) setFila(f)
      const gpu = hw.gpus[0]
      if (gpu) {
        setAmostras((atuais) => {
          const nova: AmostraHardware = {
            tempo: Date.now(),
            temperaturaC: gpu.temperaturaC,
            vramUsadaMib: gpu.vramUsadaMib,
            utilizacaoPct: gpu.utilizacaoPct,
          }
          const proximas = [...atuais, nova]
          return proximas.length > 60 ? proximas.slice(proximas.length - 60) : proximas
        })
      }
    } catch (e) {
      if (e instanceof ErroApi) {
        setOnline(false)
        setErroBackend(e.message)
      } else {
        setOnline(false)
        setErroBackend('Falha inesperada ao consultar o backend.')
      }
    }
  }, [])

  useEffect(() => {
    void sondar()
    void recarregarProjetos()
    void recarregarFila()
    const t = window.setInterval(() => {
      void sondar()
    }, 5000)
    return () => window.clearInterval(t)
  }, [sondar, recarregarProjetos, recarregarFila])

  /* ---------------------------------------------------------------- */
  /* WebSocket de eventos com reconexao e backoff                       */
  /* ---------------------------------------------------------------- */

  useEffect(() => {
    let socket: WebSocket | null = null
    let tentativa = 0
    let timer: number | undefined
    let cancelado = false

    const conectar = () => {
      if (cancelado) return
      setStatusConexao('conectando')
      try {
        socket = new WebSocket(urlEventos())
      } catch {
        agendar()
        return
      }

      socket.onopen = () => {
        tentativa = 0
        setStatusConexao('conectado')
      }

      socket.onmessage = (evento) => {
        let dados: EventoRecebido
        try {
          dados = JSON.parse(String(evento.data)) as EventoRecebido
        } catch {
          return
        }
        const nivel =
          (dados.nivel as EventoLog['nivel']) ??
          (dados.level as EventoLog['nivel']) ??
          (dados.tipo === 'log' ? 'info' : 'info')
        const mensagem =
          dados.mensagem ??
          dados.texto ??
          dados.message ??
          (dados.tipo === 'job' ? `Job ${String(dados.job_id ?? '')}` : '')
        contadorEventos.current += 1
        const entrada: EventoLog = {
          id: `ev_${contadorEventos.current}`,
          tipo: dados.tipo ?? 'log',
          nivel,
          mensagem: String(mensagem),
          timestamp: new Date().toISOString(),
          projeto: dados.projeto,
        }
        setEventos((atuais) => {
          const proximos = [entrada, ...atuais]
          return proximos.length > LIMITE_EVENTOS ? proximos.slice(0, LIMITE_EVENTOS) : proximos
        })
        if (dados.tipo === 'job') void recarregarFila()
        if (dados.tipo === 'previa') void recarregarProjetos()
      }

      socket.onerror = () => {
        /* o onclose cuida da reconexao */
      }

      socket.onclose = () => {
        if (cancelado) return
        setStatusConexao('desconectado')
        agendar()
      }
    }

    const agendar = () => {
      if (cancelado) return
      tentativa += 1
      const atraso = Math.min(1000 * 2 ** Math.min(tentativa - 1, 4), 16000)
      timer = window.setTimeout(conectar, atraso)
    }

    conectar()

    return () => {
      cancelado = true
      if (timer) window.clearTimeout(timer)
      if (socket) {
        socket.onclose = null
        socket.close()
      }
    }
  }, [recarregarFila, recarregarProjetos])

  const limparEventos = useCallback(() => setEventos([]), [])

  const valor = useMemo<ValorContexto>(
    () => ({
      online,
      erroBackend,
      estado,
      hardware,
      programas,
      projetos,
      fila,
      carregandoProjetos,
      recarregarProjetos,
      recarregarFila,
      statusConexao,
      eventos,
      limparEventos,
      amostras,
      projetoAtual,
      definirProjetoAtual: definirProjeto,
    }),
    [
      online,
      erroBackend,
      estado,
      hardware,
      programas,
      projetos,
      fila,
      carregandoProjetos,
      recarregarProjetos,
      recarregarFila,
      statusConexao,
      eventos,
      limparEventos,
      amostras,
      projetoAtual,
      definirProjeto,
    ],
  )

  return <Contexto.Provider value={valor}>{children}</Contexto.Provider>
}

export function useEstudio(): ValorContexto {
  const ctx = useContext(Contexto)
  if (!ctx) throw new Error('useEstudio deve ser usado dentro de ProvedorEstudio')
  return ctx
}
