<template>
  <div>
    <!-- booking page content: loading -->
    <main
      v-if="activeView === views.loading"
      class="flex-center h-screen select-none"
    >
      <loading-spinner/>
    </main>
    <!-- booking page content: invalid link -->
    <main
      v-else-if="activeView === views.invalid"
      class="flex-center h-screen select-none flex-col gap-8 px-4"
    >
      <booking-view-error
        :heading="errorHeading"
        :body="errorBody"
      />
    </main>
    <!-- booking page content: successful booking -->
    <main
      v-else-if="activeView === views.success"
      class="flex h-screen select-none flex-col-reverse items-center justify-evenly px-4 md:flex-row"
    >
      <booking-view-success
        :attendee-email="attendee.email"
        :selected-event="selectedEvent"
      />
    </main>
    <!-- booking page content: time slot selection -->
    <main
      v-else
      class="mx-auto max-w-screen-2xl select-none px-4"
    >
      <booking-view-slot-selection
        :show-navigation="showNavigation"
        @open-modal="openModal()"
      />
    </main>
    <!-- modals -->
    <booking-modal
      :open="showBookingModal"
      :event="selectedEvent"
      :requires-confirmation="true"
      @book="bookEvent"
      @close="closeModal()"
    />
  </div>
</template>

<script setup>
import { bookingCalendarViews as views, modalStates } from '@/definitions';
import { inject, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { useBookingModalStore } from '@/stores/booking-modal-store';
import LoadingSpinner from '@/elements/LoadingSpinner';
import BookingModal from '@/components/BookingModal';
import BookingViewSlotSelection from '@/components/bookingView/BookingViewSlotSelection.vue';
import BookingViewSuccess from '@/components/bookingView/BookingViewSuccess.vue';
import BookingViewError from '@/components/bookingView/BookingViewError.vue';

// component constants
const { t } = useI18n();
const dj = inject('dayjs');
const call = inject('call');
const bookingViewStore = useBookingViewStore();
const bookingModalStore = useBookingModalStore();

const errorHeading = ref(null);
const errorBody = ref(null);

const bookingRequestFinished = ref(false);

const showNavigation = ref(false);
const showBookingModal = ref(false);

const {
  appointment,
  activeView,
  activeDate,
  attendee,
  selectedEvent,
} = storeToRefs(bookingViewStore);

const {
  openModal, closeModal,
} = bookingModalStore;

const {
  state: modalState, stateData: modalStateData,
} = storeToRefs(bookingModalStore);

// check if slots are distributed over different months, weeks, days or only on a single day
const getViewBySlotDistribution = (slots) => {
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
    showNavigation.value = true;
    return views.month;
  }
  if (weekChanged) {
    return views.month;
  }
  if (dayChanged) {
    return views.week;
  }
  if (!dayChanged) {
    return views.day;
  }
  return views.invalid;
};

/**
 * Retrieve the appointment from either availability or booking routes.
 * Returns null if there was an error, or the Appointment object if it was successful.
 * @returns {Promise<Object|null>}
 */
const getAppointment = async () => {
  const request = call('schedule/public/availability').post({ url: window.location.href });

  const { data, error } = await request.json();

  if (error.value) {
    errorHeading.value = null;
    errorBody.value = null;

    if (data?.value?.detail?.id === 'SCHEDULE_NOT_ACTIVE') {
      errorHeading.value = '';
      errorBody.value = data.value.detail.message;
    }

    return null;
  }

  // convert start dates from UTC back to users timezone
  data.value.slots.forEach((s) => {
    s.start = dj(s.start).tz(dj.tz.guess());
  });

  return data.value;
};

/**
 * Book or request to book a selected time.
 * @param attendeeData
 * @returns {Promise<void>}
 */
const bookEvent = async (attendeeData) => {
  bookingRequestFinished.value = false;

  const obj = {
    slot: {
      start: selectedEvent.value.start,
      duration: selectedEvent.value.duration,
    },
    attendee: attendeeData,
  };

  const request = call('schedule/public/availability/request').put({
    s_a: obj,
    url: window.location.href,
  });

  // Data should just be true here.
  const { data, error } = await request.json();

  if (error.value || !data.value) {
    modalState.value = modalStates.error;
    modalStateData.value = data?.value?.detail?.message ?? t('error.unknownAppointmentError');
    appointment.value = await getAppointment();
    return;
  }

  // replace calendar view if every thing worked fine
  attendee.value = attendeeData;
  // update view to prevent reselection
  activeView.value = views.success;
  // update modal view as well
  modalState.value = modalStates.finished;
};

// initially retrieve slot data and decide which view to show
onMounted(async () => {
  bookingViewStore.$reset();
  bookingModalStore.$reset();

  appointment.value = await getAppointment();
  // process appointment data, if everything went fine
  if (appointment.value) {
    activeDate.value = dj(appointment.value?.slots[0].start);
    // check appointment slots for appropriate view
    activeView.value = getViewBySlotDistribution(appointment.value.slots);
  } else {
    activeView.value = views.invalid;
  }
});
</script>
