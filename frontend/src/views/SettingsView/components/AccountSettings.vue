<script setup lang="ts">
import { inject, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { callKey } from '@/keys';
import { DangerButton, SecondaryButton, TextInput } from '@thunderbirdops/services-ui';
import { IconCopy, IconArrowRight } from '@tabler/icons-vue';
import { createUserStore } from '@/stores/user-store';
import { BooleanResponse } from '@/models';
import { posthog, usePosthog } from '@/composables/posthog';
import { MetricEvents } from '@/definitions';
import ConfirmationModal from '@/components/ConfirmationModal.vue';

const { t } = useI18n();
const router = useRouter();

const call = inject(callKey);
const userStore = createUserStore(call);

const copyLinkTooltip = ref(t('label.copyLink'));
const cancelAccountModalOpen = ref(false);

// Link copy
const copyLink = async () => {
  await navigator.clipboard.writeText(userStore.myLink);

  copyLinkTooltip.value = t('info.copiedToClipboard');

  setTimeout(() => {
    copyLinkTooltip.value = t('label.copyLink');
  }, 2000);
};

/**
 * Request an account deletion, and then log out.
 * TODO: This will need to change for a cancellation flow
 */
const actuallyDeleteAccount = async () => {
  cancelAccountModalOpen.value = false;

  const { error }: BooleanResponse = await call('account/delete').delete();

  if (usePosthog) {
    posthog.capture(MetricEvents.DeleteAccount);
  }

  if (error.value) {
    // TODO: show error
    // console.warn('ERROR: ', error.value);
    return;
  }

  // We can't logout since we've deleted the user by now, so just delete local storage data.
  userStore.$reset();
  await router.push('/');
};
</script>

<template>
  <header>
    <h2>{{ t('heading.accountSettings') }}</h2>
  </header>

  <div class="booking-page-url-container">
    <label for="booking-page-url">
      {{ t('label.bookingPageURL') }}
    </label>
    <div class="booking-page-url-input-container">
      <text-input name="booking-page-url" class="booking-page-input" v-model="userStore.myLink" />
      <secondary-button aria-labelledby="copy-booking-page-url-button" @click="copyLink" :tooltip="copyLinkTooltip">
        <icon-copy id="copy-booking-page-url-button" :aria-label="t('label.copy')" size="18" />
      </secondary-button>
    </div>
  </div>

  <div class="booking-page-settings-container">
    <secondary-button class="booking-page-settings-button" @click="router.push({ name: 'availability' })">
      <span>
        {{ t('label.bookingPageSettings') }}
        <icon-arrow-right size="18" />
      </span>
    </secondary-button>
  </div>

  <div class="cancel-service-container">
    <span>{{ t('info.cancelServiceInfo') }}</span>
    <danger-button @click="cancelAccountModalOpen = true">
      {{ t('label.cancelService') }}
    </danger-button>
  </div>

  <!-- Account deletion modal -->
  <!-- TODO: This should be account _cancellation_ instead -->
  <confirmation-modal
    :open="cancelAccountModalOpen"
    :title="t('heading.cancelAppointmentService')"
    :message="t('text.accountCancelWarning')"
    :confirm-label="t('label.cancelService')"
    :cancel-label="t('label.cancel')"
    :use-caution-button="true"
    @confirm="actuallyDeleteAccount"
    @close="cancelAccountModalOpen = false">
  </confirmation-modal>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

header {
  margin-block-end: 2rem;
}

h2 {
  font-size: 1.5rem;
}

.booking-page-url-container {
  display: grid;
  grid-template-columns: 1fr;
  grid-gap: 1.5rem;
  align-items: center;
  margin-block-end: 1.5rem;

  .booking-page-url-input-container {
    display: flex;
    gap: 1.5rem;
  }

  .booking-page-input {
    flex-grow: 1;
  }
}

.booking-page-settings-container {
  display: flex;
  margin-block-end: 1.5rem;

  .booking-page-settings-button {
    width: 100%;

    span {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
  }
}

.cancel-service-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: end;
  gap: 2rem;
  white-space: pre-line;
  text-align: start;

  span {
    font-size: 0.825rem;
  }

  button {
    width: 100%;
  }
}

@media (--md) {
  .booking-page-url-container {
    grid-template-columns: 20% 1fr;
  }

  .booking-page-settings-container {
    justify-content: end;

    .booking-page-settings-button {
      width: auto;
    }
  }

  .cancel-service-container {
    text-align: end;
    flex-direction: row;

    button {
      width: auto;
    }
  }
}
</style>