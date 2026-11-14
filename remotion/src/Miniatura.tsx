import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill,
  Img,
  continueRender,
  delayRender,
  staticFile,
} from 'remotion';

export type MiniaturaProps = {
  /** Nome do projeto exibido no cartão de título. */
  nome: string;
};

const COR_FUNDO = '#0b1220';
const COR_ACENTO = '#22d3ee';

const tamanhoDoTitulo = (nome: string): number => {
  const n = nome.trim().length;
  if (n <= 14) {
    return 104;
  }
  if (n <= 22) {
    return 88;
  }
  if (n <= 30) {
    return 72;
  }
  return 60;
};

/**
 * Cartão de título usado como miniatura da prévia (1 quadro).
 * Carregamento da imagem usa delayRender/continueRender para que o render
 * só avance quando o recurso estiver pronto.
 */
export const Miniatura: React.FC<MiniaturaProps> = ({nome}) => {
  const [handle] = useState(() => delayRender('Carregando emblema da miniatura'));
  const [emblemaPronto, setEmblemaPronto] = useState(false);
  const [emblemaFalhou, setEmblemaFalhou] = useState(false);

  useEffect(() => {
    const imagem = new Image();
    imagem.onload = () => {
      setEmblemaPronto(true);
      continueRender(handle);
    };
    imagem.onerror = () => {
      setEmblemaFalhou(true);
      continueRender(handle);
    };
    imagem.src = staticFile('emblem.svg');
  }, [handle]);

  const titulo = nome.trim().length > 0 ? nome.trim() : 'Projeto sem nome';

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COR_FUNDO,
        fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
        color: '#f1f5f9',
        overflow: 'hidden',
      }}
    >
      {/* brilho ciano no alto à direita */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(880px 640px at 80% 12%, rgba(34,211,238,0.20), rgba(11,18,32,0) 62%)',
        }}
      />
      {/* brilho frio embaixo à esquerda */}
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(760px 520px at 8% 96%, rgba(56,189,248,0.12), rgba(11,18,32,0) 65%)',
        }}
      />
      {/* grade técnica */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(to right, rgba(148,163,184,0.07) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.07) 1px, transparent 1px)',
          backgroundSize: '64px 64px',
        }}
      />
      {/* barra diagonal de acento */}
      <div
        style={{
          position: 'absolute',
          top: -180,
          right: 34,
          width: 54,
          height: 1100,
          background:
            'linear-gradient(to bottom, rgba(34,211,238,0.00), rgba(34,211,238,0.10), rgba(34,211,238,0.00))',
          transform: 'rotate(18deg)',
        }}
      />

      {/* cabeçalho */}
      <div
        style={{
          position: 'absolute',
          top: 64,
          left: 84,
          display: 'flex',
          alignItems: 'center',
          gap: 20,
        }}
      >
        <div
          style={{
            width: 84,
            height: 84,
            borderRadius: 22,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(34,211,238,0.07)',
            border: '1px solid rgba(34,211,238,0.35)',
          }}
        >
          {emblemaPronto ? (
            <Img src={staticFile('emblem.svg')} style={{width: 56, height: 56}} />
          ) : (
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: 16,
                background: emblemaFalhou
                  ? 'rgba(148,163,184,0.25)'
                  : 'rgba(34,211,238,0.25)',
              }}
            />
          )}
        </div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
          <div
            style={{
              fontSize: 19,
              fontWeight: 700,
              letterSpacing: 4.5,
              color: COR_ACENTO,
              textTransform: 'uppercase',
            }}
          >
            Cartão de título
          </div>
          <div style={{fontSize: 15, color: '#94a3b8', letterSpacing: 1.2}}>
            M2 · animação local · bonecos de palito
          </div>
        </div>
      </div>

      {/* título principal */}
      <div
        style={{
          position: 'absolute',
          left: 84,
          top: 232,
          width: 700,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            fontSize: tamanhoDoTitulo(titulo),
            lineHeight: 1.02,
            fontWeight: 800,
            letterSpacing: -2,
            color: '#f8fafc',
            textShadow: '0 8px 34px rgba(0,0,0,0.55)',
          }}
        >
          {titulo}
        </div>
        <div
          style={{
            marginTop: 26,
            width: 148,
            height: 9,
            borderRadius: 5,
            background: `linear-gradient(to right, ${COR_ACENTO}, rgba(34,211,238,0.10))`,
          }}
        />
        <div
          style={{
            marginTop: 24,
            fontSize: 25,
            color: '#a7b6cc',
            fontWeight: 400,
            lineHeight: 1.35,
          }}
        >
          Prévia de 5 s · estilo bonecos de palito
          <br />
          Miniatura gerada a partir do primeiro quadro da prévia
        </div>
      </div>

      {/* cartão de pré-visualização à direita */}
      <div
        style={{
          position: 'absolute',
          right: 92,
          top: 214,
          width: 372,
          height: 236,
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 18,
            border: '1px solid rgba(148,163,184,0.16)',
            background: 'rgba(15,26,46,0.55)',
            transform: 'translate(26px, 26px) rotate(4deg)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 18,
            border: '1px solid rgba(148,163,184,0.24)',
            background: 'rgba(15,26,46,0.75)',
            transform: 'translate(12px, 12px) rotate(2deg)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 18,
            border: '1px solid rgba(34,211,238,0.45)',
            background:
              'linear-gradient(150deg, rgba(34,211,238,0.16), rgba(11,18,32,0.98) 62%)',
            boxShadow: '0 26px 60px rgba(0,0,0,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div
            style={{
              width: 86,
              height: 86,
              borderRadius: '50%',
              border: '2px solid rgba(34,211,238,0.75)',
              background: 'rgba(34,211,238,0.14)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <div
              style={{
                marginLeft: 7,
                width: 0,
                height: 0,
                borderTop: '17px solid transparent',
                borderBottom: '17px solid transparent',
                borderLeft: '27px solid #22d3ee',
              }}
            />
          </div>
        </div>
      </div>

      {/* linha do tempo decorativa */}
      <div
        style={{
          position: 'absolute',
          right: 92,
          top: 500,
          width: 372,
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
        }}
      >
        <div
          style={{
            fontSize: 13,
            letterSpacing: 3,
            color: '#7f8ea6',
            textTransform: 'uppercase',
          }}
        >
          Linha do tempo
        </div>
        <div
          style={{
            height: 8,
            borderRadius: 4,
            background: 'rgba(148,163,184,0.18)',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: '38%',
              height: '100%',
              background: `linear-gradient(to right, ${COR_ACENTO}, rgba(34,211,238,0.45))`,
            }}
          />
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between'}}>
          <span style={{fontSize: 13, color: '#7f8ea6'}}>0 s</span>
          <span style={{fontSize: 13, color: '#7f8ea6'}}>5 s</span>
        </div>
      </div>

      {/* rodapé */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 92,
          borderTop: '1px solid rgba(148,163,184,0.14)',
          background: 'linear-gradient(to top, rgba(2,6,16,0.85), rgba(2,6,16,0.25))',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 84px',
        }}
      >
        <div style={{display: 'flex', alignItems: 'center', gap: 14}}>
          <div
            style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: COR_ACENTO,
              boxShadow: `0 0 14px ${COR_ACENTO}`,
            }}
          />
          <span style={{fontSize: 15, color: '#c7d3e3', letterSpacing: 1.4}}>
            MINHATURA · 1280×720
          </span>
        </div>
        <div style={{display: 'flex', gap: 26}}>
          <span style={{fontSize: 15, color: '#7f8ea6', letterSpacing: 1.4}}>
            30 FPS
          </span>
          <span style={{fontSize: 15, color: '#7f8ea6', letterSpacing: 1.4}}>
            1 QUADRO
          </span>
          <span style={{fontSize: 15, color: '#7f8ea6', letterSpacing: 1.4}}>
            ESTÚDIO LOCAL
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
