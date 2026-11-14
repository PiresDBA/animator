import React from 'react';
import {Composition} from 'remotion';
import {Miniatura, type MiniaturaProps} from './Miniatura';
import {Previa, type PreviaProps} from './Previa';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Miniatura"
        component={Miniatura}
        durationInFrames={1}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{nome: 'Estúdio de Animação'} satisfies MiniaturaProps}
      />
      <Composition
        id="Previa"
        component={Previa}
        durationInFrames={150}
        fps={30}
        width={1280}
        height={720}
        defaultProps={{src: '', rotulo: 'Prévia de 5 s'} satisfies PreviaProps}
      />
    </>
  );
};
