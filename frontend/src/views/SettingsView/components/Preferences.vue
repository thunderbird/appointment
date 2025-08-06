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
    <label class="form-field-label" for="theme">
      {{ t('label.theme') }}
    </label>
    <select-input
      name="theme"
      :options="localeOptions"
      data-testid="settings-preferences-theme-select"
    />
  </div>

  <div class="form-field-container">
    <label class="form-field-label" for="language">
      {{ t('label.language') }}
    </label>
    <select-input
      name="language"
      :options="colourSchemeOptions"
      data-testid="settings-preferences-language-select"
    />
  </div>

  <div class="form-field-container">
    <label class="form-field-label time-format" for="time-format">
      {{ t('label.timeFormat') }}
    </label>
    <radio-group-pill
      name="time-format"
      :options="timezoneOptions"
    />
  </div>

  <div class="form-field-container">
    <label class="form-field-label" for="time-format">
      {{ t('label.startOfWeek') }}
    </label>
    
    <bubble-select
      name="time-format"
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
  display: flex;
  flex-direction: column;
  align-items: start;
  gap: 0.75rem;
  margin-block-end: 1.5rem;

  label {
    width: 100%;
  }

  .form-field-label.time-format {
    margin-block: 0.25rem;
  }
}

@media (--md) {
  .form-field-container {
    flex-direction: row;
    align-items: center;
    gap: 15rem;

    .form-field-label {
      width: 25%;
    }

    .form-field-label {
      width: 25%;
    }

    /* The actual input, not the label */
    & > :last-child {
      width: 75%;
    }

    /* The last form-field-container */
    &:last-child {
      margin-block-end: 0;
    }
  }
}
</style>