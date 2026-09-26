import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        abyssal: {
          DEFAULT: '#051320',
          900: '#051320',
          950: '#020f1c',
        },
        sapphire: {
          800: '#144c6b',
          900: '#0F3D56',
          950: '#0B2B44',
          990: '#061421',
        },
        cyan: {
          bright: '#00E5FF',
          glow: 'rgba(0, 229, 255, 0.35)',
        },
        titanium: {
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
        },
        diamond: {
          DEFAULT: '#F8FAFC',
          pure: '#FFFFFF',
        },
        dental: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          900: '#134e4a',
        },
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(var(--tw-gradient-stops))',
        'radial-ambient': 'radial-gradient(circle at 50% -20%, rgba(15, 61, 86, 0.45), rgba(5, 19, 32, 1))',
        'cyan-flare': 'radial-gradient(circle at center, rgba(0, 229, 255, 0.25) 0%, transparent 70%)',
      },
      boxShadow: {
        'cyan-glow': '0 0 35px -5px rgba(0, 229, 255, 0.35)',
        'cyan-glow-lg': '0 0 55px -5px rgba(0, 229, 255, 0.50)',
        'glass-card': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-hover': '0 12px 40px 0 rgba(0, 229, 255, 0.20)',
        'fiber-optic': '0 0 15px rgba(0, 229, 255, 0.4), inset 0 0 15px rgba(0, 229, 255, 0.2)',
      },
      animation: {
        'float': 'float 5s ease-in-out infinite',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.85' },
        }
      }
    },
  },
  plugins: [],
};

export default config;
