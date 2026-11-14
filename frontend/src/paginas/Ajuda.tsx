import { LifeBuoy, BookOpen, ShieldCheck, Keyboard } from 'lucide-react'
import { TituloSecao } from '../componentes/ui'

const PERGUNTAS = [
  {
    p: 'Por que não consigo gerar o vídeo completo?',
    r: 'No marco M2 o botão fica bloqueado até que um estilo seja aprovado por avaliação humana. O motivo aparece escrito ao lado do botão, e o backend também responde 403 com o código sem_aprovacao.',
  },
  {
    p: 'Quantas prévias posso gerar?',
    r: 'Até 3 tentativas por estilo. Quando o limite é atingido, o cartão do estilo mostra “Limite atingido” e o botão fica desabilitado.',
  },
  {
    p: 'Como funciona o marcador da linha do tempo?',
    r: 'A prévia tem 5 segundos. Arraste o marcador para escolher onde o trecho começa, ou use as setas do teclado com o marcador selecionado. Com Shift, o passo é de 5 segundos.',
  },
  {
    p: 'Qual a diferença entre Aprovar, Ajustar e Reprovar?',
    r: 'Aprovar marca o estilo como pronto e libera o vídeo completo. Ajustar pede uma nova tentativa com mudanças. Reprovar descarta a prévia e o estilo precisa ser refeito.',
  },
  {
    p: 'As imagens e os vídeos saem do meu computador?',
    r: 'Não. A análise, a prévia e a verificação de segurança rodam localmente. Nuvem está desativada por configuração.',
  },
  {
    p: 'O que significa “backend offline” na barra superior?',
    r: 'Que a API local na porta 8765 não respondeu. A interface continua funcionando e mostra skeletons ou estados vazios. A base da API pode ser ajustada em Configurações.',
  },
]

const CRITERIOS = [
  ['Fidelidade', 'Quanto a animação representa o vídeo original.'],
  ['Identidade visual', 'Se o estilo tem personality consistente ao longo da prévia.'],
  ['Fluidez', 'Se os movimentos parecem naturais e contínuos.'],
  ['Adequação infantil', 'Adequação para o público de 7 a 10 anos.'],
  ['Clareza da história', 'Se dá para entender o que acontece na cena.'],
]

export default function Ajuda() {
  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <TituloSecao
        titulo="Ajuda"
        descricao="Como usar o Estúdio de Animação local, o que cada tela faz e como o marco M2 funciona."
      />

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3 flex items-center gap-2">
          <BookOpen size={15} className="text-acento" aria-hidden="true" />
          Fluxo em quatro passos
        </h2>
        <ol className="space-y-2 text-sm text-slate-400">
          <li>
            <strong className="text-slate-200">1. Entrada.</strong> Informe o caminho de um vídeo
            local e crie o projeto. A análise quebra o vídeo em cenas.
          </li>
          <li>
            <strong className="text-slate-200">2. Estilos.</strong> Escolha entre os estilos
            disponíveis. Os indisponíveis mostram o motivo e o marco em que chegam.
          </li>
          <li>
            <strong className="text-slate-200">3. Prévia.</strong> Posicione o marcador de 5
            segundos, escolha a semente e gere. O progresso aparece na fila e no log ao vivo.
          </li>
          <li>
            <strong className="text-slate-200">4. Revisão.</strong> Dê notas de 1 a 5 estrelas nos
            cinco critérios e registre a decisão.
          </li>
        </ol>
      </section>

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3 flex items-center gap-2">
          <ShieldCheck size={15} className="text-acento" aria-hidden="true" />
          Os cinco critérios de avaliação
        </h2>
        <dl className="space-y-2">
          {CRITERIOS.map(([nome, texto]) => (
            <div key={nome} className="flex flex-col sm:flex-row sm:items-baseline sm:gap-3">
              <dt className="w-44 shrink-0 text-sm font-medium text-slate-200">{nome}</dt>
              <dd className="text-sm text-slate-400">{texto}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3 flex items-center gap-2">
          <LifeBuoy size={15} className="text-acento" aria-hidden="true" />
          Perguntas frequentes
        </h2>
        <dl className="space-y-3">
          {PERGUNTAS.map((item) => (
            <div key={item.p} className="rounded-lg border border-base-800 bg-base-900 px-3 py-2">
              <dt className="text-sm font-medium text-slate-100">{item.p}</dt>
              <dd className="mt-1 text-sm text-slate-400">{item.r}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="cartao p-5">
        <h2 className="cartao-titulo mb-3 flex items-center gap-2">
          <Keyboard size={15} className="text-acento" aria-hidden="true" />
          Atalhos de teclado
        </h2>
        <ul className="space-y-1.5 text-sm text-slate-400">
          <li>• Setas ← → movem o marcador do trecho (Shift = 5 s).</li>
          <li>• Home e End levam o marcador ao começo e ao fim do vídeo.</li>
          <li>• Tab percorre a barra lateral e os controles; o foco fica sempre visível.</li>
          <li>• No slider “antes e depois”, as setas movem o divisor.</li>
        </ul>
      </section>
    </div>
  )
}
