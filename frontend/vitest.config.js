import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import viteConfig from './vite.config';

export default defineConfig({
  viteConfig,
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
    extensions: ['.js', '.vue'],
  },
  test: {
    setupFiles: [
      '/test/setup/fix-fetch.js',
    ],
    globals: true,
    environment: 'jsdom',
    root: fileURLToPath(new URL('./', import.meta.url)),
  },
});
