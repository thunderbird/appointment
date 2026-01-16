<script setup lang="ts">
import { BookingCalendarView } from '@/definitions';
import { inject, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { dayjsKey, callKey } from '@/keys';
import { useI18n } from 'vue-i18n';
import {
  Appointment, Slot, Exception, ExceptionDetail, AppointmentResponse
} from '@/models';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import BookingViewSlotSelection from './components/BookingViewSlotSelection.vue';
import BookingViewSuccess from './components/BookingViewSuccess.vue';
import BookingViewError from './components/BookingViewError.vue';

// component constants
const dj = inject(dayjsKey);
const call = inject(callKey);
const { t } = useI18n();
const bookingViewStore = useBookingViewStore();

const errorHeading = ref<string>(null);
const errorBody = ref<string>(null);

const {
  appointment,
  activeView,
  activeDate,
  attendee,
  selectedEvent,
} = storeToRefs(bookingViewStore);

// check if slots are distributed over different months, weeks, days or only on a single day
const getViewBySlotDistribution = (slots: Slot[]) => {
  let monthChanged = false;
  let weekChanged = false;
  let dayChanged = false;
  let lastDate = null;
  slots.forEach((slot) => {
    if (!lastDate) {
      lastDate = dj(slot.start);
    } else {
      if (dj(slot.start).format('YYYYMM') !== lastDate.format('YYYYMM')) {
        monthChanged = true;
      }
      if (dj(slot.start).startOf('week').format('YYYYMMDD') !== lastDate.startOf('week').format('YYYYMMDD')) {
        weekChanged = true;
      }
      if (dj(slot.start).format('YYYYMMDD') !== lastDate.format('YYYYMMDD')) {
        dayChanged = true;
      }
    }
    lastDate = dj(slot.start);
  });
  if (monthChanged) {
    return BookingCalendarView.Month;
  }
  if (weekChanged) {
    return BookingCalendarView.Month;
  }
  if (dayChanged) {
    return BookingCalendarView.Week;
  }
  if (!dayChanged) {
    return BookingCalendarView.Day;
  }
  return BookingCalendarView.Invalid;
};

const handleError = (data: Exception) => {
  errorHeading.value = null;
  errorBody.value = null;

  const errorDetail = data?.detail as ExceptionDetail;

  if (errorDetail?.id === 'SCHEDULE_NOT_ACTIVE') {
    errorHeading.value = '';
    errorBody.value = errorDetail.message;
  } else if (errorDetail?.id === 'RATE_LIMIT_EXCEEDED') {
    errorHeading.value = '';
    errorBody.value = errorDetail.message;
  } else if (errorDetail?.id === 'REMOTE_CALENDAR_CONNECTION_ERROR') {
    errorHeading.value = '';
    errorBody.value = t('error.calendarConnectionUnavailable');
  }
};

/**
 * Retrieve the appointment from either availability or booking routes.
 * Returns null if there was an error, or the Appointment object if it was successful.
 */
const getAppointment = async (): Promise<Appointment|null> => {
  const url = window.location.href.split('#')[0];
  const request: AppointmentResponse = call('schedule/public/availability').post({ url });

  const { data, error } = await request.json();

  if (error.value) {
    handleError(data?.value);

    return null;
  }

  // convert start dates from UTC back to users timezone
  data.value.slots.forEach((s: Slot) => {
    s.start = dj(s.start).tz(dj.tz.guess());
  });

  return data.value;
};

// initially retrieve slot data and decide which view to show
onMounted(async () => {
  bookingViewStore.$reset();

  appointment.value = await getAppointment();
  // process appointment data, if everything went fine
  if (appointment.value) {
    activeDate.value = dj(appointment.value?.slots[0].start);
    // check appointment slots for appropriate view
    activeView.value = getViewBySlotDistribution(appointment.value.slots);
  } else {
    activeView.value = BookingCalendarView.Invalid;
  }
});
</script>

<script lang="ts">
export default {
  name: 'BookerView'
}
</script>

<template>
  <!-- booking page content: loading -->
  <main
    v-if="activeView === BookingCalendarView.Loading"
    class="booking-loading-container"
  >
    <loading-spinner/>
  </main>
  <!-- booking page content: invalid link -->
  <main
    v-else-if="activeView === BookingCalendarView.Invalid"
    class="booking-invalid-container"
  >
    <booking-view-error
      :heading="errorHeading"
      :body="errorBody"
    />
  </main>
  <!-- booking page content: successful booking -->
  <main
    v-else-if="activeView === BookingCalendarView.Success"
    class="booking-success-container"
  >
    <booking-view-success
      :attendee-email="attendee.email"
      :selected-event="selectedEvent"
      :requested="appointment?.booking_confirmation"
    />
  </main>
  <!-- booking page content: time slot selection -->
  <main
    v-else
    class="booking-slot-selection-container"
  >
    <booking-view-slot-selection />
  </main>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.booking-loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  user-select: none;
}

.booking-invalid-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  user-select: none;
  flex-direction: column;
  gap: 2rem;
  padding: 0 1rem;
}

.booking-success-container {
  display: flex;
  height: 100vh;
  user-select: none;
  flex-direction: column-reverse;
  align-items: center;
  justify-content: space-evenly;
  padding: 0 1rem;
}

.booking-slot-selection-container {
  margin: 0 auto;
  user-select: none;
  padding: 0 1rem;
  padding-bottom: 2rem;
  color: var(--colour-ti-secondary);
}

@media (--md) {
  .booking-success-container {
    flex-direction: row;
  }
}

@media (--lg) {
  .booking-slot-selection-container {
    padding-inline: 3.5rem;
  }
}
</style>
