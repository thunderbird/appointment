<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl text-gray-500 font-semibold">{{ t('heading.accountSettings') }}</div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountData') }}</div>
      <div class="pl-6 mt-6">
        <primary-button
            :label="t('label.downloadYourData')"
            class="text-sm"
            @click="downloadData"
        />
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountDeletion') }}</div>
      <div class="pl-6 mt-6">
        <caution-button
            :label="t('label.deleteYourAccount')"
            class="text-sm"
            @click="deleteAccount"
        />
      </div>
    </div>
  </div>
  <!-- Account download modal -->
    <ConfirmationModal
      :open="downloadAccountModalOpen"
      :title="t('label.accountData')"
      :message="t('text.accountDataNotice')"
      :confirm-label="t('label.loginToContinue')"
      :cancel-label="t('label.cancel')"
      @confirm="() => reauthenticateSubscriber(actuallyDownloadData)"
      @close="closeModals"
  ></ConfirmationModal>
  <!-- Account deletion modals -->
  <ConfirmationModal
      :open="deleteAccountFirstModalOpen"
      :title="t('label.deleteYourAccount')"
      :message="t('text.accountDeletionWarning')"
      :confirm-label="t('label.loginToContinue')"
      :cancel-label="t('label.cancel')"
      @confirm="() => reauthenticateSubscriber(secondDeleteAccountPrompt)"
      @close="closeModals"
  ></ConfirmationModal>
  <ConfirmationModal
      :open="deleteAccountSecondModalOpen"
      :title="t('label.deleteYourAccount')"
      :message="t('text.accountDeletionFinalWarning')"
      :confirm-label="t('label.deleteYourAccount')"
      :cancel-label="t('label.cancel')"
      @confirm="actuallyDeleteAccount"
      @close="closeModals"
  ></ConfirmationModal>
</template>

<script setup>
import {
  ref, inject, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth0 } from '@auth0/auth0-vue';
import { useRouter } from 'vue-router';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import CautionButton from '@/elements/CautionButton.vue';

// component constants
const { t } = useI18n({ useScope: 'global' });
const refresh = inject('refresh');
const call = inject('call');
const router = useRouter();
const auth0 = useAuth0();

const downloadAccountModalOpen = ref(false);
const deleteAccountFirstModalOpen = ref(false);
const deleteAccountSecondModalOpen = ref(false);

onMounted(async () => {
  await refresh();
});

const downloadData = async () => {
  downloadAccountModalOpen.value = true;
};

const closeModals = () => {
  downloadAccountModalOpen.value = false;
  deleteAccountFirstModalOpen.value = false;
  deleteAccountSecondModalOpen.value = false;
};

const deleteAccount = async () => {
  deleteAccountFirstModalOpen.value = true;
};

const secondDeleteAccountPrompt = async () => {
  deleteAccountFirstModalOpen.value = false;
  deleteAccountSecondModalOpen.value = true;
};

/**
 * Generic function to run the user through the login screen again
 * @param callbackFn
 * @returns {Promise<void>}
 */
const reauthenticateSubscriber = async (callbackFn) => {
  try {
    // Prompt the user to re-login
    await auth0.loginWithPopup({
      authorizationParams: {
        prompt: 'login',
      },
    }, {});
  } catch (e) {
    // TODO: Throw an error
    console.log('Reauth failed', e);
    closeModals();
    return;
  }

  await callbackFn();
};

/**
 * Request a data download, and prompt the user to download the data.
 * @returns {Promise<void>}
 */
const actuallyDownloadData = async () => {
  const { data } = await call('account/download').get().blob();
  if (!data || !data.value) {
    console.error('Failed to download blob!!');
    return;
  }
  // Data is a ref to our new blob
  const fileObj = window.URL.createObjectURL(data.value);
  window.location.assign(fileObj);

  await closeModals();
};

/**
 * Request an account deletion, and then log out.
 * @returns {Promise<void>}
 */
const actuallyDeleteAccount = async () => {
  deleteAccountSecondModalOpen.value = false;

  const { error } = await call('account/delete').delete();

  if (error.value) {
    console.warn('ERROR: ', error.value);
    return;
  }

  if (auth0) {
    await auth0.logout({
      logoutParams: {
        returnTo: window.location.origin,
      },
    });
  } else {
    await router.push('/');
  }
};

</script>
