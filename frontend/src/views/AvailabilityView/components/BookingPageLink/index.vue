<script setup lang="ts">
import { TextInput } from '@thunderbirdops/services-ui';
import { useI18n } from 'vue-i18n';
import { IconCopy } from '@tabler/icons-vue';

const { t } = useI18n();
</script>

<script lang="ts">
export default {
  name: 'BookingPageLink'
}
</script>

<template>
  <header>
    <h2>Booking Page Link</h2>
  </header>

  <text-input
    name="customizeLink"
    class="customize-link-input"
    outer-prefix="apmt.day/username"
  >
    {{ t('label.customizeYourLink') }}:
  </text-input>

  <!-- Share your link -->
  <div>
    <h3>Share your link:</h3>
    <div class="share-link-container">
      <p>apmt.day/username/1c544cb3</p>
      <button>
        <icon-copy size="12" />
        Copy
      </button>
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

h3 {
  font-size: 0.8125rem;
  font-weight: bold;
  margin-block-end: 0.5rem;
}

.customize-link-input {
  margin-block-end: 1rem;
}

.share-link-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.25rem;
  border: 1px solid var(--colour-neutral-border);
  border-radius: 4px;
  font-size: 0.75rem;

  button {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    background-color: var(--colour-apmt-primary);
    color: var(--colour-neutral-base);
    font-size: 0.75rem;
    border-radius: 4px;

    &:hover {
      background-color: var(--colour-apmt-primary-hover);
    }

    &:active {
      background-color: var(--colour-apmt-primary-pressed);
    }
  }
}
</style>