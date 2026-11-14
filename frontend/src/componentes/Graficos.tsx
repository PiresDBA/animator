import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  AreaChart,
  Area,
} from 'recharts'
import { ROTULO_CRITERIO, type Criterio } from '../types'
import { formatarHoraCurta } from '../util/grafico'

const CINZA = '#94a3b8'
const ACENTO = '#22d3ee'

export function GraficoRadar({
  notas,
  altura = 260,
}: {
  notas: Partial<Record<Criterio, number>>
  altura?: number
}) {
  const dados = (Object.keys(ROTULO_CRITERIO) as Criterio[]).map((c) => ({
    criterio: ROTULO_CRITERIO[c].split(' ')[0],
    nota: notas[c] ?? 0,
    cheio: (notas[c] ?? 0) > 0,
  }))
  const vazio = dados.every((d) => d.nota === 0)

  return (
    <div style={{ height: altura }} className="w-full">
      {vazio ? (
        <p className="grid h-full place-items-center text-sm text-slate-500">
          Ainda não há notas registradas para esta prévia.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={dados} outerRadius="72%">
            <PolarGrid stroke="#2c3f5c" />
            <PolarAngleAxis dataKey="criterio" tick={{ fill: CINZA, fontSize: 11 }} />
            <PolarRadiusAxis domain={[0, 5]} tick={{ fill: '#64748b', fontSize: 10 }} tickCount={6} />
            <Radar
              name="Notas"
              dataKey="nota"
              stroke={ACENTO}
              fill={ACENTO}
              fillOpacity={0.35}
              isAnimationActive={false}
            />
            <Tooltip
              contentStyle={{
                background: '#0e1626',
                border: '1px solid #2c3f5c',
                borderRadius: 8,
                color: '#e2e8f0',
                fontSize: 12,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}

export interface PontoTempo {
  rotulo: string
  valor: number
}

export function GraficoBarras({
  dados,
  altura = 260,
  nomeSerie = 'Tempo (s)',
  cor = ACENTO,
}: {
  dados: PontoTempo[]
  altura?: number
  nomeSerie?: string
  cor?: string
}) {
  if (dados.length === 0) {
    return (
      <p
        style={{ height: altura }}
        className="grid w-full place-items-center text-sm text-slate-500"
      >
        Sem tempos de geração para exibir.
      </p>
    )
  }
  return (
    <div style={{ height: altura }} className="w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={dados} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="#18253c" vertical={false} />
          <XAxis dataKey="rotulo" tick={{ fill: CINZA, fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={50} />
          <YAxis tick={{ fill: CINZA, fontSize: 11 }} width={44} unit=" s" />
          <Tooltip
            cursor={{ fill: 'rgba(34,211,238,0.08)' }}
            contentStyle={{
              background: '#0e1626',
              border: '1px solid #2c3f5c',
              borderRadius: 8,
              color: '#e2e8f0',
              fontSize: 12,
            }}
            formatter={(v: number | string) => [`${Number(v).toFixed(1)} s`, nomeSerie]}
          />
          <Bar dataKey="valor" name={nomeSerie} fill={cor} radius={[4, 4, 0, 0]} maxBarSize={56} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export interface SerieLinha {
  rotulo: string
  temperatura: number | null
  vram: number | null
}

export function GraficoLinhas({
  dados,
  altura = 260,
}: {
  dados: SerieLinha[]
  altura?: number
}) {
  if (dados.length < 2) {
    return (
      <p
        style={{ height: altura }}
        className="grid w-full place-items-center text-sm text-slate-500"
      >
        Coletando amostras do sensor… são necessários alguns segundos de monitor ao vivo.
      </p>
    )
  }
  return (
    <div style={{ height: altura }} className="w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={dados} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <defs>
            <linearGradient id="gradTemp" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#fb923c" stopOpacity={0.45} />
              <stop offset="100%" stopColor="#fb923c" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gradVram" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={ACENTO} stopOpacity={0.45} />
              <stop offset="100%" stopColor={ACENTO} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#18253c" vertical={false} />
          <XAxis dataKey="rotulo" tick={{ fill: CINZA, fontSize: 11 }} minTickGap={24} />
          <YAxis yAxisId="t" tick={{ fill: CINZA, fontSize: 11 }} width={46} unit=" °C" domain={[0, 'auto']} />
          <YAxis
            yAxisId="v"
            orientation="right"
            tick={{ fill: CINZA, fontSize: 11 }}
            width={58}
            unit=" MiB"
            domain={[0, 'auto']}
          />
          <Tooltip
            contentStyle={{
              background: '#0e1626',
              border: '1px solid #2c3f5c',
              borderRadius: 8,
              color: '#e2e8f0',
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: CINZA }} />
          <Area
            yAxisId="t"
            type="monotone"
            dataKey="temperatura"
            name="Temperatura (°C)"
            stroke="#fb923c"
            fill="url(#gradTemp)"
            strokeWidth={2}
            connectNulls
            isAnimationActive={false}
          />
          <Area
            yAxisId="v"
            type="monotone"
            dataKey="vram"
            name="VRAM (MiB)"
            stroke={ACENTO}
            fill="url(#gradVram)"
            strokeWidth={2}
            connectNulls
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function GraficoLinhaSimples({
  dados,
  altura = 180,
}: {
  dados: SerieLinha[]
  altura?: number
}) {
  if (dados.length < 2) return null
  return (
    <div style={{ height: altura }} className="w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={dados} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="#18253c" vertical={false} />
          <XAxis dataKey="rotulo" tick={{ fill: CINZA, fontSize: 11 }} minTickGap={28} />
          <YAxis tick={{ fill: CINZA, fontSize: 11 }} width={44} domain={[0, 'auto']} />
          <Tooltip
            contentStyle={{
              background: '#0e1626',
              border: '1px solid #2c3f5c',
              borderRadius: 8,
              color: '#e2e8f0',
              fontSize: 12,
            }}
          />
          <Line
            type="monotone"
            dataKey="vram"
            name="VRAM (MiB)"
            stroke={ACENTO}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export { formatarHoraCurta }
