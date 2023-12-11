import { sentryVitePlugin } from '@sentry/vite-plugin';
import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), sentryVitePlugin({
    org: 'thunderbird',
    project: 'appointment-frontend',
  })],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
    extensions: ['.js', '.vue'],
  },

  server: {
    host: '0.0.0.0',
  },

  build: {
    sourcemap: true,
  },
});
