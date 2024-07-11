import { sentryVitePlugin } from '@sentry/vite-plugin';
import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd());

  return {
    plugins: [
      vue({
        script: {
          defineModel: true,
        },
      }),
      sentryVitePlugin({
        org: 'thunderbird',
        project: 'appointment-frontend',
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
      extensions: ['.ts', '.js', '.vue'],
    },

    server: {
      host: '0.0.0.0',
      hmr: {
        clientPort: 8080,
      },
      port: 8080,
      watch: {
        usePolling: env.VITE_SERVER_WATCH_POLLING === 'true',
        interval: 1500,
        binaryInterval: 3000,
      },
    },

    build: {
      sourcemap: true,
    },
  }
});
