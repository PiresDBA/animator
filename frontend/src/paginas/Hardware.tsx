import { Cpu, Thermometer, MemoryStick, Gauge, HardDrive } from 'lucide-react'
import { useEstudio } from '../contexto/ProvedorEstudio'
import { GraficoLinhas, GraficoLinhaSimples } from '../componentes/Graficos'
import { AvisoInfo, EstadoVazio, TituloSecao } from '../componentes/ui'
import { formatarNumero, formatarPorcentagem } from '../format'
import { formatarHoraCurta } from '../util/grafico'

export default function Hardware() {
  const { hardware, amostras, online, estado } = useEstudio()
  const gpu = hardware.gpus[0]

  const serie = amostras.map((a) => ({
    rotulo: formatarHoraCurta(a.tempo),
    temperatura: a.temperaturaC,
    vram: a.vramUsadaMib,
  }))

  const campos = [
    {
      icone: Cpu,
      rotulo: 'Processador',
      valor: hardware.cpuNome ?? 'Não detectado',
      detalhe: hardware.nucleos
        ? `${hardware.nucleos} núcleos · ${hardware.threads ?? '—'} threads`
        : null,
    },
    {
      icone: MemoryStick,
      rotulo: 'Memória',
      valor: hardware.ramGb ? `${formatarNumero(hardware.ramGb, 1)} GB` : 'n/d',
      detalhe: 'Memória total do sistema',
    },
    {
      icone: Thermometer,
      rotulo: 'Temperatura da GPU',
      valor:
        gpu?.temperaturaC !== null && gpu?.temperaturaC !== undefined
          ? `${formatarNumero(gpu.temperaturaC, 0)} °C`
          : 'n/d',
      detalhe: gpu ? gpu.nome : 'Nenhuma GPU reportada',
    },
    {
      icone: Gauge,
      rotulo: 'Uso da GPU',
      valor:
        gpu?.utilizacaoPct !== null && gpu?.utilizacaoPct !== undefined
          ? formatarPorcentagem(gpu.utilizacaoPct)
          : 'n/d',
      detalhe: 'Utilização no último teste',
    },
    {
      icone: MemoryStick,
      rotulo: 'VRAM em uso',
      valor:
        gpu?.vramUsadaMib !== null && gpu?.vramUsadaMib !== undefined
          ? `${formatarNumero(gpu.vramUsadaMib, 0)} MiB`
          : 'n/d',
      detalhe: gpu?.vramTotalMib
        ? `de ${formatarNumero(gpu.vramTotalMib, 0)} MiB`
        : null,
    },
    {
      icone: HardDrive,
      rotulo: 'Espaço livre',
      valor: hardware.discoLivreGb
        ? `${formatarNumero(hardware.discoLivreGb, 1)} GB`
        : 'n/d',
      detalhe: 'Menor disco detectado',
    },
  ]

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <TituloSecao
        titulo="Hardware"
        descricao="Perfil da máquina e monitor ao vivo de temperatura e uso de VRAM enquanto o pipeline trabalha."
      />

      {!online && (
        <AvisoInfo
          titulo="Backend offline"
          mensagem="O perfil de hardware vem do backend local. Enquanto ele estiver fora do ar, os números ficam desatualizados ou vazios."
        />
      )}

      <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {campos.map((c) => (
          <div key={c.rotulo} className="cartao p-4">
            <div className="flex items-center gap-2">
              <c.icone size={15} className="text-acento" aria-hidden="true" />
              <p className="rotulo">{c.rotulo}</p>
            </div>
            <p className="mt-2 truncate text-base font-semibold text-slate-100" title={c.valor}>
              {c.valor}
            </p>
            {c.detalhe && <p className="mt-0.5 text-xs text-slate-500">{c.detalhe}</p>}
          </div>
        ))}
      </section>

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-1">Monitor ao vivo</h2>
        <p className="mb-4 text-xs text-slate-500">
          Amostras coletadas a cada 5 s pelo backend ({amostras.length} no buffers atual).
        </p>
        <GraficoLinhas dados={serie} altura={280} />
      </section>

      {amostras.length >= 2 && (
        <section className="cartao p-5">
          <h2 className="cartao-titulo mb-4">Uso de VRAM</h2>
          <GraficoLinhaSimples dados={serie} altura={200} />
        </section>
      )}

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3">Benchmark</h2>
        {estado ? (
          <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
            <div>
              <dt className="rotulo">Marco</dt>
              <dd className="mt-1 text-slate-200">{estado.marco}</dd>
            </div>
            <div>
              <dt className="rotulo">Backend</dt>
              <dd className="mt-1 text-slate-200">{estado.backend}</dd>
            </div>
            <div>
              <dt className="rotulo">GPUs</dt>
              <dd className="mt-1 text-slate-200">{hardware.gpus.length}</dd>
            </div>
            <div>
              <dt className="rotulo">Sistema</dt>
              <dd className="mt-1 truncate text-slate-200">{hardware.sistema ?? 'n/d'}</dd>
            </div>
          </dl>
        ) : (
          <EstadoVazio
            titulo="Benchmark indisponível"
            descricao="O perfil de hardware é publicado pelo backend em /api/estado. Com o backend rodando, os números aparecem aqui."
          />
        )}
      </section>
    </div>
  )
}
