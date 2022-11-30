<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <calendar-page-heading
      :month="activeDate.format('MMMM')"
      :year="activeDate.year().toString()"
      :title="pageTitle"
      @prev="dateNav('auto', false)"
      @next="dateNav('auto')"
    />
    <div class="flex gap-8 items-center">
      <button @click="selectDate(dj())" class="font-semibold text-xl text-teal-500 px-4">
        {{ t('label.today') }}
      </button>
      <tab-bar :tab-items="Object.keys(tabItems)" :active="tabActive" @update="updateTab" class="text-xl" />
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="creationStatus !== creationSteps.hidden"
        @click="creationStatus = creationSteps.details"
      />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8 min-h-[767px] items-stretch" :class="{ 'mt-[60px]': tabActive === tabItems.month }">
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-month
      v-show="tabActive === tabItems.month"
      class="w-4/5"
      :selected="activeDate"
      :events="fakeAppointments"
    />
    <calendar-week
      v-show="tabActive === tabItems.week"
      class="w-4/5 flex"
      :selected="activeDate"
    />
    <calendar-day
      v-show="tabActive === tabItems.day"
      class="w-4/5 flex"
      :selected="activeDate"
    />
    <!-- page side bar -->
    <div class="w-1/5">
      <div v-if="creationStatus === creationSteps.hidden" class="flex flex-col gap-8">
        <!-- monthly mini calendar -->
        <calendar-month
          :selected="activeDate"
          :mini="true"
          :nav="true"
          @prev="dateNav('month', false)"
          @next="dateNav('month')"
          @selected="selectDate"
        />
        <!-- appointments and events list -->
        <div>
          <div class="flex justify-between items-center">
            <div class="font-semibold text-lg">{{ t('heading.appointmentsAndEvents') }}</div>
            <router-link class="px-2 py-1 border-r rounded-full bg-teal-500 text-white text-xs uppercase" :to="{ name: 'appointments' }">
              {{ t('label.viewAll') }}
            </router-link>
          </div>
          <div class="text-slate-500 mt-4">
            {{ t('info.noAppointmentsInList') }}
          </div>
        </div>
      </div>
      <!-- appointment creation dialog -->
      <appointment-creation
        v-else
        :status="creationStatus"
        @start="creationStatus = creationSteps.details"
        @next="creationStatus = creationSteps.availability"
        @create="creationStatus = creationSteps.finished"
        @cancel="creationStatus = creationSteps.hidden"
      />
    </div>
  </div>

</template>

<script setup>
import { ref, inject, computed } from 'vue';
import CalendarPageHeading from '@/elements/CalendarPageHeading.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import CalendarWeek from '@/components/CalendarWeek.vue';
import CalendarDay from '@/components/CalendarDay.vue';
import AppointmentCreation from '@/components/AppointmentCreation.vue';
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from 'vue-router';
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject("dayjs");

// current selected date, if not in route: defaults to now
const activeDate = ref(route.params.date ? dj(route.params.date) : dj());
const selectDate = d => {
  router.replace({ name: route.name, params: { view: route.params.view, date: dj(d).format('YYYY-MM-DD') } });
  activeDate.value = dj(d);
};

// date calculations
const startOfActiveWeek = computed(() => {
  return activeDate.value.startOf('week');
});
const endOfActiveWeek = computed(() => {
  return activeDate.value.endOf('week');
});

// menu items for tab navigation
const tabItems = { 'day': 0, 'week': 1, 'month': 2 };
const tabActive = ref(tabItems[route.params.view]);
const updateTab = view => {
  router.replace({ name: route.name, params: { view: view, date: route.params.date ?? dj().format('YYYY-MM-DD') } });
  tabActive.value = tabItems[view];
};

// calculate page title
const pageTitle = computed(() => {
  switch (tabActive.value) {
    case tabItems.day:
      return activeDate.value.format('dddd Do');
    case tabItems.week:
      return startOfActiveWeek.value.format('ddd Do') + ' - ' + endOfActiveWeek.value.format('ddd Do');
    case tabItems.month:
    default:
      return ''
  }
});

// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(tabItems).find(key => tabItems[key] === tabActive.value);
  }
  if (forward) {
    selectDate(activeDate.value.add(1, unit));
  } else {
    selectDate(activeDate.value.subtract(1, unit));
  }
};

// appointment creation
const creationSteps = {
  hidden: 0,
  details: 1,
  availability: 2,
  finished: 3
}
const creationStatus = ref(creationSteps.hidden);

// TODO: fake data
const fakeAppointments = [
  { title: 'Bi-weekly Café Dates', status: 'pending', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-12-10T10:00:00', duration: 60, attendee: null }] },
  { title: 'Dog Park Event', status: 'pending', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-12-10T14:00:00', duration: 60, attendee: null }] },
  { title: 'Interview Process', status: 'pending', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Online', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-12-10T16:00:00', duration: 60, attendee: null }] },
  { title: 'Project Appointment', status: 'pending', mode: 'open', calendar: 'Work', slug: 'sdfw83jc', location_name: 'Jitsi', location_url: 'https://test-conference.org', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-12-12T10:00:00', duration: 60, attendee: null }] },
  { title: 'Bi-weekly Café Dates', status: 'pending', mode: 'open', calendar: 'Family', slug: 'sdfw83jc', location_name: 'Signal', location_url: '', details: 'Lorem Ipsum dolor sit amet', slots: [{ start: '2022-12-14T10:00:00', duration: 60, attendee: null }, { start: '2022-12-14T12:00:00', duration: 60, attendee: null }] },
];

</script>
