<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhLinkSimple, PhClockUser, PhPencil } from '@phosphor-icons/vue';
import { useUserStore } from '@/stores/user-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import AsideNavButton from '@/components/AsideNavButton.vue';

const { t } = useI18n();
const user = useUserStore();
const appointmentStore = useAppointmentStore();

const copyBookingLinkLabel = ref(t('label.copyBookingLink'));
const hasCopied = ref(false);
const pendingAppointmentsCount = ref<number>();

const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  copyBookingLinkLabel.value = t('info.copiedToClipboard');
  hasCopied.value = true

  setTimeout(() => {
    copyBookingLinkLabel.value = t('label.copyBookingLink');
    hasCopied.value = false
  }, 2000);
};

onMounted(async () => {
  const { data, error } = await appointmentStore.fetchPendingAppointmentsCount();

  if (!error.value) {
    pendingAppointmentsCount.value = data.value.count;
  }
})
</script>

<template>
  <aside>
    <aside-nav-button
      v-if="pendingAppointmentsCount"
      :label="t('label.pendingRequests', pendingAppointmentsCount)"
      :to="{
        name: 'bookings',
        query: { unconfirmed: 'true' }
      }"
      test-id="link-pending-requests"
    >
      <template #icon>
        <span class="count-badge">{{ pendingAppointmentsCount }}</span>
      </template>
    </aside-nav-button>

    <h2
      :class="{ 'has-pending-requests': pendingAppointmentsCount }"
    >
      {{ t('label.whatDoYouWantToDoToday') }}
    </h2>

    <div class="quick-actions-container">
      <aside-nav-button
        :label="copyBookingLinkLabel"
        :show-arrow="false"
        test-id="button-copy-booking-url"
        @click="copyLink"
      >
        <template #icon>
          <ph-link-simple class="icon-left" :size="24" />
        </template>
      </aside-nav-button>

      <aside-nav-button
        :label="t('label.changeMyAvailability')"
        to="availability"
        test-id="link-change-availability"
        :show-arrow="true"
      >
        <template #icon>
          <ph-clock-user class="icon-left" :size="24" />
        </template>
      </aside-nav-button>

      <aside-nav-button
        :label="t('label.modifyMyBookings')"
        to="bookings"
        test-id="link-modify-booking-page"
        :show-arrow="true"
      >
        <template #icon>
          <ph-pencil class="icon-left" :size="24" />
        </template>
      </aside-nav-button>
    </div>
  </aside>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

h2 {
  font-size: 1rem;
  font-weight: 600;
  margin-block-end: 1.5rem;
  color: var(--colour-ti-black);

  &.has-pending-requests {
    margin-block-start: 3rem;
  }
}

.quick-actions-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #A0C7F0; /* TODO: pending final colour / not yet in colours.css */
  color: #1a202c;
  border-radius: 9999px;
  width: 1.5rem;
  height: 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

@media (--md) {
  aside {
    min-width: 268px;
    padding-inline-start: 0.25rem;
    padding-block-start: 0.25rem;
  }
}
</style>