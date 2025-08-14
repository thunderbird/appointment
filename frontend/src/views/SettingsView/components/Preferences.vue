<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { isoWeekdaysKey } from '@/keys';
import { ColourSchemes } from '@/definitions';
import { BubbleSelect, SelectInput } from '@thunderbirdops/services-ui';
import RadioGroupPill from '@/components/RadioGroupPill.vue';
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
// As long as we use Qalendar, we can only support Sunday and Monday as start of week
const availableStartOfTheWeekOptions = computed(
  () => isoWeekdays.filter((day) => [7,1].includes(day.iso)).map((e) => ({
    label: e.min[0],
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
    <h2>{{ t('label.preferences') }}</h2>
  </header>

  <div class="form-field-container">
    <label for="theme">
      {{ t('label.theme') }}
    </label>
    <select-input
      name="theme"
      :options="colourSchemeOptions"
      v-model="colourScheme"
      data-testid="settings-preferences-theme-select"
    />

    <label for="language">
      {{ t('label.language') }}
    </label>
    <select-input
      name="language"
      :options="localeOptions"
      v-model="language"
      data-testid="settings-preferences-language-select"
    />

    <label for="default-time-zone">
      {{ t('label.defaultTimeZone') }}
    </label>
    <select-input
      name="default-time-zone"
      :options="timezoneOptions"
      v-model="defaultTimeZone"
      data-testid="settings-preferences-default-time-zone-select"
    />

    <label class="time-format-label" for="time-format">
      {{ t('label.timeFormat') }}
    </label>
    <radio-group-pill
      name="time-format"
      v-model="timeFormat"
      :options="timeFormatOptions"
    />

    <label for="start-of-week">
      {{ t('label.startOfWeek') }}
    </label>

    <bubble-select
      name="start-of-week"
      class="start-of-week-bubble-select"
      v-model="startOfWeek"
      single-selection
      :options="availableStartOfTheWeekOptions"
      :required="false"
    />
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.form-field-container {
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 1.5rem;
  align-items: center;

  label {
    width: 100%;
  }

  .time-format-label {
    margin-block: 0.25rem;
  }
}

.start-of-week-bubble-select {
  /* Fix for BubbleSelect component as we can't target .bubble-list */
  & > :last-child {
    justify-content: flex-start;
    gap: 0.75rem;
  }
}

@media (--md) {
  .form-field-container {
    grid-template-columns: 20% 1fr;
  }
}
</style>