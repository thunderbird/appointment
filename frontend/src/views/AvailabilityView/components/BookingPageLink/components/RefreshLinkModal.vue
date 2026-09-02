<script setup lang="ts">
import { ModalDialog, PrimaryButton } from '@thunderbirdops/services-ui';
import { useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();
const emit = defineEmits(['confirmed']);

defineProps<{
  loading?: boolean;
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
  <modal-dialog ref="modal" class="refresh-link-modal" :class="{ 'is-loading': loading }" :close-outside="!loading">
    <template #header>
      {{ t('label.refreshLink') }}
    </template>

    <div class="refresh-link-modal-container">
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
.refresh-link-modal.is-loading :deep(.modal-close) {
  pointer-events: none;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
