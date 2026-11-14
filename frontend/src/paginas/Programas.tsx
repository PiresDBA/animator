import { Boxes, ExternalLink } from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { AvisoInfo, EstadoVazio, TituloSecao } from '../componentes/ui'

const DESCRICOES: Record<string, string> = {
  comfyui: 'Geração de imagens por difusão (não usada na Fase A).',
  effectcraft: 'Composição e efeitos de motion graphics local.',
  ffmpeg: 'Codificação de vídeo, extração de áudio e thumbnails.',
  ffprobe: 'Leitura de metadados dos vídeos.',
  motor_bonecos: 'Motor local de bonecos de palito (stick-film).',
  remotion: 'Render de composição local com React.',
  videofactoryai: 'Fábrica local de vídeos (uso opcional).',
}

export default function Programas() {
  const { programas, online } = useEstudio()

  return (
    <div className="mx-auto max-w-5xl space-y-5">
      <TituloSecao
        titulo="Programas"
        descricao="Ferramentas locais detectadas na varredura somente leitura do computador. Nada é instalado por esta interface."
      />

      {!online && (
        <AvisoInfo
          titulo="Backend offline"
          mensagem="A lista de programas vem de /api/estado. Com o backend fora do ar, não é possível confirmar o que está instalado."
        />
      )}

      {programas.length === 0 ? (
        <EstadoVazio
          titulo="Nenhum programa reportado"
          descricao="Quando o backend estiver rodando, ele publica aqui os programas encontrados na varredura local."
          icone={<Boxes size={22} aria-hidden="true" />}
        />
      ) : (
        <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {programas.map((p, i) => (
            <li key={`${p.nome}-${p.caminho ?? i}`} className="cartao p-4">
              <div className="flex items-start justify-between gap-2">
                <h3 className="text-sm font-semibold text-slate-100">{p.nome}</h3>
                <span
                  className={[
                    'chip',
                    p.disponivel
                      ? 'border-emerald-500/40 text-emerald-300'
                      : 'border-amber-500/40 text-amber-300',
                  ].join(' ')}
                >
                  {p.disponivel ? 'Detectado' : 'Indisponível'}
                </span>
              </div>
              {DESCRICOES[p.nome] && (
                <p className="mt-1 text-xs text-slate-400">{DESCRICOES[p.nome]}</p>
              )}
              {p.caminho && (
                <p className="mt-2 flex items-start gap-1 break-all font-mono text-[11px] text-slate-500">
                  <ExternalLink size={12} className="mt-0.5 shrink-0" aria-hidden="true" />
                  {p.caminho}
                </p>
              )}
              {p.detalhe && <p className="mt-1 text-[11px] text-slate-500">{p.detalhe}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
