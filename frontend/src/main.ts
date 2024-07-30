// init app
import App from '@/App.vue';
import { createApp } from 'vue';
import { getPreferredTheme } from '@/utils';

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
// eslint-disable-next-line import/no-extraneous-dependencies
import * as Sentry from '@sentry/vue';
// eslint-disable-next-line import/no-extraneous-dependencies
import posthog from 'posthog-js';
import { usePosthogKey } from '@/keys';

const app = createApp(App);
const useSentry = !!import.meta.env.VITE_SENTRY_DSN;
const usePosthog = !!import.meta.env.VITE_POSTHOG_PROJECT_KEY;

app.provide(usePosthogKey, usePosthog);

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
    tracePropagationTargets: ['localhost', 'stage.appointment.day', 'appointment.day'],
  });
}

if (usePosthog) {
  posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_KEY, {
    api_host: import.meta.env.VITE_POSTHOG_HOST,
    person_profiles: 'identified_only',
    persistence: 'memory',
  });
  posthog.register({
    service: 'apmt',
  });
}

const pinia = createPinia();
app.use(pinia);
app.use(router);

// init urls
const protocol = import.meta.env.VITE_API_SECURE === 'true' ? 'https' : 'http';
const port = import.meta.env.VITE_API_PORT !== undefined ? `:${import.meta.env.VITE_API_PORT}` : '';
const apiUrl = `${protocol}://${import.meta.env.VITE_API_URL}${port}`;
app.provide('apiUrl', apiUrl);
app.provide('bookingUrl', `${protocol}://${import.meta.env.VITE_BASE_URL}/appointments/all/`);

const loc = localStorage?.getItem('locale') ?? navigator.language;
app.use(i18ninstance);
useDayJS(app, loc);

// ready? let's go!
app.mount('#app');
