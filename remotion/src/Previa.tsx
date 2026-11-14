import React, {useMemo, useState} from 'react';
import {AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame} from 'remotion';
import {resolverFonte} from './fontes';

export type PreviaProps = {
  /** Caminho ou URL do MP4 da prévia. Vazio => placeholder. */
  src: string;
  /** Texto exibido no rodapé da prévia. */
  rotulo: string;
};

const COR_FUNDO = '#0b1220';
const COR_ACENTO = '#22d3ee';

const Placeholder: React.FC<{rotulo: string}> = ({rotulo}) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: COR_FUNDO,
        backgroundImage:
          'radial-gradient(900px 600px at 50% 40%, rgba(34,211,238,0.10), rgba(11,18,32,0) 70%)',
        fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
        color: '#f1f5f9',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 22,
      }}
    >
      <div
        style={{
          width: 132,
          height: 132,
          borderRadius: 34,
          border: '1px solid rgba(34,211,238,0.35)',
          background: 'rgba(34,211,238,0.07)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            marginLeft: 8,
            width: 0,
            height: 0,
            borderTop: '26px solid transparent',
            borderBottom: '26px solid transparent',
            borderLeft: '40px solid rgba(34,211,238,0.85)',
          }}
        />
      </div>
      <div
        style={{
          fontSize: 52,
          fontWeight: 700,
          letterSpacing: -0.8,
          color: '#e2e8f0',
        }}
      >
        prévia indisponível
      </div>
      <div style={{fontSize: 22, color: '#94a3b8', textAlign: 'center'}}>
        informe o arquivo MP4 da prévia no prop <strong>src</strong>
        <br />
        {rotulo}
      </div>
    </AbsoluteFill>
  );
};

/**
 * Prévia de 5 s (150 quadros a 30 fps) reproduzindo o MP4 da prévia.
 */
export const Previa: React.FC<PreviaProps> = ({src, rotulo}) => {
  const frame = useCurrentFrame();
  const [erro, setErro] = useState(false);
  const url = useMemo(() => resolverFonte(src), [src]);

  if (!url || erro) {
    return <Placeholder rotulo={rotulo} />;
  }

  const opacidade = interpolate(
    frame,
    [0, 6, 144, 149],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COR_FUNDO,
        fontFamily: '"Segoe UI", "Helvetica Neue", Arial, sans-serif',
      }}
    >
      <OffthreadVideo
        src={url}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          backgroundColor: COR_FUNDO,
        }}
        onError={() => setErro(true)}
      />
      <AbsoluteFill
        style={{
          opacity: opacidade,
          pointerEvents: 'none',
          background:
            'linear-gradient(to top, rgba(2,6,16,0.85) 0%, rgba(2,6,16,0) 26%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 44,
          bottom: 34,
          display: 'flex',
          alignItems: 'center',
          gap: 14,
          opacity: opacidade,
        }}
      >
        <div
          style={{
            width: 10,
            height: 10,
            borderRadius: '50%',
            background: COR_ACENTO,
            boxShadow: `0 0 14px ${COR_ACENTO}`,
          }}
        />
        <span style={{fontSize: 20, color: '#dbe5f1', letterSpacing: 1.6}}>
          {rotulo.toUpperCase()}
        </span>
      </div>
      <div
        style={{
          position: 'absolute',
          right: 44,
          bottom: 34,
          fontSize: 20,
          color: '#94a3b8',
          letterSpacing: 1.6,
          opacity: opacidade,
        }}
      >
        PRÉVIA 1280×720 · 30 FPS
      </div>
    </AbsoluteFill>
  );
};
