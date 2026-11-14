/**
 * Converte o prop `src` em uma URL reproduzivel pelo <OffthreadVideo>.
 *
 * - `https://` / `http://`  -> usado como esta (servidor de midia).
 * - `file://`                -> usado como esta.
 * - `C:\dir\video.mp4`       -> `file:///C:/dir/video.mp4`.
 * - `/dir/video.mp4`         -> `file:///dir/video.mp4`.
 * - `video.mp4`              -> servido a partir da pasta `public/` do projeto.
 */
export const resolverFonte = (src: string | undefined | null): string | null => {
  const bruto = (src ?? '').trim();
  if (!bruto) {
    return null;
  }

  if (/^(https?|file|data|blob):/i.test(bruto)) {
    return bruto;
  }

  const normalizado = bruto.replace(/\\/g, '/');

  if (/^[a-zA-Z]:\//.test(normalizado)) {
    return `file:///${normalizado}`;
  }

  if (normalizado.startsWith('/')) {
    return `file://${normalizado}`;
  }

  // Caminho relativo: servido pela pasta `public/` do projeto Remotion.
  const base = (globalThis as {window?: {remotion_staticBase?: string}}).window
    ?.remotion_staticBase;

  if (typeof base === 'string' && base.length > 0) {
    return `${base.replace(/\/+$/, '')}/${normalizado.replace(/^\/+/, '')}`;
  }

  return `/${normalizado}`;
};
