<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ColourSchemes } from '@/definitions';
import { SelectInput } from '@thunderbirdops/services-ui';

const { t, availableLocales } = useI18n();

const colourSchemeOptions = Object.values(ColourSchemes).map((c) => ({
  label: t(`label.${c}`),
  value: c,
}));

const localeOptions = availableLocales.map((l) => ({
  label: `${l.toUpperCase()} — ${t(`locales.${l}`)}`,
  value: l,
}));

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
    <label class="form-field-label">
      {{ t('label.theme') }}
    </label>
    <select-input
      name="theme"
      :options="localeOptions"
      data-testid="settings-preferences-theme-select"
    />
  </div>

  <div class="form-field-container">
    <label class="form-field-label">
      {{ t('label.language') }}
    </label>
    <select-input
      name="theme"
      :options="colourSchemeOptions"
      data-testid="settings-preferences-language-select"
    />
  </div>
</template>

<style scoped>
header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.form-field-container {
  display: flex;
  align-items: center;
  gap: 15rem;
  margin-block-end: 1.5rem;

  .form-field-label {
    width: 25%;
  }

  & :last-child {
    width: 75%;
  }
}
</style>