<script setup lang="ts">
import { BookingCalendarViews, MetricEvents, ModalStates } from '@/definitions';
import { inject, onMounted, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useBookingViewStore } from '@/stores/booking-view-store';
import { useBookingModalStore } from '@/stores/booking-modal-store';
import { dayjsKey, callKey } from '@/keys';
import {
  Appointment, Slot, Exception, Attendee, ExceptionDetail, AppointmentResponse, SlotResponse,
} from '@/models';
import LoadingSpinner from '@/elements/LoadingSpinner.vue';
import BookingModal from '@/components/BookingModal.vue';
import BookingViewSlotSelection from '@/components/bookingView/BookingViewSlotSelection.vue';
import BookingViewSuccess from '@/components/bookingView/BookingViewSuccess.vue';
import BookingViewError from '@/components/bookingView/BookingViewError.vue';
import { usePosthog, posthog } from '@/composables/posthog';

// component constants
const { t } = useI18n();
const dj = inject(dayjsKey);
const call = inject(callKey);
const bookingViewStore = useBookingViewStore();
const bookingModalStore = useBookingModalStore();

const errorHeading = ref<string>(null);
const errorBody = ref<string>(null);

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

const { openModal, closeModal } = bookingModalStore;

const { state: modalState, stateData: modalStateData } = storeToRefs(bookingModalStore);

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
    showNavigation.value = true;
    return BookingCalendarViews.Month;
  }
  if (weekChanged) {
    return BookingCalendarViews.Month;
  }
  if (dayChanged) {
    return BookingCalendarViews.Week;
  }
  if (!dayChanged) {
    return BookingCalendarViews.Day;
  }
  return BookingCalendarViews.Invalid;
};

const handleError = (data: Exception) => {
  errorHeading.value = null;
  errorBody.value = null;

  const errorDetail = data?.detail as ExceptionDetail;

  if (errorDetail?.id === 'SCHEDULE_NOT_ACTIVE') {
    errorHeading.value = '';
    errorBody.value = errorDetail.message;
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

/**
 * Book or request to book a selected time.
 * @param attendeeData
 */
const bookEvent = async (attendeeData: Attendee) => {
  bookingRequestFinished.value = false;

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

  if (error.value || !data.value) {
    modalState.value = ModalStates.Error;
    modalStateData.value = data?.value?.detail?.message ?? t('error.unknownAppointmentError');
    appointment.value = await getAppointment();
    return;
  }

  // replace calendar view if every thing worked fine
  attendee.value = attendeeData;
  // update view to prevent reselection
  activeView.value = BookingCalendarViews.Success;
  // update modal view as well
  modalState.value = ModalStates.Finished;

  if (usePosthog) {
    // Not chained because it's the inverse of booking_confirmation, and it defaults to false.
    const autoConfirmed = appointment && appointment.value.booking_confirmation !== undefined
      ? !appointment.value.booking_confirmation : false;
    posthog.capture(MetricEvents.RequestBooking, {
      autoConfirmed
    });
  }
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
    activeView.value = BookingCalendarViews.Invalid;
  }
});
</script>

<template>
  <div>
    <!-- booking page content: loading -->
    <main
      v-if="activeView === BookingCalendarViews.Loading"
      class="flex-center h-screen select-none"
    >
      <loading-spinner/>
    </main>
    <!-- booking page content: invalid link -->
    <main
      v-else-if="activeView === BookingCalendarViews.Invalid"
      class="flex-center h-screen select-none flex-col gap-8 px-4"
    >
      <booking-view-error
        :heading="errorHeading"
        :body="errorBody"
      />
    </main>
    <!-- booking page content: successful booking -->
    <main
      v-else-if="activeView === BookingCalendarViews.Success"
      class="flex h-screen select-none flex-col-reverse items-center justify-evenly px-4 md:flex-row"
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
      :requires-confirmation="appointment?.booking_confirmation"
      @book="bookEvent"
      @close="closeModal()"
    />
  </div>
</template>
