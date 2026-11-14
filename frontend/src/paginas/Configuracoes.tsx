import { useEffect, useState } from 'react'
import { Save, Server, Info } from 'lucide-react'
import { API_BASE, baseMidia, definirBaseMidia } from '../api'
import { AvisoInfo, TituloSecao } from '../componentes/ui'

const PADROES = [
  { rotulo: 'Duração da prévia', valor: '5 segundos' },
  { rotulo: 'Tentativas por estilo', valor: '3' },
  { rotulo: 'Resolução padrão', valor: '480p (CPU)' },
  { rotulo: 'Formatos alvo', valor: '16:9 e 9:16' },
  { rotulo: 'Público', valor: 'crianças de 7 a 10 anos' },
  { rotulo: 'Áudio', valor: 'original do vídeo de entrada' },
  { rotulo: 'Legendas', valor: 'queimadas no vídeo final' },
  { rotulo: 'Nuvem', valor: 'desativada — tudo roda local' },
]

export default function Configuracoes() {
  const [apiBase] = useState(API_BASE)
  const [midia, setMidia] = useState(baseMidia())
  const [salvo, setSalvo] = useState<string | null>(null)

  useEffect(() => {
    setMidia(baseMidia())
  }, [])

  const salvar = () => {
    definirBaseMidia(midia)
    setSalvo(
      `Base de mídia salva. Ela vale para esta sessão do navegador; a base da API vem de VITE_API_BASE (${API_BASE}).`,
    )
  }

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <TituloSecao
        titulo="Configurações"
        descricao="Ajustes locais da interface. Nada aqui altera o comportamento do pipeline."
      />

      <section className="cartao space-y-4 p-5">
        <h2 className="cartao-titulo flex items-center gap-2">
          <Server size={15} className="text-acento" aria-hidden="true" />
          Conexão com o backend
        </h2>

        <div>
          <label className="rotulo-campo" htmlFor="api-base">
            Base da API (somente leitura)
          </label>
          <input id="api-base" className="campo font-mono text-xs" value={apiBase} readOnly />
          <p className="mt-1 text-xs text-slate-500">
            Definida pela variável de ambiente <span className="font-mono">VITE_API_BASE</span> no
            momento do build. O padrão é <span className="font-mono">http://127.0.0.1:8765</span>.
          </p>
        </div>

        <div>
          <label className="rotulo-campo" htmlFor="midia-base">
            Base dos arquivos de mídia
          </label>
          <input
            id="midia-base"
            className="campo font-mono text-xs"
            placeholder="http://127.0.0.1:8765"
            value={midia}
            onChange={(e) => setMidia(e.target.value)}
          />
          <p className="mt-1 text-xs text-slate-500">
            Endereço de onde o backend serve os MP4 e as miniaturas. Ajuste apenas se os arquivos
            não aparecerem nas prévias.
          </p>
        </div>

        <button type="button" className="botao-primario" onClick={salvar}>
          <Save size={16} aria-hidden="true" /> Salvar
        </button>

        {salvo && (
          <p
            role="status"
            className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200"
          >
            {salvo}
          </p>
        )}
      </section>

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3 flex items-center gap-2">
          <Info size={15} className="text-acento" aria-hidden="true" />
          Padrões do marco M2
        </h2>
        <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {PADROES.map((p) => (
            <div
              key={p.rotulo}
              className="flex items-center justify-between gap-3 rounded-lg border border-base-800 bg-base-900 px-3 py-2"
            >
              <dt className="text-sm text-slate-400">{p.rotulo}</dt>
              <dd className="text-sm font-medium text-slate-100">{p.valor}</dd>
            </div>
          ))}
        </dl>
        <AvisoInfo
          titulo="Estilos disponíveis"
          mensagem="No marco M2 só o estilo de bonecos de palito está habilitado. Mosaico de blocos, traço anime, cartoon 3D e 3D com materiais reais aparecem na interface como indisponíveis, com o motivo informado."
        />
      </section>
    </div>
  )
}
