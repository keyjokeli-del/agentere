/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        dental: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          900: '#134e4a',
        },
        sapphire: {
          800: '#144c6b',
          900: '#0F3D56',
          950: '#082231',
        },
        cyan: {
          bright: '#00E5FF',
          glow: 'rgba(0, 229, 255, 0.35)',
        }
      },
      boxShadow: {
        'cyan-glow': '0 0 40px -8px rgba(0, 229, 255, 0.4)',
        'glass-card': '0 8px 32px 0 rgba(0, 0, 0, 0.25)',
      },
      animation: {
        'float': 'float 5s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
