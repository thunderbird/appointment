// init app
import { createApp } from 'vue';
import App from './App.vue';
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
app.provide('baseurl', 'https://apmt.day/'); // TODO

// init router
import router from '@/router';
app.use(router);

// init localization
import { createI18n } from 'vue-i18n';
const messages = {
	"de": require("./locales/de.json"), // German
	"en": require("./locales/en.json"), // English
};
const loc = navigator.language || navigator.userLanguage;
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
import weekday from "dayjs/plugin/weekday";
import advancedFormat from 'dayjs/plugin/advancedFormat';
import localizedFormat from 'dayjs/plugin/localizedFormat';
import localeData from 'dayjs/plugin/localeData';
import duration from 'dayjs/plugin/duration';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/de';
dayjs.locale(loc);
dayjs.extend(weekday);
dayjs.extend(advancedFormat);
dayjs.extend(localizedFormat);
dayjs.extend(localeData);
dayjs.extend(duration);
dayjs.extend(relativeTime);
// provide the configured dayjs instance as well es some helper functions
app.provide('dayjs', dayjs);
const hDuration = m => {
	return (m < 60)
		? dayjs.duration(m, 'minutes').humanize()
		: dayjs.duration(m/60, 'hours').humanize();
};
app.provide('hDuration', hDuration);

// init basic css with tailwind imports
import './assets/main.css';

// ready? let's go!
app.mount('#app');
