import { sentryVitePlugin } from '@sentry/vite-plugin';
import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

const plugins = [vue()];
if (import.meta.env?.VITE_SENTRY_DSN) {
  plugins.push(sentryVitePlugin({
    org: 'thunderbird',
    project: 'appointment-frontend',
  }));
}

export default defineConfig({
  plugins: plugins,

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
