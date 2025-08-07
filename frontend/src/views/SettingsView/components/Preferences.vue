<script setup lang="ts">
import { computed, inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { isoWeekdaysKey } from '@/keys';
import { ColourSchemes } from '@/definitions';
import { BubbleSelect, SelectInput } from '@thunderbirdops/services-ui';
import RadioGroupPill from '@/components/RadioGroupPill.vue';

const { t, availableLocales } = useI18n();
const isoWeekdays = inject(isoWeekdaysKey);

const colourSchemeOptions = computed(() => Object.values(ColourSchemes).map((c) => ({
  label: t(`label.${c}`),
  value: c,
})));

const localeOptions = computed(() => availableLocales.map((l) => ({
  label: `${l.toUpperCase()} — ${t(`locales.${l}`)}`,
  value: l,
})));

const timezoneOptions = computed(() => [{
  label: '12:00 am/pm',
  value: 12
}, {
  label: '24:00',
  value: 24
}])

// As long as we use Qalendar, we can only support Sunday and Monday as start of week
const availableStartOfTheWeekOptions = computed(
  () => isoWeekdays.filter((day) => [7,1].includes(day.iso)).map((e) => ({
    label: e.min[0],
    value: e.iso,
  }))
);
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
      data-testid="settings-preferences-theme-select"
    />

    <label for="language">
      {{ t('label.language') }}
    </label>
    <select-input
      name="language"
      :options="localeOptions"
      data-testid="settings-preferences-language-select"
    />

    <label class="time-format-label" for="time-format">
      {{ t('label.timeFormat') }}
    </label>
    <radio-group-pill
      name="time-format"
      :options="timezoneOptions"
    />

    <label for="start-of-week">
      {{ t('label.startOfWeek') }}
    </label>
    <bubble-select
      name="start-of-week"
      class="start-of-week-bubble-select"
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
  grid-template-columns: 20% 1fr;
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
</style>