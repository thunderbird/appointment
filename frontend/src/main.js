// init app
import { createApp } from 'vue';
import App from './App.vue';
const app = createApp(App);

// init router
import router from './router';
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
import 'dayjs/locale/de';
dayjs.locale(loc);
dayjs.extend(weekday);
dayjs.extend(advancedFormat);
dayjs.extend(localizedFormat);
dayjs.extend(localeData)
app.provide('dayjs', dayjs);

// init basic css with tailwind imports
import './assets/main.css';

// ready? let's go!
app.mount('#app');
