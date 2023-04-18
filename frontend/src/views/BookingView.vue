<template>
  <!-- booking page content: loading -->
  <main
    v-if="activeView === views.loading"
    class="h-screen flex-center select-none"
  >
    <div class="w-12 h-12 rounded-full animate-spin border-4 border-gray-100 dark:border-gray-600 !border-t-teal-600"></div>
  </main>
  <!-- booking page content: invalid link -->
  <main
    v-else-if="activeView === views.invalid"
    class="h-screen px-4 flex-center flex-col gap-8 select-none"
  >
    <art-invalid-link class="max-w-sm h-auto my-6" />
    <div class="text-xl font-semibold text-sky-600">
      {{ t('info.bookingLinkHasAlreadyBeenUsed') }}
    </div>
    <div class="text-gray-800 dark:text-gray-300">
      {{ t('info.bookedPleaseCheckEmail') }}
    </div>
    <primary-button
      class="p-7 mt-12"
      :label="t('label.startUsingTba')"
      @click="null"
    />
  </main>
  <!-- booking page content: successful booking -->
  <main
    v-else-if="activeView === views.success"
    class="h-screen px-4 flex-center flex-col gap-8 select-none"
  >
    <art-successful-booking class="max-w-sm h-auto my-6" />
    <div class="text-2xl font-semibold text-teal-600">
      {{ t('info.bookingSuccessful') }}
    </div>
    <div class="w-full max-w-md shadow-lg rounded-lg p-2 flex flex-col gap-2">
      <div class="rounded-md bg-gray-100 text-gray-500 text-2xl font-bold p-4 w-full text-center">
        {{ activeEvent.title }}
      </div>
      <div class="flex flex-col gap-1 text-center">
        <div class="text-teal-600 font-semibold">{{ dj(activeEvent.start).format('dddd') }}</div>
        <div class="text-lg">{{ dj(activeEvent.start).format('LL') }}</div>
        <div class="uppercase">{{ dj(activeEvent.start).format('LT') }}</div>
      </div>
    </div>
    <div class="text-teal-600 text-sm underline underline-offset-2 -mt-4 cursor-pointer" @click="downloadIcs">
      {{ t('label.downloadTheIcsFile') }}
    </div>
    <div class="text-gray-700 text-lg text-center">
      <div>{{ t('info.invitationWasSent') }}</div>
      <div class="font-bold text-lg">
        {{ attendee.email }}
      </div>
    </div>
    <div class="text-sky-600 text-sm underline underline-offset-2 -mt-4">
      {{ t('label.sendInvitationToAnotherEmail') }}
    </div>
  </main>
  <!-- booking page content: time slot selection -->
  <main v-else class="max-w-screen-2xl mx-auto py-32 px-4 select-none">
    <div v-if="appointment">
      <div class="text-3xl text-gray-700 dark:text-gray-400 mb-4">{{ appointment.title }}</div>
      <div class="font-bold">{{ t('text.nameIsInvitingYou', { name: appointment.owner_name }) }}</div>
      <div class="text-gray-700 dark:text-gray-400 mb-6">{{ appointment.details }}</div>
      <div class="text-xl mb-6">{{ t('text.chooseDayTime') }}</div>
      <calendar-page-heading
        :nav="false"
        :month="activeDate.format('MMMM')"
        :year="activeDate.year().toString()"
        :title="viewTitle"
        :backlink="activeView === views.weekAfterMonth"
        @back="activeView = views.month"
      />
      <calendar-month
        v-if="(activeView === views.month)"
        :selected="activeDate"
        :appointments="dayPlaceholder"
        :placeholder="true"
        @event-selected="showWeek"
      />
      <calendar-week
        v-if="(activeView === views.week || activeView === views.weekAfterMonth)"
        :selected="activeDate"
        :appointments="[appointment]"
        :booking="true"
        @event-selected="selectEvent"
      />
      <calendar-day
        v-if="(activeView === views.day)"
        :selected="activeDate"
        :appointments="[appointment]"
        :booking="true"
        @event-selected="selectEvent"
      />
    </div>
    <!-- fixed footer with action button -->
    <footer
      class="
        fixed bottom-0 left-0 h-24 w-full px-4 border-t
        bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600
      "
    >
      <div class="h-full max-w-screen-2xl mx-auto flex justify-end items-center">
        <!-- <primary-button
          class="p-7"
          label="download"
          @click="downloadIcs"
        /> -->
        <primary-button
          class="p-7"
          :label="t('label.confirmSelection')"
          :disabled="!activeEvent"
          @click="openBookingModal"
        />
      </div>
    </footer>
  </main>
  <!-- modals -->
  <booking-modal
    :open="showBooking"
    :event="activeEvent"
    :success="activeView === views.success"
    @book="bookEvent"
    @download="downloadIcs"
    @close="closeBookingModal"
  />
</template>

<script setup>
import { bookingCalendarViews as views, appointmentState } from '@/definitions';
import { download } from '@/utils';
import { ref, inject, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import ArtInvalidLink from '@/elements/arts/ArtInvalidLink';
import ArtSuccessfulBooking from '@/elements/arts/ArtSuccessfulBooking';
import BookingModal from '@/components/BookingModal';
import CalendarDay from '@/components/CalendarDay';
import CalendarMonth from '@/components/CalendarMonth';
import CalendarPageHeading from '@/elements/CalendarPageHeading';
import CalendarWeek from '@/components/CalendarWeek';
import PrimaryButton from '@/elements/PrimaryButton';

// component constants
const { t } = useI18n();
const route = useRoute();
const dj = inject("dayjs");
const call = inject("call");
const getAppointmentStatus = inject("getAppointmentStatus");

// appointment data the visitor should see
const appointment = ref(null);

// handle different view and active date
// month: there are multiple weeks of availability, leads to week view for selection
// week: there are multiple days of availability, provides selectable slots
// day: time slots are only on one single day, provides selectable slots
const activeView = ref(views.loading);
const activeDate = ref(dj());
const startOfActiveWeek = computed(() => {
  return activeDate.value.startOf('week');
});
const endOfActiveWeek = computed(() => {
  return activeDate.value.endOf('week');
});
const viewTitle = computed(() => {
  switch (activeView.value) {
    case views.day:
      return activeDate.value.format('dddd Do');
    case views.week:
    case views.weekAfterMonth:
      return startOfActiveWeek.value.format('ddd Do') + ' - ' + endOfActiveWeek.value.format('ddd Do');
    default:
      return ''
  }
});

// retrieve appointment by slug
onMounted(async () => {
  // async get appointment data from route
  const { error, data } = await call("apmt/public/" + route.params.slug).get().json();
  // check if appointment exists and is open
  if (error.value || getAppointmentStatus(data.value) !== appointmentState.pending) {
    activeView.value = views.invalid;
  } else {
    appointment.value = data.value;
    // convert start dates from UTC back to users timezone
    appointment.value.slots.forEach(s => {
      s.start = dj.utc(s.start).tz(dj.tz.guess());
    });
    activeDate.value = dj(appointment.value?.slots[0].start);
    // check appointment slots for appropriate view
    activeView.value = getViewBySlotDistribution(appointment.value.slots);
  }
});

// check if slots are distributed over different months, weeks, days or only on a single day
const getViewBySlotDistribution = (slots) => {
  let monthChanged = false, weekChanged = false, dayChanged = false, lastDate = null;
  slots.forEach(slot => {
    if (!lastDate) {
      lastDate = dj(slot.start);
    } else {
      if (dj(slot.start).format('YYYYMM') !== lastDate.format('YYYYMM')) monthChanged = true;
      if (dj(slot.start).startOf('week').format('YYYYMMDD') !== lastDate.startOf('week').format('YYYYMMDD')) weekChanged = true;
      if (dj(slot.start).format('YYYYMMDD') !== lastDate.format('YYYYMMDD')) dayChanged = true;
    }
    lastDate = dj(slot.start);
  });
  if (monthChanged) return views.month;
  if (weekChanged) return views.month;
  if (dayChanged) return views.week;
  if (!dayChanged) return views.day;
};

// prepare events to show one placeholder per day
const dayPlaceholder = computed(() => {
  const apmt = { title: t('label.checkAvailableSlots'), slots: [] };
  const existingDates = [];
  appointment.value?.slots.forEach(slot => {
    const key = dj(slot.start).format('YYYY-MM-DD');
    if (!existingDates.includes(key)) {
      existingDates.push(key);
      apmt.slots.push(slot);
    }
  });
  return [apmt];
});

// change from month view to week view
const showWeek = d => {
  activeDate.value = dj(d);
  activeView.value = views.weekAfterMonth;
};

// selected event for booking
const activeEvent = ref();

// user selected a time slot: mark event as selected
const selectEvent = d => {
  // set event selected
  for (let i = 0; i < appointment.value.slots.length; i++) {
    const slot = appointment.value.slots[i];
    if (slot.start === d) {
      slot.selected = true;
      const e = {...appointment.value, ...slot};
      delete e.slots;
      activeEvent.value = e;
    } else {
      slot.selected = false;
    }
  }
};

// handle booking modal
const showBooking = ref(false);
const openBookingModal = () => showBooking.value = true;
const closeBookingModal = () => showBooking.value = false;

// attendee confirmed the time slot selection: book event
const attendee = ref(null);
const bookEvent = async (attendeeData) => {
  // build data object for put request
  const obj = {
    slot_id: activeEvent.value.id,
    attendee: attendeeData
  };
  // update server side event
  const { error } = await call("apmt/public/" + route.params.slug).put(obj).json();
  // disable calendar view if every thing worked fine
  if (!error.value) {
    attendee.value = attendeeData;
    // update view to prevent reselection
    activeView.value = views.success;
  }
};

// download calendar event as .ics
const downloadIcs = async () => {
  // download ICS file
  const { data, error } = await call("serve/ics/" + route.params.slug + "/" + activeEvent.value.id).get().json();
  if (!error.value) {
    download(data.value.data, data.value.name, data.value.content_type);
  }
};

</script>
