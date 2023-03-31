// init app
import App from '@/App';
import { createApp } from 'vue';
const app = createApp(App);

// init auth0
import { createAuth0 } from '@auth0/auth0-vue';
app.use(
  createAuth0({
    domain: process.env.VUE_APP_AUTH0_DOMAIN,
    clientId: process.env.VUE_APP_AUTH0_CLIENT_ID,
    authorizationParams: {
      redirect_uri: window.location.origin,
      audience: process.env.VUE_APP_AUTH0_AUDIENCE,
      // read:calendars is needed for the API
      // even if the user does not have the scope, we still request it
      scope: 'profile email read:calendars'
    },
  })
);

// init urls
const protocol = process.env.VUE_APP_API_SECURE === 'true' ? 'https' : 'http';
const port = process.env.VUE_APP_API_PORT !== undefined ? `:${process.env.VUE_APP_API_PORT}` : '';
const apiUrl = `${protocol}://${process.env.VUE_APP_API_URL}${port}`;
app.provide('apiUrl', apiUrl);
app.provide('bookingUrl', `${protocol}://${process.env.VUE_APP_BASE_URL}/booking/`);

// init router
import router from '@/router';
app.use(router);

// init localization
import { createI18n } from 'vue-i18n';
const messages = {
	"de": require("@/locales/de.json"), // German
	"en": require("@/locales/en.json"), // English
};
const loc = localStorage.locale ?? (navigator.language || navigator.userLanguage);
const i18n = createI18n({
	legacy: false,
	globalInjection: true,
	locale: loc,
	fallbackLocale: "en",
  messages
});
app.use(i18n);

// init day.js
import dayjs from 'dayjs';
import advancedFormat from 'dayjs/plugin/advancedFormat';
import duration from 'dayjs/plugin/duration';
import isBetween from 'dayjs/plugin/isBetween';
import isToday from 'dayjs/plugin/isToday';
import localeData from 'dayjs/plugin/localeData';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import relativeTime from 'dayjs/plugin/relativeTime';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';
import weekday from 'dayjs/plugin/weekday';
import 'dayjs/locale/de';
dayjs.locale(loc);
dayjs.extend(advancedFormat);
dayjs.extend(duration);
dayjs.extend(isBetween);
dayjs.extend(isToday);
dayjs.extend(localeData);
dayjs.extend(localizedFormat);
dayjs.extend(relativeTime);
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(weekday);
// provide the configured dayjs instance as well es some helper functions
app.provide('dayjs', dayjs);
const hDuration = m => {
	return (m < 60)
		? dayjs.duration(m, 'minutes').humanize()
		: dayjs.duration(m/60, 'hours').humanize();
};
app.provide('hDuration', hDuration);

// init basic css with tailwind imports
import '@/assets/main.css';

// ready? let's go!
app.mount('#app');
