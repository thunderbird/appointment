import jsLint from '@eslint/js';
import tsLint from 'typescript-eslint';
import importPlugin from 'eslint-plugin-import';
import vueLint from 'eslint-plugin-vue';
import vueTsEslintConfig from '@vue/eslint-config-typescript';
import globals from "globals";

export default [
  jsLint.configs.recommended,
  ...tsLint.configs.recommended,
  importPlugin.flatConfigs.recommended,
  ...vueLint.configs['flat/essential'],
  ...vueTsEslintConfig(),
  {
    files: [
      '**/*.vue',
      '**/*.js',
      '**/*.jsx',
      '**/*.cjs',
      '**/*.mjs',
      '**/*.ts',
      '**/*.tsx',
      '**/*.cts',
      '**/*.mts',
    ],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser,
        global: 'readonly',
      },
    },
    rules: {
      'import/extensions': ['error', 'ignorePackages', {
        '': 'never',
        ts: 'never',
        js: 'never',
        vue: 'off',
      }],
      'no-param-reassign': 'off',
      'import/prefer-default-export': 'off',
      'radix': 'off',
      'dot-notation': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      // Disable full warning, and customize the typescript one
      // Warn about unused vars unless they start with an underscore
      'no-unused-vars': 'off',
      '@typescript-eslint/no-require-imports': 'off', // can be removed when we got rid of Tailwind or updated to v4
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
        typescript: true,
        node: true,
      },
    },
  },
  {
    ignores: [
      '**/.*',
      'src/assets/*',
      'src/elements/arts/*',
      'src/locales/*',
      'node_modules/*',
    ],
  }
];
