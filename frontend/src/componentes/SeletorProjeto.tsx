import { useEstudio } from '../contexto/ProvedorEstudio'

/** Seletor de projeto, usado nas paginas que operam sobre um projeto. */
export default function SeletorProjeto({
  projetoId,
  aoMudar,
}: {
  projetoId: string | null
  aoMudar: (id: string) => void
}) {
  const { projetos, carregandoProjetos, online } = useEstudio()

  if (!online) {
    return (
      <p className="text-sm text-amber-300">
        Backend offline: a lista de projetos não pode ser carregada agora.
      </p>
    )
  }
  if (carregandoProjetos) {
    return <p className="text-sm text-slate-400">Carregando projetos…</p>
  }
  if (projetos.length === 0) {
    return (
      <p className="text-sm text-slate-400">
        Nenhum projeto ainda. Comece em <strong>Novo vídeo</strong>.
      </p>
    )
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <label className="rotulo" htmlFor="seletor-projeto">
        Projeto
      </label>
      <select
        id="seletor-projeto"
        className="campo w-auto min-w-[220px]"
        value={projetoId ?? ''}
        onChange={(e) => aoMudar(e.target.value)}
      >
        <option value="">Escolha um projeto…</option>
        {projetos.map((p) => (
          <option key={p.id} value={p.id}>
            {p.nome} — {p.id}
          </option>
        ))}
      </select>
    </div>
  )
}
