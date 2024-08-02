<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.connectedAccounts') }}</div>
    <div class="max-w-3xl pl-6" v-for="(connection, provider) in connections" v-bind:key="provider">
      <h2 class="mb-4 text-xl font-medium">{{ t(`heading.settings.connectedAccounts.${provider}`) }}</h2>
      <p>{{ t(`text.settings.connectedAccounts.connect.${provider}`) }}</p>
      <div v-if="provider === 'google'" class="pt-2">
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
          <p v-if="connection[0]">{{ t('label.connectedAs', { name: connection[0].name }) }}</p>
          <p v-if="!connection[0]">{{ t('label.notConnected') }}</p>
        </div>
        <div class="mx-auto mr-0" v-if="provider !== 'fxa'">
          <primary-button
          v-if="!connection[0]"
          :label="t('label.connect')"
          class="btn-connect"
          @click="() => connectAccount(providers[provider])"
          :title="t('label.connect')"
        />
        <caution-button
          v-if="connection[0]"
          :label="t('label.disconnect')"
          class="btn-disconnect"
          @click="() => displayModal(providers[provider])"
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
</template>

<script setup lang="ts">
import {
  ref, inject, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { callKey, fxaEditProfileUrlKey } from '@/keys';
import { ExternalConnectionProviders } from '@/definitions';
import { enumToObject } from '@/utils';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';

// stores
import { useUserStore } from '@/stores/user-store';
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useCalendarStore } from '@/stores/calendar-store';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject(callKey);
const router = useRouter();
const externalConnectionsStore = useExternalConnectionsStore();
const calendarStore = useCalendarStore();
const userStore = useUserStore();
const { connections } = storeToRefs(externalConnectionsStore);
const { $reset: resetConnections } = externalConnectionsStore;
const providers = enumToObject(ExternalConnectionProviders);

const fxaEditProfileUrl = inject(fxaEditProfileUrlKey);

const disconnectZoomModalOpen = ref(false);
const disconnectGoogleModalOpen = ref(false);

const closeModals = () => {
  disconnectZoomModalOpen.value = false;
  disconnectGoogleModalOpen.value = false;
};

const refreshData = async () => {
  // Need to reset calendar store first!
  calendarStore.$reset();
  await Promise.all([
    externalConnectionsStore.fetch(call),
    calendarStore.fetch(call),
    // Need to update userStore in case they used an attached email
    userStore.profile(call),
  ]);
};

onMounted(async () => {
  await refreshData();
});

const displayModal = async (provider: ExternalConnectionProviders) => {
  if (provider === ExternalConnectionProviders.Zoom) {
    disconnectZoomModalOpen.value = true;
  } else if (provider === ExternalConnectionProviders.Google) {
    disconnectGoogleModalOpen.value = true;
  }
};

const connectAccount = async (provider: ExternalConnectionProviders) => {
  await externalConnectionsStore.connect(call, provider, router);
};

const disconnectAccount = async (provider: ExternalConnectionProviders) => {
  await externalConnectionsStore.disconnect(call, provider);
  resetConnections();
  await refreshData();
  closeModals();
};

const editProfile = async () => {
  window.location.href = fxaEditProfileUrl;
};

</script>
