// init localization
import { createI18n } from 'vue-i18n';

// language source files
import de from '@/locales/de.json';
import en from '@/locales/en.json';

const messages = {
  de, // German
  en, // English
};
const loc = localStorage?.getItem('locale') ?? navigator.language;
const instance = createI18n({
  legacy: false,
  globalInjection: true,
  locale: loc,
  fallbackLocale: 'en',
  messages,
});

export default instance;
export const i18n = instance.global;
