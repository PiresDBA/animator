import { Link } from 'react-router-dom'
import {
  Wand2,
  Images,
  FolderKanban,
  Cpu,
  ArrowRight,
  ShieldCheck,
  Film,
  Boxes,
  Clock,
} from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { EsqueletoCartao, EstadoVazio, TituloSecao } from '../componentes/ui'
import { formatarData, formatarNumero } from '../format'

const ATALHOS = [
  {
    para: '/novo-video',
    titulo: 'Novo vídeo',
    descricao: 'Quatro passos: entrada, estilos, prévia e revisão.',
    icone: Wand2,
  },
  {
    para: '/previas',
    titulo: 'Prévias e avaliação',
    descricao: 'Compare, dê notas de 1 a 5 e decida.',
    icone: Images,
  },
  {
    para: '/projetos',
    titulo: 'Projetos',
    descricao: 'Linha do tempo do pipeline e storyboard.',
    icone: FolderKanban,
  },
  {
    para: '/hardware',
    titulo: 'Hardware',
    descricao: 'Benchmark e monitor ao vivo de CPU e GPU.',
    icone: Cpu,
  },
]

export default function Inicio() {
  const { online, estado, hardware, projetos, fila, carregandoProjetos } = useEstudio()
  const gpu = hardware.gpus[0]
  const ativos = fila.filter((j) => j.status === 'rodando' || j.status === 'na_fila').length

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <TituloSecao
        titulo="Estúdio de Animação"
        descricao="Transforme um vídeo em uma animação para crianças de 7 a 10 anos, direto no seu computador. Nada é enviado para a nuvem."
        acao={
          <Link to="/novo-video" className="botao-primario">
            <Wand2 size={16} aria-hidden="true" /> Começar um vídeo
          </Link>
        }
      />

      {!online && (
        <div
          role="status"
          className="rounded-xl border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-100"
        >
          <strong className="font-semibold">O backend está offline.</strong> A interface abriu
          normalmente, mas sem dados do servidor. Suba o backend local (porta 8765) e a tela se
          atualiza sozinha.
        </div>
      )}

      {/* Resumo */}
      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div className="cartao p-4">
          <p className="rotulo">Projetos</p>
          <p className="mt-1 text-2xl font-semibold text-slate-100">
            {carregandoProjetos ? '—' : formatarNumero(projetos.length)}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {projetos.filter((p) => p.aprovado).length} com estilo aprovado
          </p>
        </div>
        <div className="cartao p-4">
          <p className="rotulo">Fila</p>
          <p className="mt-1 text-2xl font-semibold text-slate-100">{formatarNumero(ativos)}</p>
          <p className="mt-1 text-xs text-slate-500">tarefas ativas agora</p>
        </div>
        <div className="cartao p-4">
          <p className="rotulo">GPU</p>
          <p className="mt-1 truncate text-base font-semibold text-slate-100">
            {gpu ? gpu.nome : 'Não detectada'}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            {gpu?.temperaturaC !== null && gpu?.temperaturaC !== undefined
              ? `${formatarNumero(gpu.temperaturaC, 0)} °C`
              : 'temperatura n/d'}
          </p>
        </div>
        <div className="cartao p-4">
          <p className="rotulo">Marco</p>
          <p className="mt-1 text-2xl font-semibold text-slate-100">
            {estado?.marco ?? 'M2'}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Primeiro estilo fim a fim: bonecos de palito
          </p>
        </div>
      </section>

      {/* Atalhos */}
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
          Atalhos
        </h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {ATALHOS.map(({ para, titulo, descricao, icone: Icone }) => (
            <Link
              key={para}
              to={para}
              className="cartao group flex flex-col gap-2 p-4 transition-colors hover:border-acento/60"
            >
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-acento/15 text-acento">
                <Icone size={18} aria-hidden="true" />
              </span>
              <span className="flex items-center gap-1 text-sm font-semibold text-slate-100">
                {titulo}
                <ArrowRight
                  size={14}
                  className="opacity-0 transition-opacity group-hover:opacity-100"
                  aria-hidden="true"
                />
              </span>
              <span className="text-xs text-slate-400">{descricao}</span>
            </Link>
          ))}
        </div>
      </section>

      {/* Regras do marco */}
      <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="cartao p-4">
          <h2 className="cartao-titulo mb-2 flex items-center gap-2">
            <ShieldCheck size={15} className="text-emerald-400" aria-hidden="true" />
            O que dá para fazer agora
          </h2>
          <ul className="space-y-1.5 text-sm text-slate-400">
            <li>• Analisar um vídeo local e quebrar em cenas.</li>
            <li>• Gerar prévias de 5 segundos no estilo bonecos de palito.</li>
            <li>• Avaliar com notas de 1 a 5 e aprovar ou reprovar.</li>
            <li>• Acompanhar o log do pipeline ao vivo.</li>
          </ul>
        </div>
        <div className="cartao p-4">
          <h2 className="cartao-titulo mb-2 flex items-center gap-2">
            <Film size={15} className="text-amber-400" aria-hidden="true" />
            O que ainda não está liberado
          </h2>
          <ul className="space-y-1.5 text-sm text-slate-400">
            <li>• Vídeo completo: bloqueado até existir um estilo aprovado.</li>
            <li>• Outros estilos (mosaico de blocos, traço anime, cartoon e 3D) ainda não estão prontos.</li>
            <li>• Cada estilo tem 3 tentativas no marco atual.</li>
            <li>• Formatos alvo: 16:9 e 9:16.</li>
          </ul>
        </div>
      </section>

      {/* Projetos recentes */}
      <section>
        <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-slate-400">
          <Clock size={14} aria-hidden="true" /> Projetos recentes
        </h2>
        {carregandoProjetos ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <EsqueletoCartao />
            <EsqueletoCartao />
            <EsqueletoCartao />
          </div>
        ) : projetos.length === 0 ? (
          <EstadoVazio
            titulo="Nenhum projeto por aqui"
            descricao="Crie o primeiro projeto informando o caminho de um vídeo local. A análise e a prévia acontecem na sua máquina."
            acao={
              <Link to="/novo-video" className="botao-primario">
                <Wand2 size={16} aria-hidden="true" /> Novo vídeo
              </Link>
            }
            icone={<Boxes size={22} aria-hidden="true" />}
          />
        ) : (
          <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {projetos.slice(0, 6).map((p) => (
              <li key={p.id} className="cartao p-4">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="truncate text-sm font-semibold text-slate-100">{p.nome}</h3>
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
                  Atualizado em {formatarData(p.atualizado_em)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
