import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  FileVideo,
  Loader2,
  Palette,
  PlayCircle,
  Sparkles,
} from 'lucide-react'
import { api, ErroApi } from '../api'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { AvisoErro, EsqueletoCartao, TituloSecao } from '../componentes/ui'
import CartaoEstilo from '../componentes/CartaoEstilo'
import LinhaDoTempo from '../componentes/LinhaDoTempo'
import PainelDecisao from '../componentes/PainelDecisao'
import { formatarDuracao } from '../format'
import type { Previa, ProjetoMeta } from '../types'

const PASSOS = [
  { n: 1, rotulo: 'Entrada', icone: FileVideo },
  { n: 2, rotulo: 'Estilos', icone: Palette },
  { n: 3, rotulo: 'Prévia', icone: PlayCircle },
  { n: 4, rotulo: 'Revisão', icone: Sparkles },
]

const PREVIA_S = 5
const LIMITE_TENTATIVAS = 3

export default function NovoVideo() {
  const navegar = useNavigate()
  const { online, recarregarProjetos } = useEstudio()

  const [passo, setPasso] = useState(1)
  const [nome, setNome] = useState('')
  const [video, setVideo] = useState('')
  const [criando, setCriando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [projeto, setProjeto] = useState<ProjetoMeta | null>(null)

  const [estilo, setEstilo] = useState<string | null>(null)
  const [inicio, setInicio] = useState(0)
  const [seed, setSeed] = useState(7)
  const [resolucao, setResolucao] = useState('480p')

  const [gerando, setGerando] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [previa, setPrevia] = useState<Previa | null>(null)
  const [avaliacaoSalva, setAvaliacaoSalva] = useState(false)

  /* Ao criar o projeto, mantemos o seletor global sincronizado. */
  useEffect(() => {
    if (projeto) void recarregarProjetos()
  }, [projeto, recarregarProjetos])

  const estilos = useMemo(() => {
    if (projeto?.estilos?.length) return projeto.estilos
    return [
      { id: 'bonecos', rotulo: 'Bonecos de palito', disponivel: true, motivo: null },
      {
        id: 'lego',
        rotulo: 'Mosaico de blocos',
        disponivel: false,
        motivo: 'Disponível a partir do M4',
      },
      {
        id: 'anime',
        rotulo: 'Traço anime',
        disponivel: false,
        motivo: 'Disponível a partir do M4',
      },
      {
        id: 'cartoon',
        rotulo: 'Cartoon 3D estilizado',
        disponivel: false,
        motivo: 'Disponível a partir do M4',
      },
      {
        id: '3d',
        rotulo: '3D com materiais realistas',
        disponivel: false,
        motivo: 'Disponível a partir do M4',
      },
    ]
  }, [projeto])

  const duracaoEntrada = projeto?.entrada?.duracao_s ?? 60
  const tentativasUsadas = estilo ? (projeto?.tentativas?.[estilo] ?? 0) : 0

  /* ---------------------------------------------------------------- */

  const criarProjeto = async () => {
    setErro(null)
    setCriando(true)
    try {
      const meta = await api.criarProjeto(nome.trim(), video.trim())
      setProjeto(meta)
      try {
        await api.analisar(meta.id)
      } catch {
        /* a analise pode falhar; o projeto continua criado */
      }
      setPasso(2)
    } catch (e) {
      setErro(
        e instanceof ErroApi ? e.message : 'Não foi possível criar o projeto.',
      )
    } finally {
      setCriando(false)
    }
  }

  const gerarPrevia = async () => {
    if (!projeto || !estilo) return
    setErro(null)
    setGerando(true)
    try {
      const r = await api.previa(projeto.id, {
        estilo,
        trecho_inicio: inicio,
        trecho_fim: Math.min(inicio + PREVIA_S, duracaoEntrada),
        seed,
        resolucao,
      })
      setJobId(r.job_id)
      setPrevia(null)
    } catch (e) {
      setErro(e instanceof ErroApi ? e.message : 'Não foi possível gerar a prévia.')
    } finally {
      setGerando(false)
    }
  }

  const buscarPrevia = async () => {
    if (!projeto) return
    try {
      const lista = await api.previas(projeto.id)
      const pronta = lista.filter((p) => p.status === 'pronto')
      if (pronta.length) setPrevia(pronta[pronta.length - 1])
    } catch {
      /* o painel de log mostra o detalhe */
    }
  }

  useEffect(() => {
    if (!jobId) return
    const t = window.setInterval(() => void buscarPrevia(), 2000)
    return () => window.clearInterval(t)
  }, [jobId, projeto])

  /* ---------------------------------------------------------------- */

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <TituloSecao
        titulo="Novo vídeo"
        descricao="Quatro passos: informe o vídeo, escolha o estilo, gere a prévia de 5 segundos e revise antes de aprovar."
      />

      {/* Trilha de passos */}
      <ol className="flex flex-wrap items-center gap-2" aria-label="Etapas do novo vídeo">
        {PASSOS.map((p) => {
          const ativo = p.n === passo
          const feito = p.n < passo
          return (
            <li key={p.n} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => p.n < passo && setPasso(p.n)}
                disabled={p.n > passo}
                aria-current={ativo ? 'step' : undefined}
                className={[
                  'flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors',
                  ativo
                    ? 'border-acento bg-acento/15 text-acento'
                    : feito
                      ? 'border-base-600 bg-base-800 text-slate-300 hover:border-acento/50'
                      : 'border-base-700 text-slate-500',
                ].join(' ')}
              >
                {feito ? (
                  <Check size={14} aria-hidden="true" />
                ) : (
                  <p.icone size={14} aria-hidden="true" />
                )}
                {p.n}. {p.rotulo}
              </button>
              {p.n < PASSOS.length && <ArrowRight size={14} className="text-base-600" aria-hidden="true" />}
            </li>
          )
        })}
      </ol>

      {erro && <AvisoErro mensagem={erro} />}

      {/* PASSO 1 — entrada */}
      {passo === 1 && (
        <section className="cartao space-y-4 p-5">
          <div>
            <h2 className="cartao-titulo">1. Vídeo de entrada</h2>
            <p className="mt-1 text-sm text-slate-400">
              Informe o caminho de um arquivo de vídeo já presente no computador. O arquivo não
              sai da sua máquina.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="rotulo-campo" htmlFor="nome-projeto">
                Nome do projeto
              </label>
              <input
                id="nome-projeto"
                className="campo"
                placeholder="Ex.: a história do robô"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
              />
            </div>
            <div>
              <label className="rotulo-campo" htmlFor="caminho-video">
                Caminho do vídeo
              </label>
              <input
                id="caminho-video"
                className="campo font-mono text-xs"
                placeholder="C:\Videos\meu-video.mp4"
                value={video}
                onChange={(e) => setVideo(e.target.value)}
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="botao-primario"
              disabled={!online || criando || !nome.trim() || !video.trim()}
              onClick={() => void criarProjeto()}
            >
              {criando ? (
                <>
                  <Loader2 size={16} className="animate-spin" aria-hidden="true" /> Criando…
                </>
              ) : (
                <>
                  <ArrowRight size={16} aria-hidden="true" /> Criar e analisar
                </>
              )}
            </button>
            {!online && (
              <span className="text-xs text-rose-300">
                Backend offline: não é possível criar o projeto agora.
              </span>
            )}
          </div>
        </section>
      )}

      {/* PASSO 2 — estilos */}
      {passo === 2 && (
        <section className="space-y-4">
          <div>
            <h2 className="cartao-titulo">2. Estilo da animação</h2>
            <p className="mt-1 text-sm text-slate-400">
              No marco atual, apenas o estilo de bonecos de palito está habilitado. Cada estilo
              permite {LIMITE_TENTATIVAS} tentativas.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {estilos.map((e) => (
              <CartaoEstilo
                key={e.id}
                estilo={e}
                selecionado={estilo === e.id}
                tentativas={projeto?.tentativas?.[e.id] ?? 0}
                limiteTentativas={projeto?.limite_tentativas ?? LIMITE_TENTATIVAS}
                onSelecionar={setEstilo}
              />
            ))}
          </div>

          <div className="cartao flex flex-wrap items-center justify-between gap-3 p-4">
            <p className="text-sm text-slate-400">
              {estilo
                ? `Estilo escolhido: ${estilos.find((e) => e.id === estilo)?.rotulo}. Tentativas usadas: ${tentativasUsadas}/${projeto?.limite_tentativas ?? LIMITE_TENTATIVAS}.`
                : 'Escolha um estilo disponível para continuar.'}
            </p>
            <button
              type="button"
              className="botao-primario"
              disabled={!estilo || tentativasUsadas >= (projeto?.limite_tentativas ?? LIMITE_TENTATIVAS)}
              onClick={() => setPasso(3)}
            >
              Continuar <ArrowRight size={16} aria-hidden="true" />
            </button>
          </div>
        </section>
      )}

      {/* PASSO 3 — prévia */}
      {passo === 3 && (
        <section className="space-y-4">
          <div>
            <h2 className="cartao-titulo">3. Prévia de {PREVIA_S} segundos</h2>
            <p className="mt-1 text-sm text-slate-400">
              Escolha o trecho do vídeo, a semente aleatória e a resolução. A prévia é gerada
              localmente, na CPU.
            </p>
          </div>

          <div className="cartao space-y-4 p-4">
            <LinhaDoTempo
              duracaoTotal={duracaoEntrada}
              inicio={inicio}
              duracaoPrevia={PREVIA_S}
              onChange={setInicio}
            />
            <p className="text-xs text-slate-500">
              Duração da entrada: {formatarDuracao(duracaoEntrada)}.
            </p>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="rotulo-campo" htmlFor="seed">
                  Semente (seed)
                </label>
                <input
                  id="seed"
                  type="number"
                  min={0}
                  className="campo"
                  value={seed}
                  onChange={(e) => setSeed(Number(e.target.value))}
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  A mesma semente com o mesmo trecho gera a mesma prévia.
                </p>
              </div>
              <div>
                <label className="rotulo-campo" htmlFor="resolucao">
                  Resolução
                </label>
                <select
                  id="resolucao"
                  className="campo"
                  value={resolucao}
                  onChange={(e) => setResolucao(e.target.value)}
                >
                  <option value="480p">480p (rápido, CPU)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="botao-primario"
              disabled={!online || !projeto || !estilo || gerando}
              onClick={() => void gerarPrevia()}
            >
              {gerando ? (
                <>
                  <Loader2 size={16} className="animate-spin" aria-hidden="true" /> Enfileirando…
                </>
              ) : (
                <>
                  <PlayCircle size={16} aria-hidden="true" /> Gerar prévia
                </>
              )}
            </button>
            {jobId && (
              <span className="chip font-mono" title="Identificador do job na fila">
                job {jobId}
              </span>
            )}
            <button
              type="button"
              className="botao-fantasma"
              onClick={() => setPasso(2)}
            >
              <ArrowLeft size={16} aria-hidden="true" /> Voltar aos estilos
            </button>
          </div>
        </section>
      )}

      {/* PASSO 4 — revisão */}
      {passo === 4 && (
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="space-y-3">
            <h2 className="cartao-titulo">4. Revisão e avaliação</h2>
            {previa ? (
              <div className="cartao p-4">
                <p className="text-sm text-slate-300">
                  Prévia <span className="font-mono">{previa.previa_id}</span> pronta (
                  {previa.estilo_rotulo}).
                </p>
                <p className="mt-1 text-xs text-slate-500">
                  Verificação de segurança: {previa.seguranca?.veredito ?? 'n/d'} · tempo de
                  geração {formatarDuracao(previa.tempo_geracao_s)}
                </p>
              </div>
            ) : (
              <EsqueletoCartao linhas={2} />
            )}
            <button
              type="button"
              className="botao-secundario"
              onClick={() => setPasso(3)}
            >
              <ArrowLeft size={16} aria-hidden="true" /> Voltar à prévia
            </button>
          </div>

          <PainelDecisao
            previa={previa}
            projetoId={projeto?.id ?? ''}
            aoSalvar={() => setAvaliacaoSalva(true)}
          />

          {avaliacaoSalva && (
            <div className="cartao p-4 lg:col-span-2">
              <p className="text-sm text-slate-300">
                Avaliação registrada. Você pode acompanhar os detalhes em{' '}
                <button
                  type="button"
                  className="text-acento underline"
                  onClick={() => navegar('/previas')}
                >
                  Prévias
                </button>
                .
              </p>
            </div>
          )}
        </section>
      )}
    </div>
  )
}
