<script setup lang="ts">
import { Alert } from '@/models';
import { IconButton, ModalDialog, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import { PhX } from '@phosphor-icons/vue';
import { ref, useTemplateRef } from 'vue';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useI18n } from 'vue-i18n';
import CalDavProvider from '@/components/CalDavProvider.vue';

const externalConnectionStore = useExternalConnectionsStore();
const { t } = useI18n();
const emit = defineEmits(['connected']);

const modal = useTemplateRef('modal');
const errorMessage = ref<Alert>(null);

/**
 * Trigger the modal to show up or hide.
 */
const show = () => {
  modal.value?.show();
};
const hide = () => {
  modal.value?.hide();
};

async function afterCalDavConnect() {
  modal.value.hide();
  externalConnectionStore.$reset();
  emit('connected');
}

defineExpose({ show, hide })
</script>

<template>
  <!-- Connect CalDAV modal -->
  <modal-dialog ref="modal" class="caldav-connect-modal">
    <template #header>
      {{ t('heading.settings.connectedApplications.caldav') }}
    </template>

    <div class="caldav-connect-modal-container">
      <notice-bar v-if="errorMessage" class="notice-bar" :type="NoticeBarTypes.Critical">
        {{ errorMessage.title }}
        <template #cta>
          <icon-button @click="errorMessage = null" :title="t('label.close')">
            <ph-x />
          </icon-button>
        </template>
      </notice-bar>
      <cal-dav-provider @next="afterCalDavConnect()" @error="(alert: Alert) => errorMessage = alert" />
    </div>
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
