const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    fontFamily: {
      sans: ['"Open Sans"', ...defaultTheme.fontFamily.sans],
    },
    extend: {
      gridTemplateColumns: {
        'week':    '100px repeat(7, 1fr)',
        'day':     '100px 1fr',
        'context': '28px 1fr',
      },
      maxWidth: {
        '2xs': '16rem'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms')
  ],
}
