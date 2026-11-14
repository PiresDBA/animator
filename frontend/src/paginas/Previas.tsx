import { useEffect, useMemo, useState } from 'react'
import { Images, RefreshCw, SplitSquareHorizontal, Layers } from 'lucide-react'
import { api, ErroApi, urlMidia } from '../api'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { useProjetoDetalhe } from '../util/useProjetoDetalhe'
import SeletorProjeto from '../componentes/SeletorProjeto'
import GradePrevias from '../componentes/GradePrevias'
import { ComparacaoLadoALado } from '../componentes/Comparacao'
import SliderAntesDepois from '../componentes/Comparacao'
import PainelDecisao from '../componentes/PainelDecisao'
import Storyboard from '../componentes/Storyboard'
import { GraficoRadar } from '../componentes/Graficos'
import {
  AvisoErro,
  EsqueletoGrade,
  EsqueletoCartao,
  EstadoVazio,
  TituloSecao,
} from '../componentes/ui'
import { formatarDuracao } from '../format'
import type { Previa } from '../types'

export default function Previas() {
  const { projetoAtual, definirProjetoAtual, online } = useEstudio()
  const { detalhe, carregando, erro, recarregar } = useProjetoDetalhe(projetoAtual)

  const [previas, setPrevias] = useState<Previa[]>([])
  const [selecionadas, setSelecionadas] = useState<string[]>([])
  const [erroPrevias, setErroPrevias] = useState<string | null>(null)

  useEffect(() => {
    if (!projetoAtual) {
      setPrevias([])
      return
    }
    let cancelado = false
    void (async () => {
      try {
        const lista = await api.previas(projetoAtual)
        if (!cancelado) setPrevias(lista)
      } catch (e) {
        if (!cancelado) {
          setPrevias([])
          setErroPrevias(
            e instanceof ErroApi ? e.message : 'Não foi possível carregar as prévias.',
          )
        }
      }
    })()
    return () => {
      cancelado = true
    }
  }, [projetoAtual, detalhe])

  const porId = useMemo(() => {
    const m = new Map<string, Previa>()
    for (const p of previas) m.set(p.previa_id, p)
    return m
  }, [previas])

  const a = selecionadas[0] ? (porId.get(selecionadas[0]) ?? null) : null
  const b = selecionadas[1] ? (porId.get(selecionadas[1]) ?? null) : null

  const alternar = (id: string) => {
    setSelecionadas((atuais) => {
      if (atuais.includes(id)) return atuais.filter((x) => x !== id)
      if (atuais.length >= 2) return [atuais[1], id]
      return [...atuais, id]
    })
  }

  const avaliacaoPrevia = useMemo(() => {
    if (!detalhe || !a) return null
    const lista = detalhe.avaliacoes ?? []
    return lista.find((av) => av.previa_id === a.previa_id) ?? null
  }, [detalhe, a])

  const original = detalhe?.meta?.entrada?.video ?? null

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <TituloSecao
        titulo="Prévias e avaliação"
        descricao="Gere prévias de 5 segundos, compare duas versões lado a lado e registre sua decisão com notas de 1 a 5 estrelas."
        acao={
          <button
            type="button"
            className="botao-secundario"
            onClick={() => {
              void recarregar()
              if (projetoAtual) {
                void api.previas(projetoAtual).then(setPrevias).catch(() => undefined)
              }
            }}
          >
            <RefreshCw size={16} aria-hidden="true" /> Atualizar
          </button>
        }
      />

      <SeletorProjeto projetoId={projetoAtual} aoMudar={definirProjetoAtual} />

      {erro && <AvisoErro mensagem={erro} />}
      {erroPrevias && <AvisoErro mensagem={erroPrevias} />}
      {!online && (
        <AvisoErro mensagem="Backend offline: as prévias exibidas são apenas as já carregadas." />
      )}

      {!projetoAtual ? (
        <EstadoVazio
          titulo="Escolha um projeto"
          descricao="As prévias são organizadas por projeto. Selecione um projeto acima para ver as versões geradas."
          icone={<Images size={22} aria-hidden="true" />}
        />
      ) : carregando ? (
        <EsqueletoGrade quantidade={3} />
      ) : previas.length === 0 ? (
        <EstadoVazio
          titulo="Nenhuma prévia gerada"
          descricao="Este projeto ainda não tem prévias. Vá em Novo vídeo, escolha o estilo e gere uma prévia de 5 segundos."
          icone={<Images size={22} aria-hidden="true" />}
        />
      ) : (
        <>
          <section>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-400">
              Grade de prévias
            </h2>
            <GradePrevias
              previas={previas}
              selecionadas={selecionadas}
              aoSelecionar={alternar}
            />
            <p className="mt-2 text-xs text-slate-500">
              Selecione até duas prévias para comparar. A primeira selecionada é a prévia A.
            </p>
          </section>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <section className="cartao p-4">
              <h2 className="cartao-titulo mb-3 flex items-center gap-2">
                <SplitSquareHorizontal size={15} className="text-acento" aria-hidden="true" />
                Comparação lado a lado
              </h2>
              {a && b ? (
                <ComparacaoLadoALado a={a} b={b} />
              ) : (
                <p className="py-6 text-center text-sm text-slate-500">
                  Escolha duas prévias na grade acima para comparar.
                </p>
              )}
            </section>

            <section className="cartao p-4">
              <h2 className="cartao-titulo mb-3 flex items-center gap-2">
                <Layers size={15} className="text-acento" aria-hidden="true" />
                Antes e depois
              </h2>
              {a ? (
                <SliderAntesDepois
                  antes={{ rotulo: 'Vídeo original', caminho: original }}
                  depois={{ rotulo: a.estilo_rotulo, caminho: a.miniatura }}
                />
              ) : (
                <p className="py-6 text-center text-sm text-slate-500">
                  Selecione uma prévia para ver o antes e depois.
                </p>
              )}
            </section>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <PainelDecisao
              previa={a}
              projetoId={projetoAtual}
              aoSalvar={() => void recarregar()}
            />
            <section className="cartao p-4">
              <h2 className="cartao-titulo mb-1">Notas da prévia selecionada</h2>
              <p className="mb-3 text-xs text-slate-500">
                Radar com as cinco notas registradas na última avaliação.
              </p>
              <GraficoRadar notas={avaliacaoPrevia?.notas ?? {}} />
              {avaliacaoPrevia && (
                <p className="mt-2 text-xs text-slate-400">
                  Última decisão: <strong>{avaliacaoPrevia.decisao}</strong>
                  {avaliacaoPrevia.comentario ? ` — ${avaliacaoPrevia.comentario}` : ''}
                </p>
              )}
            </section>
          </div>

          <section className="cartao p-4">
            <h2 className="cartao-titulo mb-3 flex items-center gap-2">
              <Layers size={15} className="text-acento" aria-hidden="true" />
              Storyboard — técnica por cena
            </h2>
            <Storyboard cenas={detalhe?.cenas ?? []} mapa={detalhe?.mapa_tecnicas ?? null} />
          </section>

          {detalhe?.previa && (
            <p className="text-xs text-slate-500">
              Última prévia do projeto: {detalhe.previa.previa_id} ·{' '}
              {formatarDuracao(detalhe.previa.tempo_geracao_s)} de geração · arquivo{' '}
              <span className="font-mono">{urlMidia(detalhe.previa.arquivo) ?? '—'}</span>
            </p>
          )}
        </>
      )}

      {carregando && !previas.length && <EsqueletoCartao linhas={2} />}
    </div>
  )
}
