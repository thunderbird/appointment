<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.connectedAccounts') }}</div>
    <div class="max-w-3xl pl-6" v-for="(connection, category) in connections" v-bind:key="category">
      <h2 class="mb-4 text-xl font-medium">{{ t(`heading.settings.connectedAccounts.${category}`) }}</h2>
      <p>{{ t(`text.settings.connectedAccounts.connect.${category}`) }}</p>
      <div v-if="category === 'google'" class="pt-2">
        <p>
          <i18n-t
            :keypath="`text.settings.connectedAccounts.connect.${category}Legal.text`"
            tag="label"
            :for="`text.settings.connectedAccounts.connect.${category}Legal.link`"
          >
          <a
            class="underline"
            href="https://developers.google.com/terms/api-services-user-data-policy"
            target="_blank"
          >
            {{ t(`text.settings.connectedAccounts.connect.${category}Legal.link`) }}
          </a>
          </i18n-t>
        </p>
      </div>
      <div class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-md">
          <p v-if="connection[0]">{{ t('label.connectedAs', { name: connection[0].name }) }}</p>
          <p v-if="!connection[0]">{{ t('label.notConnected') }}</p>
        </div>
        <div class="mx-auto mr-0" v-if="category !== 'fxa'">
          <primary-button
          v-if="!connection[0]"
          :label="t('label.connect')"
          @click="() => connectAccount(category)"
        />
        <caution-button
          v-if="connection[0]"
          :label="t('label.disconnect')"
          @click="() => displayModal(category)"
        />
        </div>
        <div class="mx-auto mr-0" v-else>
          <secondary-button
          :label="t('label.editProfile')"
          @click="editProfile"
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
      @confirm="() => disconnectAccount('google')"
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
      @confirm="() => disconnectAccount('zoom')"
      @close="closeModals"
  ></confirmation-modal>
</template>

<script setup>
import {
  ref, inject, onMounted, computed,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import { storeToRefs } from 'pinia';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import TextButton from '@/elements/TextButton.vue';

// icons
import { IconExternalLink } from '@tabler/icons-vue';

// stores
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import { useCalendarStore } from '@/stores/calendar-store';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject('call');
const router = useRouter();
const externalConnectionsStore = useExternalConnectionsStore();
const calendarStore = useCalendarStore();
const { connections } = storeToRefs(externalConnectionsStore);
const { $reset: resetConnections } = externalConnectionsStore;

const fxaEditProfileUrl = inject('fxaEditProfileUrl');

const disconnectZoomModalOpen = ref(false);
const disconnectGoogleModalOpen = ref(false);

const closeModals = () => {
  disconnectZoomModalOpen.value = false;
  disconnectGoogleModalOpen.value = false;
};

const refreshData = async () => {
  // Need to reset calendar store first!
  await calendarStore.$reset();
  await Promise.all([
    externalConnectionsStore.fetch(call),
    calendarStore.fetch(call),
  ]);
};

onMounted(async () => {
  await refreshData();
});

const displayModal = async (category) => {
  if (category === 'zoom') {
    disconnectZoomModalOpen.value = true;
  } else if (category === 'google') {
    disconnectGoogleModalOpen.value = true;
  }
};

const connectAccount = async (category) => {
  if (category === 'zoom') {
    const { data } = await call('zoom/auth').get().json();
    // Ship them to the auth link
    window.location.href = data.value.url;
  } else if (category === 'google') {
    await router.push('/settings/calendar');
  }
};

const disconnectAccount = async (category) => {
  if (category === 'zoom') {
    await call('zoom/disconnect').post();
  } else if (category === 'google') {
    await call('google/disconnect').post();
  }

  await resetConnections();
  await refreshData();
  await closeModals();
};

const editProfile = async () => {
  window.location = fxaEditProfileUrl;
};

</script>
