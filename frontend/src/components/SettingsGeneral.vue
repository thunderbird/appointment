<script setup lang="ts">
import { ColourSchemes } from '@/definitions';
import { inject, watch, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { createUserStore } from '@/stores/user-store';
import { callKey, isoWeekdaysKey } from '@/keys';
import SelectInput from '@/tbpro/elements/SelectInput.vue';

// component constants
const { t, locale, availableLocales } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const user = createUserStore(call);
const isoWeekdays = inject(isoWeekdaysKey);

const localeOptions = availableLocales.map((l) => ({
  label: l.toUpperCase() + ' — ' + t('locales.' + l),
  value: l,
}));

const colourSchemeOptions = Object.values(ColourSchemes).map((c) => ({
  label: t('label.' + c),
  value: c,
}));

// As long as we use Qalendar, we can only support Sunday and Monday as start of week
const availableStartOfTheWeekOptions = computed(
  () => isoWeekdays.filter((day) => [7,1].includes(day.iso)).map((e) => ({
    label: e.long,
    value: e.iso,
  }))
);

// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

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
    user.data.settings.startOfWeek,
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
        <select-input
          name="timezone"
          :options="localeOptions"
          v-model="locale"
          class="w-full max-w-sm"
          data-testid="settings-general-locale-select"
        />
      </label>
    </div>
    <div class="mt-6 pl-6">
      <div class="text-lg">{{ t('label.appearance') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.theme') }}</div>
        <select-input
          name="timezone"
          :options="colourSchemeOptions"
          v-model="user.data.settings.colourScheme"
          class="w-full max-w-sm"
          data-testid="settings-general-theme-select"
        />
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
    <div class="mt-6 pl-6">
      <div class="text-lg">{{ t('label.startOfTheWeek') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.startOfTheWeek') }}</div>
        <select-input
          name="timezone"
          :options="availableStartOfTheWeekOptions"
          v-model="user.data.settings.startOfWeek"
          class="w-full max-w-sm"
          data-testid="settings-general-start-of-week-select"
        />
      </label>
    </div>
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
        <select-input
          name="timezone"
          :options="timezoneOptions"
          v-model="user.data.settings.timezone"
          class="w-full max-w-sm"
          data-testid="settings-general-timezone-select"
        />
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
