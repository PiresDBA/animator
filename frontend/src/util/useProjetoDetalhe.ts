import { useCallback, useEffect, useState } from 'react'
import { api, ErroApi } from '../api'
import type { DetalheProjeto } from '../types'

export function useProjetoDetalhe(projetoId: string | null) {
  const [detalhe, setDetalhe] = useState<DetalheProjeto | null>(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)

  const carregar = useCallback(async () => {
    if (!projetoId) {
      setDetalhe(null)
      setErro(null)
      return
    }
    setCarregando(true)
    setErro(null)
    try {
      const d = await api.projeto(projetoId)
      setDetalhe(d)
    } catch (e) {
      setDetalhe(null)
      setErro(
        e instanceof ErroApi
          ? e.message
          : 'Não foi possível carregar o detalhe do projeto.',
      )
    } finally {
      setCarregando(false)
    }
  }, [projetoId])

  useEffect(() => {
    void carregar()
  }, [carregar])

  return { detalhe, carregando, erro, recarregar: carregar }
}
