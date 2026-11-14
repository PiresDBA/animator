import { useEffect, useState } from 'react'
import {
  CircleCheck,
  CircleDashed,
  Circle,
  FolderKanban,
  Layers,
  Clock,
} from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { useProjetoDetalhe } from '../util/useProjetoDetalhe'
import SeletorProjeto from '../componentes/SeletorProjeto'
import Storyboard from '../componentes/Storyboard'
import {
  EsqueletoCartao,
  EsqueletoGrade,
  EstadoVazio,
  TituloSecao,
} from '../componentes/ui'
import { formatarData, formatarDuracao, formatarNumero } from '../format'
import type { ProjetoMeta } from '../types'

const ETAPAS = [
  { id: 'criado', rotulo: 'Projeto criado', descricao: 'Vídeo de entrada registrado com hash.' },
  { id: 'analisado', rotulo: 'Análise', descricao: 'Cenas, fala, poses e movimento detectados.' },
  { id: 'roteado', rotulo: 'Técnicas', descricao: 'Roteador escolhe a técnica de cada cena.' },
  { id: 'previa', rotulo: 'Prévia', descricao: 'Prévia de 5 s gerada na CPU.' },
  { id: 'aprovado', rotulo: 'Avaliado', descricao: 'Decisão humana registrada com notas.' },
]

function etapasDoProjeto(p: ProjetoMeta, temPrevia: boolean, temAvaliacao: boolean) {
  const status = p.status ?? ''
  const criado = true
  const analisado = !['criado', 'novo'].includes(status.toLowerCase())
  const roteado = temPrevia
  const previa = temPrevia
  const avaliado = temAvaliacao || p.aprovado
  return { criado, analisado, roteado, previa, avaliado }
}

export default function Projetos() {
  const { projetos, carregandoProjetos, online, projetoAtual, definirProjetoAtual } =
    useEstudio()
  const { detalhe, carregando: carregandoDetalhe } = useProjetoDetalhe(projetoAtual)
  const [avaliacoesPorProjeto, setAvaliacoesPorProjeto] = useState<
    Record<string, number>
  >({})

  useEffect(() => {
    if (!projetoAtual || !detalhe) return
    setAvaliacoesPorProjeto((atuais) => ({
      ...atuais,
      [projetoAtual]: (detalhe.avaliacoes ?? []).length,
    }))
  }, [projetoAtual, detalhe])

  const selecionado = projetos.find((p) => p.id === projetoAtual) ?? null
  const etapas = selecionado
    ? etapasDoProjeto(
        selecionado,
        Boolean(detalhe?.previa),
        (avaliacoesPorProjeto[selecionado.id] ?? 0) > 0,
      )
    : null

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <TituloSecao
        titulo="Projetos"
        descricao="Acompanhe a linha do tempo do pipeline de cada projeto e veja o storyboard com a técnica escolhida por cena."
      />

      <SeletorProjeto projetoId={projetoAtual} aoMudar={definirProjetoAtual} />

      <section>
        <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
          <FolderKanban size={14} aria-hidden="true" /> Todos os projetos
        </h2>
        {carregandoProjetos ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <EsqueletoCartao />
            <EsqueletoCartao />
            <EsqueletoCartao />
          </div>
        ) : !online ? (
          <EstadoVazio
            titulo="Backend offline"
            descricao="Sem conexão com a API local, a lista de projetos não pode ser lida agora."
            icone={<CircleDashed size={22} aria-hidden="true" />}
          />
        ) : projetos.length === 0 ? (
          <EstadoVazio
            titulo="Nenhum projeto criado"
            descricao="Crie o primeiro projeto em Novo vídeo para ver a linha do tempo do pipeline."
          />
        ) : (
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {projetos.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  onClick={() => definirProjetoAtual(p.id)}
                  className={[
                    'cartao w-full p-4 text-left transition-colors hover:border-acento/60',
                    p.id === projetoAtual ? 'border-acento ring-1 ring-acento/50' : '',
                  ].join(' ')}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="truncate text-sm font-semibold text-slate-100">
                      {p.nome}
                    </span>
                    <span
                      className={[
                        'chip',
                        p.aprovado
                          ? 'border-emerald-500/40 text-emerald-300'
                          : 'border-base-600 text-slate-400',
                      ].join(' ')}
                    >
                      {p.aprovado ? 'Aprovado' : p.status}
                    </span>
                  </div>
                  <p className="mt-1 font-mono text-[11px] text-slate-500">{p.id}</p>
                  <p className="mt-2 text-xs text-slate-500">
                    Criado em {formatarData(p.criado_em)}
                  </p>
                  <p className="text-xs text-slate-500">
                    Entrada: {formatarDuracao(p.entrada?.duracao_s ?? 0)}
                  </p>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {selecionado && etapas && (
        <section className="cartao p-5">
          <h2 className="cartao-titulo mb-4">Linha do tempo do pipeline</h2>
          <ol className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {ETAPAS.map((etapa, i) => {
              const feita =
                i === 0
                  ? etapas.criado
                  : i === 1
                    ? etapas.analisado
                    : i === 2
                      ? etapas.roteado
                      : i === 3
                        ? etapas.previa
                        : etapas.avaliado
              return (
                <li key={etapa.id} className="relative">
                  <div className="flex items-center gap-2">
                    {feita ? (
                      <CircleCheck
                        size={18}
                        className="text-emerald-400"
                        aria-hidden="true"
                      />
                    ) : (
                      <Circle size={18} className="text-base-600" aria-hidden="true" />
                    )}
                    <span
                      className={[
                        'text-sm font-medium',
                        feita ? 'text-slate-100' : 'text-slate-500',
                      ].join(' ')}
                    >
                      {etapa.rotulo}
                    </span>
                  </div>
                  <p className="mt-1 pl-6 text-xs text-slate-500">{etapa.descricao}</p>
                </li>
              )
            })}
          </ol>

          <dl className="mt-5 grid grid-cols-2 gap-3 border-t border-base-800 pt-4 text-xs sm:grid-cols-4">
            <div>
              <dt className="rotulo">Tentativas</dt>
              <dd className="mt-1 text-slate-200">
                {formatarNumero(
                  Object.values(selecionado.tentativas ?? {}).reduce((a, b) => a + b, 0),
                )}
                /{formatarNumero(
                  (selecionado.estilos?.length ?? 1) * (selecionado.limite_tentativas ?? 3),
                )}
              </dd>
            </div>
            <div>
              <dt className="rotulo">Estilos</dt>
              <dd className="mt-1 text-slate-200">
                {selecionado.estilos?.filter((e) => e.disponivel).length ?? 0} disponíveis
              </dd>
            </div>
            <div>
              <dt className="rotulo">Avaliações</dt>
              <dd className="mt-1 text-slate-200">
                {formatarNumero(avaliacoesPorProjeto[selecionado.id] ?? 0)}
              </dd>
            </div>
            <div>
              <dt className="rotulo">Atualizado</dt>
              <dd className="mt-1 text-slate-200">{formatarData(selecionado.atualizado_em)}</dd>
            </div>
          </dl>
        </section>
      )}

      {selecionado && (
        <section className="cartao p-5">
          <h2 className="cartao-titulo mb-3 flex items-center gap-2">
            <Layers size={15} className="text-acento" aria-hidden="true" />
            Storyboard do projeto
          </h2>
          {carregandoDetalhe ? (
            <EsqueletoGrade quantidade={3} />
          ) : (
            <Storyboard cenas={detalhe?.cenas ?? []} mapa={detalhe?.mapa_tecnicas ?? null} />
          )}
          {detalhe?.previa && (
            <p className="mt-3 flex items-center gap-2 text-xs text-slate-500">
              <Clock size={13} aria-hidden="true" />
              Última prévia gerada em {formatarData(detalhe.previa.gerado_em)} em{' '}
              {formatarDuracao(detalhe.previa.tempo_geracao_s)}.
            </p>
          )}
        </section>
      )}
    </div>
  )
}
