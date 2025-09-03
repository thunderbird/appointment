<script setup lang="ts">
import { computed, inject, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import {
  IconWorld,
  IconCalendarClock,
  IconCalendar,
  IconClock,
  IconCircleCheckFilled,
  IconMapPin
} from '@tabler/icons-vue';
import { PrimaryButton } from '@thunderbirdops/services-ui';
import { dayjsKey, callKey } from '@/keys';
import { SlotResponse } from '@/models';
import { usePosthog, posthog } from '@/composables/posthog';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { useUserStore } from '@/stores/user-store';
import { BookingCalendarView, MetricEvents, AlertSchemes } from '@/definitions';
import SlotSelectionUserInfo from './SlotSelectionUserInfo.vue';
import AlertBox from '@/elements/AlertBox.vue';

const { t } = useI18n();

const dj = inject(dayjsKey);
const call = inject(callKey);

const userStore = useUserStore();
const {
  appointment,
  selectedEvent,
  guestUserInfo,
  guestUserInfoValid,
  attendee,
  activeView
} = storeToRefs(useBookingViewStore());

const bookingRequestLoading = ref<boolean>(false);
const bookingRequestError = ref<string>('');

const timezone = computed(() => dj.tz.guess());
const selectedSlotDate = computed(() => dj(selectedEvent.value?.start).format('LL'))
const selectedSlotTimeDuration = computed(() => {
  const startTime = dj(selectedEvent.value?.start).format('LT');
  const endTime = dj(selectedEvent.value?.start)
    .add(selectedEvent.value?.slot_duration, 'minutes')
    .format('LT');

  return `${startTime} ${t('label.to')} ${endTime}`;
})

/**
 * Book or request to book a selected time.
 */
const bookEvent = async () => {
  bookingRequestLoading.value = true;
  bookingRequestError.value = '';

  const attendeeData = userStore.authenticated ? {
    id: userStore.data.id,
    email: userStore.data.email,
    name: userStore.data.name,
    timezone: userStore.data.settings.timezone,
  } : {
    email: guestUserInfo.value.email,
    name: guestUserInfo.value.name,
    timezone: timezone.value,
  }

  const obj = {
    slot: {
      start: selectedEvent.value.start,
      duration: selectedEvent.value.duration,
    },
    attendee: attendeeData,
  };

  const url = window.location.href.split('#')[0];
  const request: SlotResponse = call('schedule/public/availability/request').put({
    s_a: obj,
    url,
  });

  // Data should just be true here.
  const { data, error } = await request.json();

  bookingRequestLoading.value = false;

  if (error.value || !data.value) {
    bookingRequestError.value = data?.value?.detail?.message ?? t('error.unknownAppointmentError');
    return;
  }

  bookingRequestError.value = '';

  // replace calendar view if every thing worked fine
  attendee.value = attendeeData;
  // update view to prevent reselection
  activeView.value = BookingCalendarView.Success;

  if (usePosthog) {
    // Not chained because it's the inverse of booking_confirmation, and it defaults to false.
    const autoConfirmed = appointment && appointment.value.booking_confirmation !== undefined
      ? !appointment.value.booking_confirmation : false;
    posthog.capture(MetricEvents.RequestBooking, {
      autoConfirmed,
    });
  }
};
</script>

<template>
  <aside>
    <p class="invitation-text" data-testid="booking-view-inviting-you-text">
      {{ t('text.nameIsInvitingYou', { name: appointment.owner_name }) }}
    </p>
    <h1 class="appointment-title" data-testid="booking-view-title-text">
      {{ appointment.title }}
    </h1>
    <p v-if="appointment.details" class="appointment-details">
      {{ appointment.details }}
    </p>
    <div class="timezone-section">
      <span class="timezone-label">{{ t('label.timeZone') }}:</span>
      <div class="timezone-display">
        <icon-world size="24" />
        {{ timezone }}
      </div>
    </div>

    <template v-if="selectedEvent">
      <div class="appointment-card">
        <h3>{{ t('label.bookingDetails') }}</h3>
        <div class="appointment-card-inner">
          <header>
            {{ selectedEvent.title }}
            <icon-circle-check-filled size="24"/>
          </header>
          <div class="appointment-card-inner-details">
            <icon-calendar size="16"/>
            <span>{{ selectedSlotDate }}</span>
            <icon-map-pin size="16"/>
            <!-- TODO: We are currently only allowing for events to be online but the backend defaults to in person -->
            <!-- <span>{{ selectedEvent.location_type === EventLocationType.Online ? t('label.virtual') : t('label.inPerson') }}</span> -->
            <span>{{ t('label.virtual') }}</span>
            <icon-clock size="16"/>
            <span>{{ selectedSlotTimeDuration }} <span class="timezone-badge">{{ timezone }}</span></span>
            <icon-clock size="16"/>
            <span>{{ t('units.minutes', { value: selectedEvent.slot_duration }) }}</span>
          </div>
        </div>
      </div>

      <slot-selection-user-info v-if="!userStore.authenticated" />
    </template>

    <div v-else class="appointment-card empty">
      {{ t('label.selectATimeFromTheCalendar') }}
      <icon-calendar-clock size="108"/>
    </div>

    <alert-box
      v-if="bookingRequestError"
      :alert="{ title: bookingRequestError }"
      :scheme="AlertSchemes.Error"
      @close="bookingRequestError = ''"
    />

    <primary-button
      :label="t('label.confirmSelection')"
      :disabled="!selectedEvent || bookingRequestLoading || (!userStore.authenticated && !guestUserInfoValid)"
      @click="bookEvent"
      :title="t('label.confirm')"
      class="confirm-selection-button"
      data-testid="booking-view-confirm-selection-button"
    >
      {{ t('label.confirmSelection') }}
    </primary-button>
  </aside>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

aside {
  .invitation-text {
    margin-bottom: 0.825rem;
    font-size: 0.825rem;
    font-weight: 600;
    color: var(--colour-ti-muted);
  }

  .appointment-title {
    margin-bottom: 0.825rem;
    font-size: 1.725rem;
    line-height: 2.25rem;
    color: var(--colour-ti-base);
  }

  .appointment-details {
    margin-bottom: 1.5rem;
    color: var(--colour-ti-base);
  }

  .timezone-section {
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 1rem;

    .timezone-label {
      font-size: 0.875rem;
      line-height: 1.75rem;
      color: var(--colour-ti-base);
    }

    .timezone-display {
      font-size: 0.875rem;
      line-height: 1.25rem;
      color: var(--colour-accent-teal);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
  }

  .appointment-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    padding: 1rem 0.5rem;
    border: 1px dashed var(--colour-neutral-border);
    border-radius: 0.25rem;
    background-color: var(--colour-neutral-raised);
    margin-block-end: 1rem;

    &.empty {
      align-items: center;
      padding: 4rem 1.5rem;
    }

    h3 {
      text-align: center;
      font-weight: 500;
    }

    .appointment-card-inner {
      padding: 1rem 1.5rem;
      border-radius: 0.25rem;
      color: var(--colour-ti-base);
      /* TODO: Color not in design system */
      background-color: #7d9cfb;

      header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-block-end: 1rem;
      }

      .appointment-card-inner-details {
        display: grid;
        grid-template-columns: 1.5rem 1fr;
        align-items: center;
        row-gap: 0.25rem;
        column-gap: 0.125rem;

        .timezone-badge {
          background-color: var(--colour-neutral-raised);
          font-size: 0.75rem;
          padding: 0.25rem 0.375rem;
          margin-inline-start: 0.25rem;
          border-radius: 8px;
        }
      }
    }
  }

  .booking-request-error {
    margin-block: 1rem;
    border-radius: 0.25rem;
    padding: 0.5rem;
    background-color: var(--colour-danger-soft);
    color: var(--colour-danger-default);
  }

  .confirm-selection-button {
    margin-inline-start: auto;
    margin-block-start: 1rem;
  }
}

@media (--md) {
  aside {
    width: 470px;

    .timezone-section {
      flex-direction: row;
    }
  }
}
</style>