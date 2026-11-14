import { useState } from 'react'
import { Film, Lock, PlayCircle } from 'lucide-react'
import { api, ErroApi } from '../api'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { useProjetoDetalhe } from '../util/useProjetoDetalhe'
import SeletorProjeto from '../componentes/SeletorProjeto'
import { AvisoErro, AvisoInfo, EstadoVazio, TituloSecao } from '../componentes/ui'

export default function VideosCompletos() {
  const { projetoAtual, definirProjetoAtual } = useEstudio()
  const { detalhe, carregando, recarregar } = useProjetoDetalhe(projetoAtual)
  const [tentando, setTentando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  const meta = detalhe?.meta
  const aprovado = meta?.aprovado === true
  const estiloAprovado = (meta?.estilos ?? []).find((e) => e.disponivel && e.id === meta?.aprovacao)
  const motivoBloqueio = aprovado
    ? null
    : 'Nenhum estilo foi aprovado ainda. Aprove uma prévia em Prévias e avaliação para liberar a geração do vídeo completo.'

  const tentarGerar = async () => {
    if (!projetoAtual) return
    setTentando(true)
    setErro(null)
    try {
      await api.gerarCompleto(projetoAtual)
      void recarregar()
    } catch (e) {
      if (e instanceof ErroApi) {
        setErro(
          e.codigo === 'sem_aprovacao'
            ? `O backend recusou a geração (403 · ${e.codigo}). ${e.message}`
            : `${e.message} (HTTP ${e.status} · ${e.codigo})`,
        )
      } else {
        setErro('Não foi possível falar com o backend.')
      }
    } finally {
      setTentando(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <TituloSecao
        titulo="Vídeos completos"
        descricao="A geração do vídeo inteiro está bloqueada no marco M2. Ela só é liberada depois que um estilo passa por avaliação humana."
      />

      <SeletorProjeto projetoId={projetoAtual} aoMudar={definirProjetoAtual} />

      {!projetoAtual ? (
        <EstadoVazio
          titulo="Nenhum projeto selecionado"
          descricao="Escolha um projeto para ver a situação da geração do vídeo completo."
          icone={<Film size={22} aria-hidden="true" />}
        />
      ) : carregando ? (
        <div className="cartao h-40 animate-pulse bg-base-800" />
      ) : (
        <>
          <section className="cartao space-y-4 p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="cartao-titulo">{meta?.nome ?? 'Projeto'}</h2>
                <p className="mt-1 font-mono text-xs text-slate-500">{meta?.id}</p>
              </div>
              <span
                className={[
                  'chip',
                  aprovado
                    ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                    : 'border-amber-500/40 bg-amber-500/10 text-amber-300',
                ].join(' ')}
              >
                {aprovado ? 'Estilo aprovado' : 'Aguardando aprovação'}
              </span>
            </div>

            {motivoBloqueio && (
              <AvisoInfo titulo="Geração bloqueada" mensagem={motivoBloqueio} />
            )}

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                className="botao-primario"
                disabled={!aprovado || tentando}
                onClick={() => void tentarGerar()}
                aria-describedby="motivo-bloqueio"
              >
                {aprovado ? (
                  <PlayCircle size={16} aria-hidden="true" />
                ) : (
                  <Lock size={16} aria-hidden="true" />
                )}
                {tentando ? 'Enfileirando…' : 'Gerar vídeo completo'}
              </button>

              {!aprovado && (
                <span id="motivo-bloqueio" className="text-xs text-slate-400">
                  Bloqueado: {motivoBloqueio}
                </span>
              )}
            </div>

            {aprovado && estiloAprovado && (
              <p className="text-xs text-slate-400">
                Estilo aprovado: <strong>{estiloAprovado.rotulo}</strong>.
              </p>
            )}

            {erro && <AvisoErro mensagem={erro} />}
          </section>

          <section className="cartao p-5">
            <h2 className="cartao-titulo mb-2">Saídas completas</h2>
            <p className="text-sm text-slate-400">
              Ainda não há vídeos completos neste projeto. No marco M2 o único produto liberado é
              a prévia de 5 segundos.
            </p>
            <ul className="mt-3 space-y-1 text-xs text-slate-500">
              <li>• Formatos alvo: 16:9 e 9:16.</li>
              <li>• Áudio original mantido e legendas queimadas.</li>
              <li>• Nada é enviado para a nuvem: a renderização é local.</li>
            </ul>
          </section>
        </>
      )}
    </div>
  )
}
