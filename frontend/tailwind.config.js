const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: ['./public/index.html', './src/**/*.{vue,js}'],
  theme: {
    fontFamily: {
      sans: ['"Open Sans"', ...defaultTheme.fontFamily.sans],
      display: ['"Raleway"', ...defaultTheme.fontFamily.sans],
      roboto: ['"Roboto"', ...defaultTheme.fontFamily.sans],
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
      scale: {
        102: '1.02',
        98: '0.98',
      },
      strokeWidth: {
        3: '3',
      },
    },
  },
  darkMode: 'class',
  plugins: [require('@tailwindcss/forms')],
};
