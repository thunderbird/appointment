// init app
import App from '@/App';
import { createApp } from 'vue';
const app = createApp(App);

// init fetch
import { createFetch } from '@vueuse/core'
const call = createFetch({
  baseUrl: 'http://localhost:5000',
  fetchOptions: {
    mode: 'cors',
  },
})
app.provide('call', call);
app.provide('baseurl', 'http://localhost:8080/booking/'); // TODO

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
