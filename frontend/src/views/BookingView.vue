<template>
  <!-- fixed header with app title -->
  <header class="fixed h-24 w-full px-4 shadow-lg bg-white border-b border-gray-300 flex gap-3 items-center">
    <img class="h-10 mr-2" src="/appointment_logo.svg" alt="Appointment Logo">
    <div class="text-4xl font-thin text-teal-500">Thunderbird</div>
    <div class="text-4xl font-thin text-sky-500">Appointment</div>
  </header>
  <!-- booking page content -->
  <main class="max-w-screen-2xl mx-auto py-32 px-4 flex justify-between items-start select-none">
    <div v-if="appointment">
      <div class="text-3xl text-gray-700 mb-4">{{ appointment.title }}</div>
      <div class="font-bold">{{ t('text.nameIsInvitingYou', { name: appointment.owner }) }}</div>
      <div class="text-gray-700 mb-6">{{ appointment.details }}</div>
      <div class="text-xl mb-6">{{ t('text.chooseDayTime') }}</div>
      <calendar-page-heading
        :nav="false"
        :month="activeDate.format('MMMM')"
        :year="activeDate.year().toString()"
        :title="viewTitle"
        :backlink="activeView === views.weekAfterMonth"
        @back="activeView = views.month"
        class="mb-8"
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
        :events="[appointment]"
        :booking="true"
        @event-selected="selectEvent"
      />
      <calendar-day
        v-if="(activeView === views.day)"
        :selected="activeDate"
        :events="[appointment]"
        :booking="true"
        @event-selected="selectEvent"
      />
    </div>
  </main>
  <!-- fixed footer with action button -->
  <footer class="fixed bottom-0 h-24 w-full px-4 bg-white border-t border-gray-300">
    <div class="h-full max-w-screen-2xl mx-auto flex justify-end items-center">
      <primary-button
        class="p-7"
        :label="t('label.confirmSelection')"
        :disabled="!activeEvent"
        @click="openBookingModal"
      />
    </div>
  </footer>
  <!-- modals -->
  <booking-modal :open="showBooking" :event="activeEvent" @booked="bookEvent" @close="closeBookingModal" />
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue'
import CalendarPageHeading from '@/elements/CalendarPageHeading.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import CalendarWeek from '@/components/CalendarWeek.vue';
import CalendarDay from '@/components/CalendarDay.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import BookingModal from '@/components/BookingModal.vue';
import { useI18n } from "vue-i18n";
// import { useRoute } from 'vue-router';
const { t } = useI18n();
// const route = useRoute();
const dj = inject("dayjs");

// appointment data the visitor should see
const appointment = ref({ title: '', slots: [] });

// handle different view and active date
// month: there are multiple weeks of availability, leads to week view for selection
// week: there are multiple days of availability, provides selectable slots
// day: time slots are only on one single day, provides selectable slots
const views = {
  month: 1,
  weekAfterMonth: 2,
  week: 3,
  day: 4
};
const activeView = ref(views.month);
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
    case views.month:
    default:
      return ''
  }
});

// TODO: retrieve appointment by slug
onMounted(() => {
  // TODO: async get appointment data with route.params.slug;
  appointment.value = fakeAppointment;
  activeDate.value = dj(appointment.value?.slots[0].start);
  // check appointment slots for appropriate view
  activeView.value = getViewBySlotDistribution(appointment.value.slots);
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
const closeBookingModal = () => {
  showBooking.value = false;
  activeEvent.value = null;
};

// attendee confirmed the time slot selection: event is booked
const bookEvent = (attendee) => {
  // TODO: create server side event
  console.log(attendee);
};

// TODO: fake data
const fakeAppointment = {
  title: 'Bi-weekly Café Dates',
  status: 'pending',
  mode: 'open',
  calendar: 'Family',
  slug: 'sdfw83jc',
  location_name: 'Signal',
  location_url: '',
  details: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam dictum magna sit amet est iaculis ullamcorper. Quisque tortor orci, cursus in ex sit amet, scelerisque rhoncus erat. Maecenas vehicula elit in pulvinar laoreet. Vivamus suscipit ligula elementum, porttitor dui eu, suscipit lectus. Mauris vitae',
  owner: 'Solange',
  slots: [
    { start: '2022-12-09T11:00:00', duration: 120, attendee: null },
    { start: '2022-12-13T11:00:00', duration: 120, attendee: null },
    { start: '2022-12-13T13:00:00', duration: 120, attendee: null },
    { start: '2022-12-13T15:00:00', duration: 120, attendee: null },
    { start: '2022-12-14T09:30:00', duration: 120, attendee: null },
    { start: '2022-12-15T10:00:00', duration: 120, attendee: null },
    { start: '2022-12-15T12:00:00', duration: 120, attendee: null }
  ]
};

</script>
