<script setup lang="ts">
import {
  ModalDialog,
  PrimaryButton,
  DangerButton,
  IconButton,
  NoticeBar,
  NoticeBarTypes,
} from '@thunderbirdops/services-ui';
import { PhX } from '@phosphor-icons/vue';
import { useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const emit = defineEmits(['confirmed', 'dismiss-error']);

defineProps<{
  loading?: boolean;
  errorMessage?: string;
}>();

const modal = useTemplateRef('modal');

/**
 * Trigger the modal to show up or hide.
 */
const show = () => {
  modal.value?.show();
};
const hide = () => {
  modal.value?.hide();
};

defineExpose({ show, hide });
</script>

<template>
  <!-- Booking cancellation modal -->
  <modal-dialog ref="modal" class="booking-cancel-modal" :class="{ 'is-loading': loading }" :close-outside="!loading">
    <template #header>
      {{ t('label.cancelBooking') }}
    </template>

    <div class="booking-cancel-modal-container">
      <notice-bar v-if="errorMessage" class="notice-bar" :type="NoticeBarTypes.Critical">
        {{ errorMessage }}
        <template #cta>
          <icon-button @click="emit('dismiss-error')" :title="t('label.close')">
            <ph-x />
          </icon-button>
        </template>
      </notice-bar>

      {{ t('text.cancelBookingNotice') }}
    </div>

    <template #actions>
      <primary-button
        name="back"
        outline
        :disabled="loading"
        @click="modal?.hide()"
        data-testid="booking-cancel-back-btn"
      >
        {{ t('label.back') }}
      </primary-button>
      <danger-button
        name="confirm"
        :disabled="loading"
        @click="emit('confirmed')"
        data-testid="booking-cancel-confirm-btn"
      >
        {{ loading ? t('label.loading') : t('label.cancelBooking') }}
      </danger-button>
    </template>
  </modal-dialog>
</template>

<style scoped>
.booking-cancel-modal-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.booking-cancel-modal.is-loading :deep(.modal-close) {
  pointer-events: none;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
