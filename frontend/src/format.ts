/** Formatacao pt-BR (Intl) usada em toda a interface. */

const locale = 'pt-BR'

export function formatarData(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return new Intl.DateTimeFormat(locale, {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(d)
}

export function formatarDataHoraCurta(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return new Intl.DateTimeFormat(locale, {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(d)
}

export function formatarNumero(valor: number | null | undefined, casas = 0): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—'
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: casas,
    maximumFractionDigits: casas,
  }).format(valor)
}

export function formatarPorcentagem(valor: number | null | undefined, casas = 0): string {
  if (valor === null || valor === undefined || Number.isNaN(valor)) return '—'
  return `${formatarNumero(valor, casas)}%`
}

/** Duracao em segundos -> "1 min 05 s" / "12,3 s". */
export function formatarDuracao(segundos: number | null | undefined): string {
  if (segundos === null || segundos === undefined || Number.isNaN(segundos)) return '—'
  if (segundos < 60) return `${formatarNumero(segundos, 1)} s`
  const min = Math.floor(segundos / 60)
  const seg = Math.round(segundos % 60)
  return `${min} min ${String(seg).padStart(2, '0')} s`
}

/** Segundos -> "mm:ss" (relogio). */
export function formatarTempo(segundos: number | null | undefined): string {
  if (segundos === null || segundos === undefined || Number.isNaN(segundos)) return '0:00'
  const total = Math.max(0, Math.floor(segundos))
  const min = Math.floor(total / 60)
  const seg = total % 60
  return `${min}:${String(seg).padStart(2, '0')}`
}

export function formatarBytes(bytes: number | null | undefined): string {
  if (!bytes || Number.isNaN(bytes)) return '—'
  const unidades = ['B', 'KB', 'MB', 'GB', 'TB']
  let valor = bytes
  let i = 0
  while (valor >= 1024 && i < unidades.length - 1) {
    valor /= 1024
    i += 1
  }
  return `${formatarNumero(valor, i === 0 ? 0 : 1)} ${unidades[i]}`
}

export function formatarMiB(mib: number | null | undefined): string {
  if (mib === null || mib === undefined || Number.isNaN(mib)) return '—'
  return `${formatarNumero(mib, 0)} MiB`
}

/** Rotulo amigavel para os estilos (nunca usar marca registrada). */
export function rotuloEstilo(id: string): string {
  const mapa: Record<string, string> = {
    bonecos: 'Bonecos de palito',
    lego: 'Mosaico de blocos',
    anime: 'Traço anime',
    cartoon: 'Cartoon 3D estilizado',
    '3d': '3D com materiais realistas',
  }
  return mapa[id] ?? id
}
