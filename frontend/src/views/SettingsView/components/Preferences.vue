<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { isoWeekdaysKey } from '@/keys';
import { ColourSchemes } from '@/definitions';
import { BubbleSelect, SegmentedControl, SelectInput } from '@thunderbirdops/services-ui';
import { useSettingsStore } from '@/stores/settings-store';
import { storeToRefs } from 'pinia';

const { t, availableLocales } = useI18n();
const isoWeekdays = inject(isoWeekdaysKey);

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
// TODO: As long as we use Qalendar, we can only support Sunday and Monday as start of week
const availableStartOfTheWeekOptions = computed(
  () => isoWeekdays.filter((day) => [7,1].includes(day.iso)).map((e) => ({
    label: e.short,
    value: e.iso,
  }))
);

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
