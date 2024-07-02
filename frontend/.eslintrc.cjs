/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution');

module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  parser: '@typescript-eslint/parser',
  extends: [
    'plugin:vue/vue3-essential',
    'plugin:tailwindcss/recommended',
    'plugin:@typescript-eslint/recommended',
    'airbnb-base',
  ],
  overrides: [],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: [
    'vue',
    '@typescript-eslint',
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
    '@typescript-eslint/no-explicit-any': 'off',
    // Disable full warning, and customize the typescript one
    // Warn about unused vars unless they start with an underscore
    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': [
      'warn',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      },
    ],
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
