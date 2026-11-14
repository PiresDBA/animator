import { useMemo, useState } from 'react'
import { Check, RotateCcw, ThumbsDown, Wand2 } from 'lucide-react'
import { api, ErroApi } from '../api'
import { CRITERIOS, type Avaliacao, type Decisao, type Notas, type Previa } from '../types'
import Estrelas from './Estrelas'
import { AvisoErro } from './ui'

const DECISOES: Array<{
  valor: Decisao
  rotulo: string
  classe: string
  icone: typeof Check
  ajuda: string
}> = [
  {
    valor: 'aprovar',
    rotulo: 'Aprovar',
    classe: 'botao-primario',
    icone: Check,
    ajuda: 'A prévia fica aprovada e libera o vídeo completo.',
  },
  {
    valor: 'ajustar',
    rotulo: 'Ajustar',
    classe: 'botao-secundario',
    icone: RotateCcw,
    ajuda: 'Gere outra tentativa do mesmo estilo com ajustes.',
  },
  {
    valor: 'reprovar',
    rotulo: 'Reprovar',
    classe: 'botao-perigo',
    icone: ThumbsDown,
    ajuda: 'Esta prévia é descartada e o estilo precisa ser refeito.',
  },
]

const NOTAS_INICIAIS: Notas = {
  fidelidade: 0,
  identidade_visual: 0,
  fluidez: 0,
  adequacao_infantil: 0,
  clareza_historia: 0,
}

export default function PainelDecisao({
  previa,
  projetoId,
  aoSalvar,
}: {
  previa: Previa | null
  projetoId: string
  aoSalvar?: (avaliacao: Avaliacao) => void
}) {
  const [notas, setNotas] = useState<Notas>(NOTAS_INICIAIS)
  const [comentario, setComentario] = useState('')
  const [decisao, setDecisao] = useState<Decisao | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [sucesso, setSucesso] = useState<string | null>(null)

  const completo = useMemo(() => CRITERIOS.every((c) => notas[c] >= 1), [notas])

  const submeter = async () => {
    if (!previa || !decisao) return
    setEnviando(true)
    setErro(null)
    setSucesso(null)
    const avaliacao: Avaliacao = {
      id: `av_${Date.now().toString(36)}`,
      previa_id: previa.previa_id,
      estilo: previa.estilo,
      data: new Date().toISOString(),
      decisao,
      notas: { ...notas },
      comentario: comentario.trim(),
      params: {
        seed: previa.params?.seed ?? 0,
        resolucao: previa.params?.resolucao ?? '480p',
        modo: previa.params?.modo ?? 'rapido',
        versao_preset: previa.params?.versao_preset ?? 1,
        trecho_inicio: previa.trecho?.inicio_s ?? 0,
        trecho_fim: previa.trecho?.fim_s ?? 5,
      },
      observacao_responsavel: null,
    }
    try {
      const salva = await api.salvarAvaliacao(avaliacao)
      setSucesso(
        `Decisão registrada: ${DECISOES.find((d) => d.valor === decisao)?.rotulo.toLowerCase()}.`,
      )
      aoSalvar?.(salva ?? avaliacao)
    } catch (e) {
      setErro(
        e instanceof ErroApi
          ? e.message
          : 'Não foi possível salvar a avaliação. Tente de novo.',
      )
    } finally {
      setEnviando(false)
    }
  }

  if (!previa) {
    return (
      <div className="cartao p-4">
        <h2 className="cartao-titulo mb-2">Decisão</h2>
        <p className="text-sm text-slate-400">
          Selecione uma prévia na grade para avaliá-la. As notas vão de 1 a 5 estrelas em cinco
          critérios.
        </p>
      </div>
    )
  }

  return (
    <div className="cartao space-y-4 p-4">
      <div>
        <h2 className="cartao-titulo">Decisão — {previa.estilo_rotulo}</h2>
        <p className="mt-0.5 text-xs text-slate-500">
          Prévia {previa.previa_id} · {previa.trecho?.inicio_s != null ? previa.trecho.inicio_s.toFixed(1) : '0.0'}–
          {previa.trecho?.fim_s != null ? previa.trecho.fim_s.toFixed(1) : '5.0'} s
        </p>
      </div>

      <div>
        <p className="rotulo mb-2">Notas (1 a 5 estrelas)</p>
        <div className="divide-y divide-base-800">
          {CRITERIOS.map((c) => (
            <Estrelas
              key={c}
              criterio={c}
              valor={notas[c]}
              aoMudar={(v) => setNotas((n) => ({ ...n, [c]: v }))}
            />
          ))}
        </div>
        {!completo && (
          <p className="mt-2 text-xs text-amber-300">
            Avalie os cinco critérios antes de enviar a decisão.
          </p>
        )}
      </div>

      <div>
        <label className="rotulo-campo" htmlFor="comentario-avaliacao">
          Comentário (opcional)
        </label>
        <textarea
          id="comentario-avaliacao"
          className="campo min-h-[72px] resize-y"
          placeholder="O que poderia melhorar nesta prévia?"
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
        />
      </div>

      <div>
        <p className="rotulo mb-2">Decisão</p>
        <div className="flex flex-wrap gap-2">
          {DECISOES.map((d) => (
            <button
              key={d.valor}
              type="button"
              className={`${d.classe} ${decisao === d.valor ? 'ring-2 ring-acento ring-offset-2 ring-offset-base-850' : ''}`}
              onClick={() => setDecisao(d.valor)}
              aria-pressed={decisao === d.valor}
              title={d.ajuda}
            >
              <d.icone size={16} aria-hidden="true" />
              {d.rotulo}
            </button>
          ))}
        </div>
        {decisao && (
          <p className="mt-2 flex items-start gap-2 text-xs text-slate-400">
            <Wand2 size={13} className="mt-0.5 shrink-0 text-acento" aria-hidden="true" />
            {DECISOES.find((d) => d.valor === decisao)?.ajuda}
          </p>
        )}
      </div>

      {erro && <AvisoErro mensagem={erro} />}
      {sucesso && (
        <p role="status" className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200">
          {sucesso}
        </p>
      )}

      <button
        type="button"
        className="botao-primario w-full"
        disabled={!completo || !decisao || enviando}
        onClick={() => void submeter()}
      >
        {enviando ? 'Enviando…' : 'Enviar avaliação'}
      </button>
      <p className="text-[11px] text-slate-500">
        A avaliação é gravada em <span className="font-mono">/api/avaliacoes</span> do projeto{' '}
        <span className="font-mono">{projetoId}</span>.
      </p>
    </div>
  )
}
