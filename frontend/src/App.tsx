import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './componentes/Layout'
import Inicio from './paginas/Inicio'
import NovoVideo from './paginas/NovoVideo'
import Previas from './paginas/Previas'
import VideosCompletos from './paginas/VideosCompletos'
import Projetos from './paginas/Projetos'
import Hardware from './paginas/Hardware'
import Programas from './paginas/Programas'
import Fila from './paginas/Fila'
import Configuracoes from './paginas/Configuracoes'
import Ajuda from './paginas/Ajuda'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Inicio />} />
        <Route path="/novo-video" element={<NovoVideo />} />
        <Route path="/previas" element={<Previas />} />
        <Route path="/videos-completos" element={<VideosCompletos />} />
        <Route path="/projetos" element={<Projetos />} />
        <Route path="/hardware" element={<Hardware />} />
        <Route path="/programas" element={<Programas />} />
        <Route path="/fila" element={<Fila />} />
        <Route path="/configuracoes" element={<Configuracoes />} />
        <Route path="/ajuda" element={<Ajuda />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
