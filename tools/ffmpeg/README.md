# FFmpeg local

Build: `ffmpeg 8.1-full_build-www.gyan.dev`
Origem: instalação WinGet `Gyan.FFmpeg`, copiada para esta pasta em 2026-11-14.
Licença do build: GPLv3 (`--enable-gpl --enable-version3 --enable-libx264`).

| Arquivo | SHA-256 |
|---|---|
| `ffmpeg.exe` | `D1E2A156261ECC675081943197A85F08F2868784A0AF499171EDE89353EDAD31` |
| `ffprobe.exe` | `70872C3FFBC43D0B2C570F9837F54D6E9A832F4CA25463E9735B6A3EC0621478` |

Os binários são ignorados pelo git (`.gitignore`: `tools/ffmpeg/*.exe`) para não
inflar o repositório. Para reconstruir o ambiente, instale o FFmpeg 8.1 full do
Gyan ou copie os dois executáveis para esta pasta.

Teste de fumaça do M0: MP4 de 1,0 s, H.264 + AAC, 12.388 bytes
(`docs/evidencias/m0_ffmpeg_smoke.mp4`).
