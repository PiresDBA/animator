/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        base: {
          950: '#070c16',
          900: '#0b1220',
          850: '#0e1626',
          800: '#121c2e',
          700: '#18253c',
          600: '#213149',
          500: '#2c3f5c',
        },
        acento: {
          DEFAULT: '#22d3ee',
          suave: '#67e8f9',
          escuro: '#0891b2',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          'Segoe UI',
          'system-ui',
          '-apple-system',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: ['Cascadia Mono', 'Consolas', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        paine: '0 1px 0 0 rgba(255,255,255,0.04) inset, 0 8px 24px -12px rgba(0,0,0,0.8)',
      },
    },
  },
  plugins: [],
}
