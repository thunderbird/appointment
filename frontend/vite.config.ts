import { sentryVitePlugin } from '@sentry/vite-plugin';
import { fileURLToPath, URL } from 'node:url';

import { defineConfig, loadEnv, WatchOptions } from 'vite';
import vue from '@vitejs/plugin-vue';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd());

  // Build watch options
  const watch = {
    usePolling: env.VITE_SERVER_WATCH_POLLING === 'true'
  } as WatchOptions;
  if (env.VITE_SERVER_WATCH_INTERVAL) {
    watch.interval = Number(env.VITE_SERVER_WATCH_INTERVAL);
  }
  if (env.VITE_SERVER_WATCH_BINARY_INTERVAL) {
    watch.binaryInterval = Number(env.VITE_SERVER_WATCH_BINARY_INTERVAL);
  }

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
      watch: watch,
    },

    build: {
      sourcemap: true,
    },
  }
});
