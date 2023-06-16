module.exports = {
  env: {
    browser: true,
    es2021: true,
  },
  extends: [
    'plugin:vue/vue3-essential',
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
      js: 'never',
      vue: 'off', // TODO: once migrated to Vite, we should set this to 'always'
    }],
    'max-len': ['error', { code: 120 }],
    'no-param-reassign': 'off',
  },
  settings: {
    'import/resolver': {
      webpack: {
        config: require.resolve('@vue/cli-service/webpack.config.js'),
      },
    },
  },
};
