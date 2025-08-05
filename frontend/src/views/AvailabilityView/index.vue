<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { callKey } from '@/keys';
import { LinkButton, PrimaryButton } from '@thunderbirdops/services-ui';
import { createAvailabilityStore } from '@/stores/availability-store';

import AvailabilitySettings from './components/AvailabilitySettings/index.vue';
import BookingPageDetails from './components/BookingPageDetails/index.vue';
import BookingPageLink from './components/BookingPageLink/index.vue';

const { t } = useI18n();
const call = inject(callKey);

const availabilityStore = createAvailabilityStore(call);
const { isDirty } = storeToRefs(availabilityStore)

const onSaveChanges = async () => {
  await availabilityStore.saveChanges();
}

const onRevertChanges = () => {
  availabilityStore.revertChanges();
}
</script>

<script lang="ts">
export default {
  name: 'AvailabilityView'
}
</script>

<template>
  <h1 class="page-title">{{ t('label.availability') }}</h1>
  <form @submit.prevent>
    <div class="page-content">
      <section>
        <availability-settings />
      </section>
  
      <div class="page-content-right">
        <section>
          <booking-page-details />
        </section>
  
        <section>
          <booking-page-link />
        </section>
      </div>
    </div>

    <div class="footer-save-panel" v-if="isDirty">
      <link-button
        @click="onRevertChanges"
      >
        {{ t('label.revertChanges') }}
      </link-button>
      <primary-button
        @click="onSaveChanges"
      >
        {{ t('label.saveChanges') }}
      </primary-button>
    </div>
  </form>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-title {
  margin-block-end: 2rem;
  font-size: 1.5rem;
}

.page-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-block-end: 2rem;
}

.page-content-right {
  display: grid;
  gap: 2rem;
  align-self: start;
}

.footer-save-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  gap: 2rem;
  margin-inline-start: auto;
  padding: 1rem 1.5rem;
  margin: 0 0.5rem 0.5rem 0.5rem;
  border-radius: 8px;
  background-color: var(--colour-neutral-lower);
  z-index: 99;
}

section {
  border: 1px solid var(--colour-neutral-border);
  border-radius: 8px;
  padding: 1.5rem;
  align-self: flex-start;
}

@media (--md) {
  .page-content {
    grid-template-columns: 1fr 1fr;
  }
}
</style>