<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
    <div class="pl-6 flex flex-col max-w-3xl">
      <div class="text-xl">{{ t('heading.profile') }}</div>
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
        <div class="w-full">
          <input
            v-model="activeUsername"
            type="text"
            class="w-full rounded-md"
            :class="{ '!border-red-500': errorUsername }"
          />
          <div v-if="errorUsername" class="text-red-500 text-sm">
            {{ t('error.usernameIsNotAvailable')}}
          </div>
        </div>
      </label>
      <label class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.displayName') }}</div>
        <input
          v-model="activeDisplayName"
          type="text"
          class="w-full rounded-md"
        />
      </label>
      <label class="pl-4 mt-6 flex items-center">
        <div class="w-full max-w-2xs">{{ t('label.myLink') }}</div>
        <div class="w-full flex justify-between items-center gap-4">
          <div class="relative w-full">
            <input
              v-model="signedUserUrl"
              type="text"
              class="w-full rounded-md mr-2 pr-7"
              readonly
            />
            <a :href="signedUserUrl" target="_blank" class="text-gray-500 absolute right-1.5 top-1/2 -translate-y-1/2">
              <icon-external-link class="w-5 h-5" />
            </a>
          </div>
          <text-button :label="t('label.copyLink')" :copy="signedUserUrl" />
        </div>
      </label>
      <div class="self-end flex gap-4 mt-6">
        <secondary-button
            :label="t('label.refreshLink')"
            class="!text-teal-500"
            @click="refreshLink"
        />
        <secondary-button
            :label="t('label.saveChanges')"
            class="!text-teal-500"
            @click="updateUserCheckForConfirmation"
        />
      </div>
    </div>
    <div class="pl-6 max-w-3xl">
      <div class="text-xl mb-4">{{ t('heading.zoom') }}</div>
      <div>
        <p>{{ t('text.connectZoom') }}</p>
      </div>
      <div class="pl-4 mt-4 flex items-center">
        <div class="w-full max-w-2xs">
          <p v-if="hasZoomAccountConnected">{{ t('label.connectedAs', { name: zoomAccountName }) }}</p>
          <p v-if="!hasZoomAccountConnected">{{ t('label.notConnected') }}</p>
        </div>
        <div class="mx-auto mr-0">
          <primary-button
          v-if="!hasZoomAccountConnected"
          :label="t('label.connect')"
          @click="connectZoom"
        />
        <caution-button
          v-if="hasZoomAccountConnected"
          :label="t('label.disconnect')"
          @click="disconnectZoom"
        />
        </div>
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountData') }}</div>
      <div class="pl-4 mt-4">
        <primary-button
          :label="t('label.downloadYourData')"
          @click="downloadData"
        />
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountDeletion') }}</div>
      <div class="pl-4 mt-4">
        <caution-button
          :label="t('label.deleteYourAccount')"
          @click="deleteAccount"
        />
      </div>
    </div>
  </div>
  <!-- Refresh link confirmation modal -->
    <ConfirmationModal
      :open="refreshLinkModalOpen"
      :title="t('label.refreshLink')"
      :message="t('text.refreshLinkNotice')"
      :confirm-label="t('label.refresh')"
      :cancel-label="t('label.cancel')"
      @confirm="() => refreshLinkConfirm()"
      @close="closeModals"
  ></ConfirmationModal>
  <!-- Update username confirmation modal -->
    <ConfirmationModal
      :open="updateUsernameModalOpen"
      :title="t('label.updateUsername')"
      :message="t('text.updateUsernameNotice')"
      :confirm-label="t('label.saveChanges')"
      :cancel-label="t('label.cancel')"
      @confirm="() => updateUser()"
      @close="closeModals"
  ></ConfirmationModal>
  <!-- Account download modal -->
    <ConfirmationModal
      :open="downloadAccountModalOpen"
      :title="t('label.accountData')"
      :message="t('text.accountDataNotice')"
      :confirm-label="t('label.continue')"
      :cancel-label="t('label.cancel')"
      @confirm="actuallyDownloadData"
      @close="closeModals"
  ></ConfirmationModal>
  <!-- Account deletion modals -->
  <ConfirmationModal
      :open="deleteAccountFirstModalOpen"
      :title="t('label.deleteYourAccount')"
      :message="t('text.accountDeletionWarning')"
      :confirm-label="t('label.deleteYourAccount')"
      :cancel-label="t('label.cancel')"
      :use-caution-button="true"
      @confirm="actuallyDeleteAccount"
      @close="closeModals"
  ></ConfirmationModal>
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import TextButton from '@/elements/TextButton.vue';

// icons
import { IconExternalLink } from '@tabler/icons-vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject('call');
const refresh = inject('refresh');
const router = useRouter();
const user = useUserStore();
const logout = inject('logout');

const externalConnections = ref({});
const hasZoomAccountConnected = computed(() => (externalConnections.value?.zoom?.length ?? []) > 0);
const zoomAccountName = computed(() => (externalConnections.value?.zoom[0].name ?? null));

const activeUsername = ref(user.data.username);
const activeDisplayName = ref(user.data.name);
const downloadAccountModalOpen = ref(false);
const deleteAccountFirstModalOpen = ref(false);
const deleteAccountSecondModalOpen = ref(false);
const refreshLinkModalOpen = ref(false);
const updateUsernameModalOpen = ref(false);

// calculate signed link
const signedUserUrl = ref('');

const closeModals = () => {
  downloadAccountModalOpen.value = false;
  deleteAccountFirstModalOpen.value = false;
  deleteAccountSecondModalOpen.value = false;
  refreshLinkModalOpen.value = false;
  updateUsernameModalOpen.value = false;
};

const getSignedUserUrl = async () => {
  // Retrieve the user short url
  const { data, error } = await call('me/signature').get().json();
  if (error.value) {
    return;
  }

  signedUserUrl.value = data.value.url;
};

const getExternalConnections = async () => {
  const { data } = await call('account/external-connections').get().json();
  externalConnections.value = data.value;
};

const refreshData = async () => Promise.all([
  getSignedUserUrl(),
  getExternalConnections(),
  refresh(),
]);

// save user data
const errorUsername = ref(false);
const updateUser = async () => {
  const inputData = {
    username: activeUsername.value,
    name: activeDisplayName.value,
  };
  const { error } = await call('me').put(inputData).json();
  if (!error.value) {
    // update user in store
    user.$patch({ data: { ...user.data, ...inputData }});
    errorUsername.value = false;
    // TODO show some confirmation
    await refreshData();
  } else {
    errorUsername.value = true;
  }

  closeModals();
};

/**
 * Check if the username has been changed, and open a modal to warn the user their short link is going to change
 * If it didn't change, then just update the user immediately.
 */
const updateUserCheckForConfirmation = async () => {
  if (activeUsername.value !== user.data.username) {
    updateUsernameModalOpen.value = true;
    return;
  }

  await updateUser();
};

onMounted(async () => {
  await refreshData();
});

const connectZoom = async () => {
  const { data } = await call('zoom/auth').get().json();
  // Ship them to the auth link
  window.location.href = data.value.url;
};
const disconnectZoom = async () => {
  await call('zoom/disconnect').post();
  await refreshData();
};

const downloadData = async () => {
  downloadAccountModalOpen.value = true;
};

const deleteAccount = async () => {
  deleteAccountFirstModalOpen.value = true;
};

const secondDeleteAccountPrompt = async () => {
  deleteAccountFirstModalOpen.value = false;
  deleteAccountSecondModalOpen.value = true;
};

const refreshLink = async () => {
  refreshLinkModalOpen.value = true;
};

const refreshLinkConfirm = async () => {
  const { data, error } = await call('me/signature').post().json();

  if (error.value) {
    console.log('Error!', data.value);
  }

  await refreshData();
  closeModals();
};

/**
 * Generic function to run the user through the login screen again
 * @param callbackFn
 * @returns {Promise<void>}
 */
const reauthenticateSubscriber = async (callbackFn) => {
  // Currently not supported
  await callbackFn();
};

/**
 * Request a data download, and prompt the user to download the data.
 * @returns {Promise<void>}
 */
const actuallyDownloadData = async () => {
  const { data } = await call('account/download').get().blob();
  if (!data || !data.value) {
    // TODO: show error
    // console.error('Failed to download blob!!');
    return;
  }
  // Data is a ref to our new blob
  const fileObj = window.URL.createObjectURL(data.value);
  window.location.assign(fileObj);

  closeModals();
};

/**
 * Request an account deletion, and then log out.
 * @returns {Promise<void>}
 */
const actuallyDeleteAccount = async () => {
  deleteAccountSecondModalOpen.value = false;

  const { error } = await call('account/delete').delete();

  if (error.value) {
    // TODO: show error
    // console.warn('ERROR: ', error.value);
    return;
  }

  await router.push('/');
};

</script>
