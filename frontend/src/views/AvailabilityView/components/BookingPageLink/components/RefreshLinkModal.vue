<script setup lang="ts">
import { ModalDialog, PrimaryButton, IconButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
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
  <!-- Refresh link modal -->
  <modal-dialog
    ref="modal"
    class="refresh-link-modal"
    :class="{ 'is-loading': loading }"
    :close-outside="!loading"
  >
    <template #header>
      {{ t('label.refreshLink') }}
    </template>

    <div class="refresh-link-modal-container">
      <notice-bar v-if="errorMessage" class="notice-bar" :type="NoticeBarTypes.Critical">
        {{ errorMessage }}
        <template #cta>
          <icon-button @click="emit('dismiss-error')" :title="t('label.close')">
            <ph-x />
          </icon-button>
        </template>
      </notice-bar>

      {{ t('text.refreshLinkNotice') }}
    </div>

    <template #actions>
      <primary-button
        name="cancel"
        variant="outline"
        :disabled="loading"
        @click="modal?.hide()"
        class="cancel-button"
        data-testid="refresh-link-cancel-btn"
      >
        {{ t('label.cancel') }}
      </primary-button>
      <primary-button
        name="confirm"
        :disabled="loading"
        @click="emit('confirmed')"
        class="confirm-button"
        data-testid="refresh-link-confirm-btn"
      >
        {{ loading ? t('label.loading') : t('label.confirm') }}
      </primary-button>
    </template>
  </modal-dialog>
</template>

<style scoped>
.refresh-link-modal-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.refresh-link-modal.is-loading :deep(.modal-close) {
  pointer-events: none;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
