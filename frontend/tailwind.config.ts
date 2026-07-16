import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#10B981',
        danger: '#EF4444',
        warning: '#F59E0B',
        info: '#0EA5E9',
        cream: {
          DEFAULT: '#F5F2EB', // Cream
          90: '#E5E2DA',      // Cream 90%
          50: '#8C8980',      // Cream 50%
          30: '#595752',      // Cream 30%
          10: '#2D2C2A',      // Cream 10%
        },
        dark: {
          DEFAULT: '#0C0C0C', // Black
          card: '#151515',    // 50% Black
          border: '#242424',  // Black 10%
        },
        coral: {
          DEFAULT: '#E55F73', // Red
        },
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}

export default config
