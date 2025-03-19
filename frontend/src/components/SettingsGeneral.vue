<script setup lang="ts">
import { ColourSchemes } from '@/definitions';
import { inject, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { createUserStore } from '@/stores/user-store';
import { callKey } from '@/keys';

// component constants
const { t, locale, availableLocales } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const user = createUserStore(call);

// handle ui languages
watch(locale, (newValue: string) => {
  user.data.settings.language = newValue;
  // This is needs a window.location.reload(); to reload locale for dayjs instance
});

// handle theme mode
watch(() => user.data.settings.colourScheme, (newValue) => {
  switch (newValue) {
    case ColourSchemes.Dark:
      document.documentElement.classList.add('dark');
      break;
    case ColourSchemes.Light:
      document.documentElement.classList.remove('dark');
      break;
    case ColourSchemes.System:
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

// Make sure settings are saved directly when changed
watch(
  () => [
    user.data.settings.language,
    user.data.settings.timezone,
    user.data.settings.colourScheme,
    user.data.settings.timeFormat,
  ],
  () => {
    if (user.authenticated) {
      user.updateSettings();
    }
  },
);

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezones = Intl.supportedValuesOf('timeZone');

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
        <select v-model="locale" class="w-full max-w-sm rounded-md" data-testid="settings-general-locale-select">
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
        <select v-model="user.data.settings.colourScheme" class="w-full max-w-sm rounded-md" data-testid="settings-general-theme-select">
          <option v-for="value in Object.values(ColourSchemes)" :key="value" :value="value">
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
        <input type="radio" name="timeFormat" :value="12" v-model="user.data.settings.timeFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.12hAmPm') }}</div>
      </label>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <!-- <input type="radio" name="dateFormat" class="text-teal-500" />
        <div class="w-full max-w-2xs">{{ t('label.DDMMYYYY') }}</div> -->
      </label>
      <label class="flex cursor-pointer items-center gap-4 pl-4">
        <input type="radio" name="timeFormat" :value="24" v-model="user.data.settings.timeFormat" class="text-teal-500" />
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
          v-model="user.data.settings.timezone"
          class="w-full max-w-sm rounded-md"
          data-testid="settings-general-timezone-select"
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
