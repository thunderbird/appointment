// init app
import App from '@/App';
import { createApp } from 'vue';

// pinia state management
import { createPinia } from 'pinia';

// init router
import router from '@/router';

// init localization
import { createI18n } from 'vue-i18n';

// init day.js
import dayjs from 'dayjs';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import duration from 'dayjs/plugin/duration';
import isBetween from 'dayjs/plugin/isBetween';
import isoWeek from 'dayjs/plugin/isoWeek';
import isToday from 'dayjs/plugin/isToday';
import localeData from 'dayjs/plugin/localeData';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import minMax from 'dayjs/plugin/minMax';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import weekday from 'dayjs/plugin/weekday';
import 'dayjs/locale/de';

// language source files
import de from '@/locales/de.json';
import en from '@/locales/en.json';

// init basic css with tailwind imports
import '@/assets/main.css';

// init sentry
// eslint-disable-next-line import/no-extraneous-dependencies
import * as Sentry from '@sentry/vue';

const app = createApp(App);

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      new Sentry.BrowserTracing({
        // Set `tracePropagationTargets` to control for which URLs distributed tracing should be enabled
        tracePropagationTargets: ['localhost', 'stage.appointment.day'],
        routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      }),
      new Sentry.Replay(),
    ],
    // Performance Monitoring
    tracesSampleRate: 1.0, // Capture 100% of the transactions, reduce in production!
    // Session Replay
    replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%. You may want to change it to 100% while in development and then sample at a lower rate in production.
    replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
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
app.provide('bookingUrl', `${protocol}://${import.meta.env.VITE_BASE_URL}/booking/`);

const messages = {
  de, // German
  en, // English
};
const loc = localStorage.getItem('locale') ?? (navigator.language || navigator.userLanguage);
const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: loc,
  fallbackLocale: 'en',
  messages,
});
app.use(i18n);
dayjs.locale(loc);
dayjs.extend(advancedFormat);
dayjs.extend(duration);
dayjs.extend(isBetween);
dayjs.extend(isoWeek);
dayjs.extend(isToday);
dayjs.extend(localeData);
dayjs.extend(localizedFormat);
dayjs.extend(minMax);
dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(weekday);

// provide the configured dayjs instance as well es some helper functions
// TODO: provide method to live update the dayjs locale
app.provide('dayjs', dayjs);
const hDuration = (m) => ((m < 60)
  ? dayjs.duration(m, 'minutes').humanize()
  : dayjs.duration(m / 60, 'hours').humanize());
app.provide('hDuration', hDuration);

// locale aware first day of week
const firstDayOfWeek = dayjs.localeData().firstDayOfWeek();
const isoFirstDayOfWeek = firstDayOfWeek === 0 ? 7 : firstDayOfWeek;
app.provide('isoFirstDayOfWeek', isoFirstDayOfWeek);

// provide unified list of locale weekdays with Monday=1 to Sunday=7 (isoweekdays)
// taking locale first day of week into account
const isoWeekdays = [];
const order = isoFirstDayOfWeek === 7 ? [7,1,2,3,4,5,6] : [1,2,3,4,5,6,7]; // TODO: generate for all starts
order.forEach((i) => {
  const n = i === 7 ? 0 : i;
  isoWeekdays.push({
    iso: i,
    long: dayjs.weekdays()[n],
    short: dayjs.weekdaysShort()[n],
    min: dayjs.weekdaysMin()[n],
  });
});
app.provide('isoWeekdays', isoWeekdays);

// ready? let's go!
app.mount('#app');
