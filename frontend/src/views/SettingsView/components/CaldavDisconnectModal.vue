<script setup lang="ts">
import { Alert } from '@/models';
import { IconButton, ModalDialog, NoticeBar, NoticeBarTypes, PrimaryButton, DangerButton } from '@thunderbirdops/services-ui';
import { PhX } from '@phosphor-icons/vue';
import { ref, useTemplateRef } from 'vue';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useI18n } from 'vue-i18n';
import { ExternalConnectionProviders } from '@/definitions';

const externalConnectionStore = useExternalConnectionsStore();
const { t } = useI18n();
const emit = defineEmits(['disconnected']);

const modal = useTemplateRef('modal');
const errorMessage = ref<Alert>(null);

const props = defineProps<{
  typeId: string|null,
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

async function disconnect() {
  await externalConnectionStore.disconnect(ExternalConnectionProviders.Caldav, props.typeId);
  externalConnectionStore.$reset();
  modal.value.hide();
  emit('disconnected');
}

defineExpose({ show, hide })
</script>

<template>
  <!-- Connect CalDAV modal -->
  <modal-dialog ref="modal" class="caldav-disconnect-modal">
    <template #header>
      {{ t('text.settings.connectedApplications.disconnect.caldav.title') }}
    </template>

    <div class="caldav-disconnect-modal-container">
      <notice-bar v-if="errorMessage" class="notice-bar" :type="NoticeBarTypes.Critical">
        {{ errorMessage.title }}
        <template #cta>
          <icon-button @click="errorMessage = null" :title="t('label.close')">
            <ph-x />
          </icon-button>
        </template>
      </notice-bar>

      {{ t('text.settings.connectedApplications.disconnect.caldav.message') }}
    </div>

    <template #actions>
      <primary-button
        name="cancel"
        variant="outline"
        @click="modal?.hide()"
        class="cancel-button"
        data-testid="caldav-disconnect-cancel-btn"
      >
        {{ t('text.settings.connectedApplications.disconnect.caldav.cancel') }}
      </primary-button>
      <danger-button
        name="disconnect"
        @click="disconnect()"
        class="disconnect-button"
        data-testid="caldav-disconnect-confirm-btn"
      >
        {{ t('text.settings.connectedApplications.disconnect.caldav.confirm') }}
      </danger-button>
    </template>
  </modal-dialog>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.caldav-connect-modal  {
  &:deep(.modal-header) {
    text-align: center;
  }

  .caldav-connect-modal-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }
}
</style>
