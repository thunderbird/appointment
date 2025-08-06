<script setup lang="ts">
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
</script>

<template>
  <header>
    <h2>{{ t('label.connectedApplications') }}</h2>
  </header>

  <div class="form-field-container">
    <label class="form-field-label" for="videoMeeting">
      {{ t('label.videoMeeting') }}
    </label>

    <div>
      
    </div>
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

  /* The actual input, not the label */
  & > :last-child {
    width: 75%;
  }

  /* The last form-field-container */
  &:last-child {
    margin-block-end: 0;
  }
}
</style>