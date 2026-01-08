<script setup lang="ts">
import { computed, inject, ref, useTemplateRef } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import {
  PhCalendarBlank,
  PhClock,
  PhMapPin
} from '@phosphor-icons/vue';
import { TextInput, PrimaryButton } from '@thunderbirdops/services-ui';
import { dayjsKey, callKey } from '@/keys';
import { SlotResponse } from '@/models';
import { usePosthog, posthog } from '@/composables/posthog';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { useUserStore } from '@/stores/user-store';
import { BookingCalendarView, MetricEvents, AlertSchemes } from '@/definitions';
import AlertBox from '@/elements/AlertBox.vue';

const { t } = useI18n();

const dj = inject(dayjsKey);
const call = inject(callKey);

const userStore = useUserStore();
const {
  appointment,
  selectedEvent,
  attendee,
  activeView
} = storeToRefs(useBookingViewStore());

const userInfoForm = useTemplateRef<HTMLFormElement>('userInfoForm');

const bookingRequestLoading = ref<boolean>(false);
const bookingRequestError = ref<string>('');
const guestUserName = ref<string>('');
const guestUserEmail = ref<string>('');

const timezone = computed(() => dj.tz.guess());
const selectedSlotDate = computed(() => dj(selectedEvent.value?.start).format('LL'))
const selectedSlotDateDayOfWeek = computed(() => dj(selectedEvent.value?.start).format('dddd'));
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
  if (!userInfoForm.value.checkValidity()) {
    userInfoForm.value.reportValidity();
    return;
  }

  bookingRequestLoading.value = true;
  bookingRequestError.value = '';

  const attendeeData = userStore.authenticated ? {
    id: userStore.data.id,
    email: userStore.data.email,
    name: userStore.data.name,
    timezone: userStore.data.settings.timezone,
  } : {
    email: guestUserEmail.value,
    name: guestUserName.value,
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
    <h3>{{ t('label.bookingDetails') }}</h3>

    <template v-if="selectedEvent">
      <div class="appointment-card-inner">
        <header>{{ selectedEvent.title }}</header>
        <div class="appointment-card-inner-details">
          <div class="appointment-card-inner-details-item">
            <ph-calendar-blank size="20"/>
            <div class="appointment-card-inner-details-item-details">
              <p>{{ selectedSlotDateDayOfWeek }}</p>
              <span>{{ selectedSlotDate }}</span>
            </div>
          </div>
          <div class="appointment-card-inner-details-item">
            <ph-clock size="20"/>
            <div class="appointment-card-inner-details-item-details">
              <p>{{ timezone }}</p>
              <span>{{ selectedSlotTimeDuration }}</span>
            </div>
          </div>
          <div class="appointment-card-inner-details-item">
            <ph-clock size="20"/>
            <span>{{ t('units.minutes', { value: selectedEvent.slot_duration }) }}</span>
          </div>
          <div class="appointment-card-inner-details-item">
            <ph-map-pin size="20"/>
            <!-- TODO: We are currently only allowing for events to be online but the backend defaults to in person -->
            <!-- <span>{{ selectedEvent.location_type === EventLocationType.Online ? t('label.virtual') : t('label.inPerson') }}</span> -->
            <span>{{ t('label.virtual') }}</span>
          </div>
        </div>
      </div>

      <form ref="userInfoForm" class="user-info-form" @submit.prevent @keyup.enter="bookEvent">
        <text-input required name="booker-view-user-name" v-model="guestUserName">
          {{ t('label.name') }}
        </text-input>

        <text-input required type="email" name="booker-view-user-email" v-model="guestUserEmail">
          {{ t('label.email') }}
        </text-input>

        <alert-box
          v-if="bookingRequestError"
          :alert="{ title: bookingRequestError }"
          :scheme="AlertSchemes.Error"
          @close="bookingRequestError = ''"
          class="booking-request-error"
        />

        <primary-button
          v-if="selectedEvent && userInfoForm"
          :label="t('label.bookAppointment')"
          :disabled="bookingRequestLoading"
          @click="bookEvent"
          :title="t('label.confirm')"
          class="book-appointment-button"
          data-testid="booking-view-confirm-selection-button"
        >
          {{ t('label.bookAppointment') }}
        </primary-button>
      </form>

      <p
        v-if="selectedEvent && !appointment.booking_confirmation"
        class="confirmation-footer-note"
      >
        {{ t('label.yourAppointmentWillBeConfirmedAutomatically') }}
      </p>
    </template>

    <div v-else class="appointment-card empty">
      <ph-calendar-blank size="24" class="empty-icon" weight="duotone" />
      <strong>{{ t('label.noneSelected') }}</strong>
      <p>{{ t('label.selectATimeFromTheCalendar') }}</p>
    </div>
  </aside>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

aside {
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  border: 1px solid var(--colour-neutral-border);
  border-radius: 24px;
  background-color: var(--colour-neutral-base);
  font-family: Inter, sans-serif;

  h3 {
    font-weight: 600;
    color: var(--colour-ti-highlight);
    margin-block-end: 1.5rem;
  }

  .appointment-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border: 1px solid var(--colour-neutral-border);
    border-radius: 4px;
    background-color: var(--colour-neutral-lower);
    margin-block-end: 1.5rem;

    &.empty {
      align-items: center;
      text-align: center;
      font-size: 1rem;
      gap: 0;
      margin-block-end: 0;

      .empty-icon {
        margin-block: 0.75rem 1.5rem;
      }

      strong {
        font-weight: 500;
        margin-block-end: 0.5rem;
      }

      p {
        font-size: 0.875rem;
        margin-block-end: 0.75rem;
      }
    }
  }

  .appointment-card-inner {
    padding: 0.75rem;
    border-radius: 0.25rem;
    background-color: var(--colour-primary-soft);
    margin-block-end: 1.5rem;

    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 600;
      margin-block-end: 0.5rem;
      color: var(--colour-ti-base);
    }

    .appointment-card-inner-details {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      font-size: 0.875rem;
      color: var(--colour-ti-base);

      .appointment-card-inner-details-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        .appointment-card-inner-details-item-details {
          display: flex;
          flex-direction: column;

          p {
            line-height: 0.75rem;
            font-size: 0.6875rem;
          }
        }
      }

      svg {
        color: var(--colour-ti-highlight);
      }
    }
  }

  .user-info-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;

    .book-appointment-button {
      text-transform: capitalize;
    }
  } 

  .booking-request-error {
    margin-block: 1rem;
    border-radius: 0.25rem;
    padding: 0.5rem;
    background-color: var(--colour-danger-soft);
    color: var(--colour-danger-default);
  }

  .booking-request-error {
    margin-block: 0;
  }

  .confirmation-footer-note {
    text-align: center;
    font-size: 0.6875rem;
    margin-block-start: 1rem;
  }
}

@media (--md) {
  aside {
    position: sticky;
    top: 5rem;
    width: 268px;
  }
}
</style>
