import type { Config } from 'tailwindcss';

const defaultTheme = require('tailwindcss/defaultTheme');

export default {
  content: ['./public/index.html', './src/**/*.{vue,ts,js}'],
  theme: {
    fontFamily: {
      sans: ['"Inter"', ...defaultTheme.fontFamily.sans],
    },
    extend: {
      gridTemplateColumns: {
        week: '100px repeat(7, 1fr)',
        day: '100px 1fr',
        context: '28px 1fr',
      },
      maxWidth: {
        '2xs': '16rem',
      },
      maxHeight: {
        lg: '32rem',
        xl: '36rem',
      },
      scale: {
        102: '1.02',
        98: '0.98',
      },
      strokeWidth: {
        3: '3',
      },
      colors: {
        'tb-red': {
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },
      },
    },
  },
  darkMode: 'class',
  plugins: [require('@tailwindcss/forms')],
} satisfies Config;
