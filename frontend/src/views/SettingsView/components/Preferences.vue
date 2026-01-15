<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { ColourSchemes } from '@/definitions';
import { BubbleSelect, SegmentedControl, SelectInput } from '@thunderbirdops/services-ui';
import { useSettingsStore } from '@/stores/settings-store';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';

const { t, availableLocales } = useI18n();
const dj = inject(dayjsKey);
const userStore = useUserStore();

const settingsStore = useSettingsStore();
const { currentState } = storeToRefs(settingsStore);

// Theme / Colour Scheme
const colourSchemeOptions = computed(() => Object.values(ColourSchemes).map((c) => ({
  label: t(`label.${c}`),
  value: c,
})));

const colourScheme = computed({
  get: () => currentState.value.colourScheme,
  set: (value) => {
    settingsStore.$patch({ currentState: { colourScheme: value }})
  }
})

// Language / Locale
const localeOptions = computed(() => availableLocales.map((l) => ({
  label: `${l.toUpperCase()} — ${t(`locales.${l}`)}`,
  value: l,
})));

const language = computed({
  get: () => currentState.value.language,
  set: (value) => {
    settingsStore.$patch({ currentState: { language: value }})
  }
})

// Default Time Zone
// @ts-expect-error ignore type err
// See https://github.com/microsoft/TypeScript/issues/49231
const timezoneOptions = Intl.supportedValuesOf('timeZone').map((timezone: string) => ({
  label: timezone.replaceAll('_', ' '),
  value: timezone,
}));

const defaultTimeZone = computed({
  get: () => currentState.value.defaultTimeZone,
  set: (value) => {
    settingsStore.$patch({ currentState: { defaultTimeZone: value }})
  }
})

// Time Format
const timeFormatOptions = computed(() => [{
  label: t('label.12hAmPm'),
  value: 12
}, {
  label: t('label.24h'),
  value: 24
}])

const timeFormat = computed({
  get: () => currentState.value.timeFormat,
  set: (value) => {
    settingsStore.$patch({ currentState: { timeFormat: value }})
  }
})

// Start of Week
// Generate options dynamically using dayjs to respect current locale
const availableStartOfTheWeekOptions = computed(() => {
  // Access language to trigger recomputation when locale changes
  void userStore.data.settings.language;

  // ISO weekday values: 1=Monday, 2=Tuesday, ..., 7=Sunday
  // dayjs weekday values: 0=Sunday, 1=Monday, ..., 6=Saturday
  const allDays = [
    { iso: 7, dayjsDay: 0 }, // Sunday
    { iso: 1, dayjsDay: 1 }, // Monday
    { iso: 2, dayjsDay: 2 }, // Tuesday
    { iso: 3, dayjsDay: 3 }, // Wednesday
    { iso: 4, dayjsDay: 4 }, // Thursday
    { iso: 5, dayjsDay: 5 }, // Friday
    { iso: 6, dayjsDay: 6 }, // Saturday
  ];

  return allDays.map((day) => ({
    label: dj().day(day.dayjsDay).format('ddd'),
    value: day.iso,
  }));
});

const startOfWeek = computed({
  get: () => {
    return [currentState.value.startOfWeek]
  },
  set: (value) => {
    settingsStore.$patch({ currentState: { startOfWeek: value[0] }})
  }
})
</script>

<script lang="ts">
export default {
  name: 'SettingsViewPreferences'
}
</script>

<template>
  <header>
    <h2>{{ t('heading.preferences') }}</h2>
  </header>

  <div class="form-field-container">
    <select-input
      name="theme"
      :options="colourSchemeOptions"
      v-model="colourScheme"
      data-testid="settings-preferences-theme-select"
    >
      {{ t('label.theme') }}
    </select-input>

    <select-input
      name="language"
      :options="localeOptions"
      v-model="language"
      data-testid="settings-preferences-language-select"
    >
      {{ t('label.language') }}
    </select-input>

    <select-input
      name="default-time-zone"
      :options="timezoneOptions"
      v-model="defaultTimeZone"
      data-testid="settings-preferences-default-time-zone-select"
    >
      {{ t('label.defaultTimeZone') }}
    </select-input>

    <segmented-control
      name="time-format"
      v-model="timeFormat"
      :options="timeFormatOptions"
    >
      {{ t('label.timeFormat') }}
    </segmented-control>

    <bubble-select
      name="start-of-week"
      class="start-of-week-bubble-select"
      v-model="startOfWeek"
      single-selection
      :options="availableStartOfTheWeekOptions"
      :required="false"
    >
      {{ t('label.startOfWeek') }}
    </bubble-select>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 1.5rem;
}

h2 {
  color: var(--colour-ti-highlight);
  font-size: 1.5rem;
  font-family: metropolis;
}

.form-field-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.start-of-week-bubble-select {
  /* Fix for BubbleSelect component as we can't target .bubble-list */
  & > :last-child {
    justify-content: flex-start;
    gap: 0.75rem;
  }
}
</style>
