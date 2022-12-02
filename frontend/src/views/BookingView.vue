<template>
  <!-- fixed header -->
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
      <div class="text-gray-700 mb-8">{{ appointment.details }}</div>
      <div class="text-xl">{{ t('text.chooseDayTime') }}</div>
      <div v-if="(activeView === views.month)">
        <calendar-month
          :selected="activeDate"
          :events="eventPlaceholder"
          :placeholder="true"
          @event-selected="showWeek"
        />
      </div>
      <div v-if="(activeView === views.week)">
        <calendar-week
          :selected="activeDate"
          :events="[appointment]"
          @selected="null"
        />
      </div>
    </div>
  </main>
  <!-- fixed footer with action button -->
  <footer class="fixed bottom-0 h-24 w-full px-4 bg-white border-t border-gray-300">
    <div class="h-full max-w-screen-2xl mx-auto flex justify-end items-center">
      <primary-button
        class="p-7"
        :label="t('label.confirmSelection')"
        :disabled="true"
        @click="null"
      />
    </div>
  </footer>
</template>

<script setup>
import { ref, inject, onMounted, computed } from 'vue'
import CalendarMonth from '@/components/CalendarMonth.vue';
import CalendarWeek from '@/components/CalendarWeek.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import { useI18n } from "vue-i18n";
// import { useRoute } from 'vue-router';
const { t } = useI18n();
// const route = useRoute();
const dj = inject("dayjs");

// appointment data the visitor should see
const appointment = ref({ title: '', slots: [] });

// handle different view adn active date
// month: there are multiple weeks of availability, leads to week view for selection
// week: there are multiple days of availability, provides selectable slots
// day: time slots are only on one single day, provides selectable slots
const views = {
  month: 1,
  week: 2,
  day: 3
};
const activeView = ref(views.month);
const activeDate = ref(dj());

// TODO: retrieve appointment by slug
onMounted(() => {
  // TODO: async get appointment data with route.params.slug;
  appointment.value = fakeAppointment;
  activeDate.value = dj(appointment.value?.slots[0].start);
  // TODO: check appointment for appropriate view
});

// prepare events to show one placeholder per day
const eventPlaceholder = computed(() => {
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
  activeView.value = views.week;
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
    { start: '2022-12-13T11:00:00', duration: 120, attendee: null },
    { start: '2022-12-13T13:00:00', duration: 120, attendee: null },
    { start: '2022-12-13T15:00:00', duration: 120, attendee: null },
    { start: '2022-12-14T09:30:00', duration: 120, attendee: null },
    { start: '2022-12-15T10:00:00', duration: 120, attendee: null },
    { start: '2022-12-15T12:00:00', duration: 120, attendee: null }
  ]
};

</script>
