import { fileURLToPath } from 'node:url';
import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(viteConfig, defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
    extensions: ['ts', '.js', '.vue'],
  },
  test: {
    setupFiles: [
      '/test/setup/fix-fetch.js',
    ],
    globals: true,
    environment: 'jsdom',
    root: fileURLToPath(new URL('./', import.meta.url)),
  },
}));
