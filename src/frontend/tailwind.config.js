/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        tg: {
          accent: '#3390ec',
          accentHover: '#1c7ad6',
          sidebar: '#f4f4f5',
          sidebarHover: '#e6e7eb',
          bubbleIn: '#ffffff',
          bubbleOut: '#eeffde',
          bg: '#ffffff',
          panel: '#ffffff',
          text: '#0f172a',
          mute: '#707579',
          online: '#34c759',
          border: '#e4e4e7',
          danger: '#e53935',
        },
      },
      borderRadius: {
        bubble: '14px',
      },
      fontFamily: {
        sans: ['"Segoe UI"', 'Roboto', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
