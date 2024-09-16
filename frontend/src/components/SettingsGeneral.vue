<script setup lang="ts">
import { ColorSchemes } from '@/definitions';
import {
  ref, reactive, inject, watch,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useUserStore } from '@/stores/user-store';
import { dayjsKey, callKey } from '@/keys';
import { SubscriberResponse } from '@/models';

// component constants
const user = useUserStore();
const { t, locale, availableLocales } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const dj = inject(dayjsKey);

// handle ui languages
// TODO: move to settings store
watch(locale, (newValue) => {
  localStorage?.setItem('locale', newValue);
  window.location.reload();
});

// handle theme mode
// TODO: move to settings store
const initialTheme = localStorage?.getItem('theme')
  ? localStorage.getItem('theme')
  : ColorSchemes.System;
const theme = ref(initialTheme);
watch(theme, (newValue) => {
  switch (newValue) {
    case ColorSchemes.Dark:
      localStorage?.setItem('theme', 'dark');
      document.documentElement.classList.add('dark');
      break;
    case ColorSchemes.Light:
      localStorage?.setItem('theme', 'light');
      document.documentElement.classList.remove('dark');
      break;
    case ColorSchemes.System:
      localStorage?.removeItem('theme');
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

// handle time format
// TODO: move to settings store
const detectedTimeFormat = Number(dj('2022-05-24 20:00:00').format('LT').split(':')[0]) > 12 ? '24' : '12';
const initialTimeFormat = localStorage?.getItem('timeFormat') ?? detectedTimeFormat;
const timeFormat = ref(initialTimeFormat);
watch(timeFormat, (newValue) => {
  localStorage?.setItem('timeFormat', newValue);
});

// timezones
const activeTimezone = reactive({
  primary: user.data.timezone ?? dj.tz.guess(),
  secondary: dj.tz.guess(),
});
// @ts-ignore
// See https://github.com/microsoft/TypeScript/issues/49231
const timezones = Intl.supportedValuesOf('timeZone');

// save timezone config
const updateTimezone = async () => {
  const obj = {
    username: user.data.username,
    timezone: activeTimezone.primary,
  };
  const { error }: SubscriberResponse = await call('me').put(obj).json();
  if (!error.value) {
    // update user in store
    user.data.timezone = activeTimezone.primary;
    // TODO show some confirmation
  }
};
</script>

<template>
<div class="flex flex-col gap-8">
  <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.generalSettings') }}</div>
  <div class="pl-6">
    <div class="text-xl">{{ t('heading.languageAndAppearance') }}</div>
    <div class="mt-6 pl-6">
      <div class="text-lg">{{ t('label.language') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.language') }}</div>
        <select v-model="locale" class="w-full max-w-sm rounded-md">
          <option v-for="l in availableLocales" :key="l" :value="l">
            {{ l.toUpperCase() + ' &mdash; ' + t('locales.' + l) }}
          </option>
        </select>
      </label>
    </div>
    <div class="mt-6 pl-6">
      <div class="text-lg">{{ t('label.appearance') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.theme') }}</div>
        <select v-model="theme" class="w-full max-w-sm rounded-md">
          <option v-for="value in Object.values(ColorSchemes)" :key="value" :value="value">
            {{ t('label.' + value) }}
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
    <div class="mt-6 inline-grid grid-cols-2 gap-x-16 gap-y-8 pl-6">
      <div class="text-lg">{{ t('label.timeFormat') }}</div>
      <div class="text-lg"><!--{{ t('label.dateFormat') }}--></div>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <input type="radio" name="timeFormat" :value="12" v-model="timeFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.12hAmPm') }}</div>
      </label>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <!-- <input type="radio" name="dateFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.DDMMYYYY') }}</div> -->
      </label>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <input type="radio" name="timeFormat" :value="24" v-model="timeFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.24h') }}</div>
      </label>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <!-- <input type="radio" name="dateFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.MMDDYYYY') }}</div> -->
      </label>
    </div>
    <div class="mt-6 pl-6">
      <div class="text-lg">{{ t('label.timeZone') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.primaryTimeZone') }}</div>
        <select
          v-model="activeTimezone.primary"
          class="w-full max-w-sm rounded-md"
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
