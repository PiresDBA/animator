import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  Home,
  Wand2,
  Images,
  Film,
  FolderKanban,
  Cpu,
  Boxes,
  ListOrdered,
  Settings,
  LifeBuoy,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from 'lucide-react'
import BarraSuperior from './BarraSuperior'

const LINKS = [
  { para: '/', rotulo: 'Início', icone: Home, exato: true },
  { para: '/novo-video', rotulo: 'Novo vídeo', icone: Wand2 },
  { para: '/previas', rotulo: 'Prévias', icone: Images },
  { para: '/videos-completos', rotulo: 'Vídeos completos', icone: Film },
  { para: '/projetos', rotulo: 'Projetos', icone: FolderKanban },
  { para: '/hardware', rotulo: 'Hardware', icone: Cpu },
  { para: '/programas', rotulo: 'Programas', icone: Boxes },
  { para: '/fila', rotulo: 'Fila', icone: ListOrdered },
  { para: '/configuracoes', rotulo: 'Configurações', icone: Settings },
  { para: '/ajuda', rotulo: 'Ajuda', icone: LifeBuoy },
]

export default function Layout() {
  const [recolhida, setRecolhida] = useState(false)
  const [menuAberto, setMenuAberto] = useState(false)

  return (
    <div className="flex min-h-screen bg-base-950">
      {/* Barra lateral recolhível */}
      <aside
        className={[
          'fixed inset-y-0 left-0 z-40 flex shrink-0 flex-col border-r border-base-800 bg-base-900',
          'transition-[width] duration-200 ease-out',
          recolhida ? 'w-[68px]' : 'w-60',
          menuAberto ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        ].join(' ')}
        aria-label="Navegação principal"
      >
        <div className="flex h-14 items-center gap-2 border-b border-base-800 px-3">
          <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-acento font-bold text-base-950">
            E
          </span>
          {!recolhida && (
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-100">Estúdio</p>
              <p className="truncate text-[11px] text-slate-400">Animação local</p>
            </div>
          )}
          <button
            type="button"
            className="ml-auto rounded-md p-1.5 text-slate-400 hover:bg-base-800 hover:text-slate-100 lg:hidden"
            onClick={() => setMenuAberto(false)}
            aria-label="Fechar menu"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto p-2">
          <ul className="space-y-0.5">
            {LINKS.map(({ para, rotulo, icone: Icone, exato }) => (
              <li key={para}>
                <NavLink
                  to={para}
                  end={exato}
                  onClick={() => setMenuAberto(false)}
                  title={recolhida ? rotulo : undefined}
                  className={({ isActive }) =>
                    [
                      'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                      isActive
                        ? 'bg-acento/15 text-acento ring-1 ring-inset ring-acento/40'
                        : 'text-slate-300 hover:bg-base-800 hover:text-slate-100',
                    ].join(' ')
                  }
                >
                  <Icone size={18} className="shrink-0" aria-hidden="true" />
                  {!recolhida && <span className="truncate">{rotulo}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="hidden border-t border-base-800 p-2 lg:block">
          <button
            type="button"
            onClick={() => setRecolhida((v) => !v)}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-base-800 hover:text-slate-100"
            aria-label={recolhida ? 'Expandir barra lateral' : 'Recolher barra lateral'}
            aria-expanded={!recolhida}
          >
            {recolhida ? (
              <PanelLeftOpen size={18} aria-hidden="true" />
            ) : (
              <PanelLeftClose size={18} aria-hidden="true" />
            )}
            {!recolhida && <span>Recolher</span>}
          </button>
        </div>
      </aside>

      {menuAberto && (
        <div
          className="fixed inset-0 z-30 bg-black/60 lg:hidden"
          onClick={() => setMenuAberto(false)}
          aria-hidden="true"
        />
      )}

      <div
        className={[
          'flex min-w-0 flex-1 flex-col transition-[margin] duration-200 ease-out',
          recolhida ? 'lg:ml-[68px]' : 'lg:ml-60',
        ].join(' ')}
      >
        <BarraSuperior onMenu={() => setMenuAberto(true)} />
        <main className="flex-1 px-4 py-5 lg:px-6">
          <Outlet />
        </main>
        <footer className="border-t border-base-800 px-4 py-3 text-xs text-slate-500 lg:px-6">
          Estúdio de Animação local — marco M2. Tudo roda na sua máquina; nenhum vídeo sai do
          computador.
        </footer>
      </div>
    </div>
  )
}
