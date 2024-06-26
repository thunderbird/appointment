/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'plugin:vue/vue3-essential',
    'plugin:tailwindcss/recommended',
    'airbnb-base',
  ],
  overrides: [],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: [
    'vue',
  ],
  rules: {
    'import/extensions': ['error', 'ignorePackages', {
      '': 'never',
      ts: 'never',
      js: 'never',
      vue: 'off',
    }],
    'max-len': 'off', // ['error', { code: 120 }],
    'no-param-reassign': 'off',
    'tailwindcss/no-custom-classname': 'off',
    'import/prefer-default-export': 'off',
    radix: 'off',
  },
  settings: {
    'import/resolver': {
      alias: {
        map: [
          ['@', './src'],
        ],
        extensions: ['.ts', '.js', '.vue'],
      },
    },
  },
};
