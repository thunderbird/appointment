<script setup lang="ts">
import {
  computed, inject, onMounted, ref,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import GenericModal from '@/components/GenericModal.vue';
import CalDavProvider from '@/components/FTUE/CalDavProvider.vue';
import {
  callKey, fxaEditProfileUrlKey, isAccountsAuthKey, isFxaAuthKey,
} from '@/keys';
import { ExternalConnectionProviders } from '@/definitions';
import { enumToObject } from '@/utils';

// stores
import { createUserStore } from '@/stores/user-store';
import { createExternalConnectionsStore } from '@/stores/external-connections-store';
import { createCalendarStore } from '@/stores/calendar-store';

import { Alert } from '@/models';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const router = useRouter();
const externalConnectionsStore = createExternalConnectionsStore(call);
const calendarStore = createCalendarStore(call);
const userStore = createUserStore(call);
const { connections } = storeToRefs(externalConnectionsStore);
const { $reset: resetConnections } = externalConnectionsStore;
const providers = enumToObject(ExternalConnectionProviders);
const isFxaAuth = inject(isFxaAuthKey);
const isAccountsAuth = inject(isAccountsAuthKey);
/*
 * Temp until we remove local fxa
 */
const filteredConnections = computed(() => {
  const newConnections = {};
  const keys = Object.keys(connections.value);
  // eslint-disable-next-line no-restricted-syntax
  for (const connection of keys) {
    if (connection === 'fxa' && !isFxaAuth) {
      // eslint-disable-next-line no-continue
      continue;
    }
    if (connection === 'accounts' && !isAccountsAuth) {
      // eslint-disable-next-line no-continue
      continue;
    }
    newConnections[connection] = connections.value[connection];
  }
  return newConnections;
});

const fxaEditProfileUrl = inject(fxaEditProfileUrlKey);

const connectCalDavModalOpen = ref(false);
const disconnectCalDavModalOpen = ref(false);
const disconnectZoomModalOpen = ref(false);
const disconnectGoogleModalOpen = ref(false);
const disconnectTypeId = ref(null);

const calDavErrorMessage = ref();

const closeModals = () => {
  connectCalDavModalOpen.value = false;
  disconnectZoomModalOpen.value = false;
  disconnectGoogleModalOpen.value = false;
  disconnectCalDavModalOpen.value = false;
  disconnectTypeId.value = null;
};

const refreshData = async () => {
  // Need to reset calendar store first!
  calendarStore.$reset();
  await Promise.all([
    externalConnectionsStore.fetch(true),
    calendarStore.fetch(),
    // Need to update userStore in case they used an attached email
    userStore.profile(),
  ]);
};

onMounted(async () => {
  await refreshData();
});

const displayModal = async (provider: ExternalConnectionProviders, typeId: string | null = null) => {
  disconnectTypeId.value = typeId;

  if (provider === ExternalConnectionProviders.Zoom) {
    disconnectZoomModalOpen.value = true;
  } else if (provider === ExternalConnectionProviders.Google) {
    disconnectGoogleModalOpen.value = true;
  } else if (provider === ExternalConnectionProviders.Caldav) {
    disconnectCalDavModalOpen.value = true;
  }
};

const connectAccount = async (provider: ExternalConnectionProviders) => {
  if (provider === ExternalConnectionProviders.Caldav) {
    connectCalDavModalOpen.value = true;
    return;
  }
  await externalConnectionsStore.connect(provider, router);
};

const connectCalDAV = async () => {
  await refreshData();
  closeModals();
};

const disconnectAccount = async (provider: ExternalConnectionProviders, typeId: string | null = null) => {
  await externalConnectionsStore.disconnect(provider, typeId);
  resetConnections();
  await refreshData();
  closeModals();
};

const editProfile = async () => {
  window.location.href = fxaEditProfileUrl;
};

</script>

<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.connectedAccountsSettings') }}</div>
    <div class="max-w-3xl pl-6" v-for="(connection, provider) in filteredConnections" v-bind:key="provider">
      <h2 class="mb-4 text-xl font-medium">{{ t(`heading.settings.connectedAccounts.${provider}`) }}</h2>
      <p>{{ t(`text.settings.connectedAccounts.connect.${provider}`) }}</p>
      <div v-if="providers[provider] === ExternalConnectionProviders.Google" class="pt-2">
        <p>
          <i18n-t
            :keypath="`text.settings.connectedAccounts.connect.${provider}Legal.text`"
            tag="label"
            :for="`text.settings.connectedAccounts.connect.${provider}Legal.link`"
          >
            <a
              class="underline"
              href="https://developers.google.com/terms/api-services-user-data-policy"
              target="_blank"
            >
              {{ t(`text.settings.connectedAccounts.connect.${provider}Legal.link`) }}
            </a>
          </i18n-t>
        </p>
      </div>
      <div class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-md">
          <p v-if="connection[0]">{{ t('label.connectedAs', {name: connection[0].name}) }}</p>
          <p v-if="!connection[0]">{{ t('label.notConnected') }}</p>
        </div>
        <div class="mx-auto mr-0" v-if="providers[provider] !== ExternalConnectionProviders.Fxa && providers[provider] !== ExternalConnectionProviders.accounts">
          <primary-button
          v-if="!connection[0]"
          :label="t('label.connect')"
          class="btn-connect"
          :data-testid="'connected-accounts-settings-' + t(provider) + '-connect-btn'"
          @click="() => connectAccount(providers[provider])"
          :title="t('label.connect')"
        />
        <caution-button
          v-if="connection[0]"
          :label="t('label.disconnect')"
          class="btn-disconnect"
          :data-testid="'connected-accounts-settings-' + t(provider) + '-disconnect-btn'"
          @click="() => displayModal(providers[provider], connection[0].type_id)"
          :title="t('label.disconnect')"
        />
        </div>
        <div class="mx-auto mr-0" v-else>
          <secondary-button
            :label="t('label.editProfile')"
            class="btn-edit"
            @click="editProfile"
            :title="t('label.edit')"
          />
        </div>
      </div>
    </div>
  </div>
  <!-- Disconnect Google Modal -->
  <confirmation-modal
    :open="disconnectGoogleModalOpen"
    :title="t('text.settings.connectedAccounts.disconnect.google.title')"
    :message="t('text.settings.connectedAccounts.disconnect.google.message')"
    :confirm-label="t('text.settings.connectedAccounts.disconnect.google.confirm')"
    :cancel-label="t('text.settings.connectedAccounts.disconnect.google.cancel')"
    :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Google)"
    @close="closeModals"
  ></confirmation-modal>
  <!-- Disconnect CalDav Modal -->
  <confirmation-modal
    :open="disconnectCalDavModalOpen"
    :title="t('text.settings.connectedAccounts.disconnect.caldav.title')"
    :message="t('text.settings.connectedAccounts.disconnect.caldav.message')"
    :confirm-label="t('text.settings.connectedAccounts.disconnect.caldav.confirm')"
    :cancel-label="t('text.settings.connectedAccounts.disconnect.caldav.cancel')"
    :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Caldav, disconnectTypeId)"
    @close="closeModals"
  ></confirmation-modal>
  <!-- Disconnect Zoom Modal -->
  <confirmation-modal
    :open="disconnectZoomModalOpen"
    :title="t('text.settings.connectedAccounts.disconnect.zoom.title')"
    :message="t('text.settings.connectedAccounts.disconnect.zoom.message')"
    :confirm-label="t('text.settings.connectedAccounts.disconnect.zoom.confirm')"
    :cancel-label="t('text.settings.connectedAccounts.disconnect.zoom.cancel')"
    :use-caution-button="true"
    @confirm="() => disconnectAccount(ExternalConnectionProviders.Zoom)"
    @close="closeModals"
  ></confirmation-modal>
  <!-- Bit of a hack until we figure out this ux flow -->
  <generic-modal v-if="connectCalDavModalOpen" @close="closeModals()" :error-message="calDavErrorMessage">
    <template v-slot:header>
      <h2 class="modal-title">
        {{ t('heading.settings.connectedAccounts.caldav') }}
      </h2>
    </template>
    <cal-dav-provider @next="connectCalDAV()" @error="(alert: Alert) => calDavErrorMessage = alert"></cal-dav-provider>
  </generic-modal>
</template>
<style scoped>
.modal-title {
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-weight: 400;
  font-size: 1.375rem;
  line-height: 1.664rem;
}
</style>
