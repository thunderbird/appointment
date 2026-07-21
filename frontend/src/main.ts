// init app
import App from '@/App.vue';
import { createApp } from 'vue';
import { apiUrlKey, shortUrlKey } from '@/keys';
import { defaultLocale } from '@/utils';
import { config, assertConfigured } from '@/config';

// pinia state management
import { createPinia } from 'pinia';

// init router
import router from '@/router';

// init composables
import useDayJS from '@/composables/dayjs';
import i18ninstance from '@/composables/i18n';

// init basic css with services-ui styles
import '@/assets/styles/main.css';
import '@thunderbirdops/services-ui/style.css';

// init sentry
import * as Sentry from '@sentry/vue';

// Fail loud if the SPA booted without runtime config (the container path has no
// baked fallback -- a missing/empty /config.js would otherwise be silent). See config.ts.
assertConfigured();

const app = createApp(App);
const useSentry = !!config.sentryDsn;

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
    dsn: config.sentryDsn,
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
    tracePropagationTargets: [
      'localhost',
      'https://stage.appointment.day',
      'https://appointment-stage.tb.pro',
      'https://appointment.tb.pro',
      'https://apmt.day',
      'https://apt.mt',
    ],
    sendDefaultPii: false,
  });
}

const pinia = createPinia();
app.use(pinia);
app.use(router);

// init urls
const protocol = config.apiSecure === 'true' ? 'https' : 'http';
const port = config.apiPort ? `:${config.apiPort}` : '';
const apiUrl = `${protocol}://${config.apiUrl}${port}`;
app.provide(apiUrlKey, apiUrl);
app.provide(shortUrlKey, `${protocol}://${config.shortBaseUrl}`);

app.use(i18ninstance);
useDayJS(app, defaultLocale());

// ready? let's go!
app.mount('#app');
