import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import { ProvedorEstudio } from './contexto/ProvedorEstudio'
import './index.css'

const raiz = document.getElementById('root')
if (!raiz) throw new Error('Elemento #root nao encontrado no index.html')

ReactDOM.createRoot(raiz).render(
  <React.StrictMode>
    <HashRouter>
      <ProvedorEstudio>
        <App />
      </ProvedorEstudio>
    </HashRouter>
  </React.StrictMode>,
)
