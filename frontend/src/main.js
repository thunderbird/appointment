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
dayjs.locale(loc);
app.provide('dayjs', dayjs);

// init basic css with tailwind imports
import './assets/main.css';

// ready? let's go!
app.mount('#app');
