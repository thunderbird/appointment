<template>
  <div class="flex flex-col gap-8">
    <div class="text-3xl font-thin text-gray-500 dark:text-gray-200">{{ t('heading.accountSettings') }}</div>
    <div class="flex max-w-3xl flex-col pl-6">
      <div class="text-xl">{{ t('heading.profile') }}</div>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.username') }}</div>
        <div class="w-full">
          <input
            v-model="activeUsername"
            type="text"
            class="w-full rounded-md"
            :class="{ '!border-red-500': errorUsername }"
          />
          <div v-if="errorUsername" class="text-sm text-red-500">
            {{ t('error.usernameIsNotAvailable') }}
          </div>
        </div>
      </label>
      <label class="tooltip-label mt-4 flex items-center pl-4">
        <div class="flex w-full max-w-2xs gap-2">{{ t('label.preferredEmail') }}
          <span class="relative cursor-help" role="tooltip" aria-labelledby="preferred-email-help-tooltip">
          <icon-info-circle class="tooltip-icon w-4" aria-hidden="true"/>
            <span class="tooltip hidden">
              <transition>
                  <tool-tip id="preferred-email-help-tooltip" class="tooltip left-[-8.5rem]  w-72" :content="t('text.preferredEmailHelp')"/>
              </transition>
            </span>
        </span>
        </div>
        <select v-model="activePreferredEmail" class="w-full rounded-md">
          <option v-for="email in availableEmails" :key="email" :value="email">{{ email }}</option>
        </select>
      </label>
      <label class="mt-4 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.displayName') }}</div>
        <input
          v-model="activeDisplayName"
          type="text"
          class="w-full rounded-md"
        />
      </label>
      <label class="mt-6 flex items-center pl-4">
        <div class="w-full max-w-2xs">{{ t('label.myLink') }}</div>
        <div class="flex w-full items-center justify-between gap-4">
          <div class="relative w-full">
            <input
              :value="user.myLink"
              type="text"
              class="mr-2 w-full rounded-md pr-7"
              readonly
            />
            <a
              :href="user.myLink"
              target="_blank"
              class="absolute right-1.5 top-1/2 -translate-y-1/2 text-gray-500"
            >
              <icon-external-link class="size-5"/>
            </a>
          </div>
          <text-button
            uid="myLink"
            class="btn-copy"
            :tooltip="t('label.copyLink')"
            :copy="user.myLink"
            :title="t('label.copy')"
          />
        </div>
      </label>
      <div class="mt-6 flex gap-4 self-end">
        <secondary-button
          :label="t('label.refreshLink')"
          class="btn-refresh !text-teal-500"
          @click="refreshLink"
          :title="t('label.refresh')"
        />
        <secondary-button
          :label="t('label.saveChanges')"
          class="btn-save !text-teal-500"
          @click="updateUserCheckForConfirmation"
          :title="t('label.save')"
        />
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountData') }}</div>
      <div class="mt-4 pl-4">
        <primary-button
          :label="t('label.downloadYourData')"
          class="btn-download"
          @click="downloadData"
          :title="t('label.download')"
        />
      </div>
    </div>
    <div class="pl-6">
      <div class="text-xl">{{ t('heading.accountDeletion') }}</div>
      <div class="mt-4 pl-4">
        <caution-button
          :label="t('label.deleteYourAccount')"
          class="btn-delete"
          @click="deleteAccount"
          :title="t('label.delete')"
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
import {
  ref, inject, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user-store';
import CautionButton from '@/elements/CautionButton.vue';
import ConfirmationModal from '@/components/ConfirmationModal.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import SecondaryButton from '@/elements/SecondaryButton.vue';
import TextButton from '@/elements/TextButton.vue';

// icons
import { IconExternalLink, IconInfoCircle } from '@tabler/icons-vue';

// stores
import { useExternalConnectionsStore } from '@/stores/external-connections-store';
import ToolTip from '@/elements/ToolTip.vue';
import { useScheduleStore } from '@/stores/schedule-store';

import { MetricEvents } from '@/definitions';
import { usePosthog, posthog } from '@/composables/posthog';

// component constants
const { t } = useI18n({ useScope: 'global' });
const call = inject('call');
const router = useRouter();
const user = useUserStore();
const schedule = useScheduleStore();
const externalConnectionsStore = useExternalConnectionsStore();

const activeUsername = ref(user.data.username);
const activeDisplayName = ref(user.data.name);
const downloadAccountModalOpen = ref(false);
const deleteAccountFirstModalOpen = ref(false);
const deleteAccountSecondModalOpen = ref(false);
const refreshLinkModalOpen = ref(false);
const updateUsernameModalOpen = ref(false);
const availableEmails = ref([user.data.preferredEmail]);
const activePreferredEmail = ref(user.data.preferredEmail);

const closeModals = () => {
  downloadAccountModalOpen.value = false;
  deleteAccountFirstModalOpen.value = false;
  deleteAccountSecondModalOpen.value = false;
  refreshLinkModalOpen.value = false;
  updateUsernameModalOpen.value = false;
};

const getAvailableEmails = async () => {
  const { data } = await call('account/available-emails').get().json();
  if (!data || !data.value) {
    availableEmails.value = [];
  }

  availableEmails.value = data.value;
};

const refreshData = async () => Promise.all([
  user.profile(call),
  schedule.fetch(call, true),
  externalConnectionsStore.fetch(call),
  getAvailableEmails(),
]);

// save user data
const errorUsername = ref(false);
const updateUser = async () => {
  const inputData = {
    username: activeUsername.value,
    name: activeDisplayName.value,
    secondary_email: activePreferredEmail.value,
  };
  const { data, error } = await call('me').put(inputData).json();
  if (!error.value) {
    // update user in store
    user.updateProfile(data.value);
    await user.updateSignedUrl(call);
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

/**
 * Send off some metrics
 * @param event {MetricEvents}
 * @param properties {Object}
 */
const sendMetrics = (event, properties = {}) => {
  if (usePosthog) {
    posthog.capture(event, properties);
  }
};

const downloadData = async () => {
  downloadAccountModalOpen.value = true;
};

const deleteAccount = async () => {
  deleteAccountFirstModalOpen.value = true;
};

const refreshLink = async () => {
  refreshLinkModalOpen.value = true;
};

const refreshLinkConfirm = async () => {
  await user.changeSignedUrl(call);
  await refreshData();
  closeModals();

  sendMetrics(MetricEvents.RefreshLink);
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
  sendMetrics(MetricEvents.DownloadData);
};

/**
 * Request an account deletion, and then log out.
 * @returns {Promise<void>}
 */
const actuallyDeleteAccount = async () => {
  deleteAccountSecondModalOpen.value = false;

  const { error } = await call('account/delete').delete();

  sendMetrics(MetricEvents.DeleteAccount);

  if (error.value) {
    // TODO: show error
    // console.warn('ERROR: ', error.value);
    return;
  }

  // We can't logout since we've deleted the user by now, so just delete local storage data.
  await user.$reset();
  await router.push('/');
};

</script>
<style scoped>

/* If the device does not support hover (i.e. mobile) then make it activate on focus within */
@media (hover: none) {
  .tooltip-label:focus-within .tooltip {
    display: block;
  }
}

.tooltip-icon:hover ~ .tooltip {
  display: block;
}

</style>
