<template>
<div class="flex flex-col gap-8">
  <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.generalSettings') }}</div>
  <div class="pl-6">
    <div class="text-xl">{{ t('heading.languageAndAppearance') }}</div>
    <div class="pl-6 mt-6">
      <div class="text-lg">{{ t('label.language') }}</div>
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.language') }}</div>
        <select v-model="locale" class="w-full max-w-sm rounded-md w-full">
          <option v-for="l in availableLocales" :key="l" :value="l">
            {{ l.toUpperCase() + ' &mdash; ' + t('locales.' + l) }}
          </option>
        </select>
      </label>
    </div>
    <div class="pl-6 mt-6">
      <div class="text-lg">{{ t('label.appearance') }}</div>
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.theme') }}</div>
        <select v-model="theme" class="w-full max-w-sm rounded-md w-full">
          <option v-for="(key, label) in colorSchemes" :key="key" :value="key">
            {{ t('label.' + label) }}
          </option>
        </select>
      </label>
      <!-- <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.defaultFont') }}</div>
        <select class="w-full max-w-sm rounded-md w-full">
          <option value="os">Open Sans</option>
          <option value="fs">Fira Sans</option>
        </select>
      </label> -->
    </div>
  </div>
  <div class="pl-6">
    <div class="text-xl">{{ t('heading.dateAndTimeFormatting') }}</div>
    <div class="pl-6 mt-6 inline-grid grid-cols-2 gap-y-8 gap-x-16">
      <div class="text-lg">{{ t('label.timeFormat') }}</div>
      <div class="text-lg">{{ t('label.dateFormat') }}</div>
      <label class="pl-4 flex gap-4 items-center cursor-pointer">
        <input type="radio" name="timeFormat" :value="12" v-model="timeFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.12hAmPm') }}</div>
      </label>
      <label class="pl-4 flex gap-4 items-center cursor-pointer">
        <input type="radio" name="dateFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.DDMMYYYY') }}</div>
      </label>
      <label class="pl-4 flex gap-4 items-center cursor-pointer">
        <input type="radio" name="timeFormat" :value="24" v-model="timeFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.24h') }}</div>
      </label>
      <label class="pl-4 flex gap-4 items-center cursor-pointer">
        <input type="radio" name="dateFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.MMDDYYYY') }}</div>
      </label>
    </div>
    <div class="pl-6 mt-6">
      <div class="text-lg">{{ t('label.timeZone') }}</div>
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.primaryTimeZone') }}</div>
        <select
          v-model="activeTimezone.primary"
          class="w-full max-w-sm rounded-md w-full"
          @change="updateTimezone"
        >
          <option v-for="tz in timezones" :key="tz" :value="tz">
            {{ tz }}
          </option>
        </select>
      </label>
      <!-- <label class="pl-4 mt-6 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.showSecondaryTimeZone') }}</div>
        <switch-toggle :active="false" />
      </label>
      <label class="pl-4 mt-6 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.secondaryTimeZone') }}</div>
        <select v-model="activeTimezone.secondary" class="w-full max-w-sm rounded-md w-full">
          <option v-for="tz in timezones" :key="tz" :value="tz">
            {{ tz }}
          </option>
        </select>
      </label> -->
    </div>
  </div>
</div>
</template>

<script setup>
import { colorSchemes } from '@/definitions';
import {
  ref, reactive, inject, watch,
} from 'vue';
import { useI18n } from 'vue-i18n';
import SwitchToggle from '@/elements/SwitchToggle';

// component constants
const { t, locale, availableLocales } = useI18n({ useScope: 'global' });
const call = inject('call');
const dj = inject('dayjs');

// view properties
const props = defineProps({
  user: Object, // currently logged in user, null if not logged in
});

// handle ui languages
watch(locale, (newValue) => {
  localStorage.locale = newValue;
});

// handle theme mode
const initialTheme = !('theme' in localStorage) ? colorSchemes.system : colorSchemes[localStorage.theme];
const theme = ref(initialTheme);
watch(theme, (newValue) => {
  switch (newValue) {
    case colorSchemes.dark:
      localStorage.theme = 'dark';
      document.documentElement.classList.add('dark');
      break;
    case colorSchemes.light:
      localStorage.theme = 'light';
      document.documentElement.classList.remove('dark');
      break;
    case colorSchemes.system:
      localStorage.removeItem('theme');
      if (!window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.remove('dark');
      } else {
        document.documentElement.classList.add('dark');
      }
      break;
    default:
      break;
  }
});

// handle theme mode
const initialTimeFormat = ('timeFormat' in localStorage) ? localStorage.timeFormat : 24;
const timeFormat = ref(initialTimeFormat);
watch(timeFormat, (newValue) => {
  console.log(newValue);
  localStorage.timeFormat = newValue;
});

// timezones
const activeTimezone = reactive({
  primary: props.user?.timezone ?? dj.tz.guess(),
  secondary: dj.tz.guess(),
});
const timezones = Intl.supportedValuesOf('timeZone');
// load user defined timezone on page reload
watch(
  () => props.user,
  (loadedUser) => {
    activeTimezone.primary = loadedUser.timezone;
  },
);

// save timezone config
const updateTimezone = async () => {
  const { error } = await call('me').put({ timezone: activeTimezone.primary }).json();
  if (!error) {
    // TODO show some confirmation
  }
};
</script>
