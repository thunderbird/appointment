<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { PhLinkSimple, PhClockUser, PhPencil, PhArrowRight } from '@phosphor-icons/vue';
import { useUserStore } from '@/stores/user-store';
import { useAppointmentStore } from '@/stores/appointment-store';

const { t } = useI18n();
const user = useUserStore();
const appointmentStore = useAppointmentStore();

const copyBookingUrlLabel = ref(t('label.copyBookingUrl'));
const hasCopied = ref(false);
const pendingAppointmentsCount = ref<number>();

const copyLink = async () => {
  await navigator.clipboard.writeText(user.myLink);

  copyBookingUrlLabel.value = t('info.copiedToClipboard');
  hasCopied.value = true

  setTimeout(() => {
    copyBookingUrlLabel.value = t('label.copyBookingUrl');
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
    <router-link v-if="pendingAppointmentsCount" data-testid="link-pending-requests" class="link-button"
      :to="{
        name: 'bookings',
        query: {
          unconfirmed: 'true'
        }
      }">
      <span class="count-badge">{{ pendingAppointmentsCount }}</span>
      {{ t('label.pendingRequests', pendingAppointmentsCount) }}
    </router-link>

    <h2
      :class="{ 'has-pending-requests': pendingAppointmentsCount }"
    >
      {{ t('label.whatDoYouWantToDoToday') }}
    </h2>

    <div class="quick-actions-container">
      <button class="link-button with-icon" :class="{ 'copied': hasCopied }" @click="copyLink" data-testid="button-copy-booking-url">
        <ph-link-simple class="icon-left" :size="24" />
        {{ copyBookingUrlLabel }}
      </button>
      <router-link class="link-button with-icon with-right-icon" to="availability" data-testid="link-change-availability">
        <ph-clock-user class="icon-left" :size="24" />
        {{ t('label.changeMyAvailability') }}
        <ph-arrow-right class="icon-right" :size="16" />
      </router-link>
      <router-link class="link-button with-icon with-right-icon" to="bookings" data-testid="link-modify-booking-page">
        <ph-pencil class="icon-left" :size="24" />
        {{ t('label.modifyMyBookings') }}
        <ph-arrow-right class="icon-right" :size="16" />
      </router-link>
    </div>
  </aside>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

h2 {
  font-size: 1rem;
  font-weight: 600;
  margin-block-end: 1.5rem;

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
  margin-right: 0.5rem;
}

.link-button {
  display: block;
  position: relative;
  cursor: pointer;
  padding: 0.75rem 1rem;
  background-color: var(--colour-neutral-lower);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  text-align: left;
  text-transform: capitalize;

  .icon-left {
    color: var(--colour-ti-highlight);
  }

  &.with-icon {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  &.with-right-icon {
    gap: 0;
  }

  &.copied {
    background-color: var(--colour-neutral-lower);

    &:hover {
      text-decoration-line: none;
      background-color: var(--colour-neutral-raised);
    }
  }

  &:hover {
    text-decoration-line: underline;
    background-color: var(--colour-primary-soft);
  }
}

.with-right-icon .icon-left {
  margin-right: 0.5rem;
}

.with-right-icon .icon-right {
  margin-left: auto;
}

.dark .link-button {
  background-color: var(--colour-neutral-raised);

  &:hover {
    text-decoration-line: underline;
    background-color: var(--colour-neutral-base);
  }
}

@media (--md) {
  aside {
    min-width: 268px;
  }
}
</style>