// init app
import App from '@/App.vue';
import { createApp } from 'vue';
import { apiUrlKey, bookingUrlKey, shortUrlKey } from '@/keys';
import { defaultLocale } from '@/utils';

// pinia state management
import { createPinia } from 'pinia';

// init router
import router from '@/router';

// init composables
import useDayJS from '@/composables/dayjs';
import i18ninstance from '@/composables/i18n';

// init basic css with tailwind imports
import '@/assets/styles/main.css';

// init sentry
 
import * as Sentry from '@sentry/vue';

const app = createApp(App);
const useSentry = !!import.meta.env.VITE_SENTRY_DSN;

// The modes we use -> short names for sorting
const environmentMap = {
  // Development is used by vite in dev mode...
  development: 'dev',
  // We set these correctly :)
  stage: 'stage',
  prod: 'prod',
};
const environment = environmentMap[import.meta.env.MODE] ?? 'unknown';

if (useSentry) {
  Sentry.init({
    app,
    environment,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      Sentry.browserTracingIntegration({
        router,
      }),
      Sentry.replayIntegration(),
    ],

    // Performance Monitoring
    // Capture 100% of the transactions, reduce in production!
    tracesSampleRate: 1.0,
    // Session Replay
    // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a
    // lower rate in production.
    replaysSessionSampleRate: 0.1,
    // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where
    // errors occur.
    replaysOnErrorSampleRate: 1.0,
    // Set `tracePropagationTargets` to control for which URLs distributed tracing should be enabled
    tracePropagationTargets: ['localhost', 'https://stage.appointment.day', 'https://appointment.day', 'https://apmt.day'],
    sendDefaultPii: false,
  });
}

const pinia = createPinia();
app.use(pinia);
app.use(router);

// init urls
const protocol = import.meta.env.VITE_API_SECURE === 'true' ? 'https' : 'http';
const port = import.meta.env.VITE_API_PORT !== undefined ? `:${import.meta.env.VITE_API_PORT}` : '';
const apiUrl = `${protocol}://${import.meta.env.VITE_API_URL}${port}`;
app.provide(apiUrlKey, apiUrl);
app.provide(bookingUrlKey, `${protocol}://${import.meta.env.VITE_BASE_URL}/appointments/all/`);
app.provide(shortUrlKey, `${protocol}://${import.meta.env.VITE_SHORT_BASE_URL}`);

app.use(i18ninstance);
useDayJS(app, defaultLocale());

// ready? let's go!
app.mount('#app');
