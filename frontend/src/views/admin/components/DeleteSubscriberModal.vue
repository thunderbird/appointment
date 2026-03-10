<script setup lang="ts">
import { BooleanResponse } from '@/models';
import { ModalDialog, PrimaryButton, DangerButton } from '@thunderbirdops/services-ui';
import { inject, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';

const call = inject(callKey);
const { t } = useI18n();
const emit = defineEmits(['deleted']);

const modal = useTemplateRef('modal');

const props = defineProps<{
  subscriberId?: number|null,
}>();

/**
 * Trigger the modal to show up or hide.
 */
const show = () => {
  modal.value?.show();
};
const hide = () => {
  modal.value?.hide();
};

const hardDeleteSubscriber = async () => {
  if (!props.subscriberId) {
    hide();
    return;
  }

  // Use ids here
  const response: BooleanResponse = await call(`subscriber/hard-delete/${props.subscriberId}`).put().json();
  const { data } = response;

  if (data.value) {
    emit('deleted');
  }

  hide();
};

defineExpose({ show, hide })
</script>

<template>
  <!-- Delete subscriber modal -->
  <modal-dialog ref="modal" class="delete-subscriber-modal">
    <template #header>
      {{ t('label.warning').toUpperCase() }}
    </template>

    <div class="delete-subscriber-modal-container">
      {{ t('text.admin.completelyRemoveUser') }}
    </div>

    <template #actions>
      <primary-button
        name="cancel"
        variant="outline"
        @click="modal?.hide()"
        class="cancel-button"
        data-testid="delete-subscriber-cancel-btn"
      >
        {{ t('label.cancel') }}
      </primary-button>
      <danger-button
        name="confirm"
        @click="hardDeleteSubscriber()"
        class="confirm-button"
        data-testid="delete-subscriber-confirm-btn"
      >
        {{ t('label.delete') }}
      </danger-button>
    </template>
  </modal-dialog>
</template>
