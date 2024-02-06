<template>
  <!-- page title area -->
  <div class="flex flex-col lg:flex-row justify-between items-start select-none">
    <div class="text-4xl font-light">{{ t('label.schedule') }}</div>
    <div class="flex flex-col gap-8 md:flex-row mx-auto lg:ml-0 lg:mr-0 items-center">
      <button @click="selectDate(dj())" class="font-semibold text-base text-teal-500 px-4">
        {{ t("label.today") }}
      </button>
      <tab-bar
        :tab-items="calendarViews"
        :active="tabActive"
        @update="updateTab"
        class="text-sm"
      />
      <div class="flex-center gap-2 select-none">
        <div @click="dateNav('auto', false)" class="cursor-pointer">
          <icon-chevron-left class="h-6 w-6 stroke-2 fill-transparent stroke-teal-500" />
        </div>
        <div class="h-12 flex-center flex-col">
          <div class="flex gap-2 text-lg">
            <span class="font-normal">{{ activeDate.format('MMMM') }}</span>
            <span class="font-light">{{ activeDate.format('YYYY')}}</span>
          </div>
          <div v-if="pageTitle" class="text-sm text-center text-gray-500">{{ pageTitle }}</div>
        </div>
        <div @click="dateNav('auto')" class="cursor-pointer">
          <icon-chevron-right class="h-6 w-6 stroke-2 fill-transparent stroke-teal-500" />
        </div>
      </div>
    </div>
  </div>
  <!-- page content -->
  <div
    class="flex flex-col flex-col-reverse md:flex-row justify-between gap-4 lg:gap-24 mt-8 items-stretch"
    :class="{ 'lg:mt-10': tabActive === calendarViews.month }"
  >
    <!-- schedule creation dialog -->
    <div class="w-full sm:w-1/2 md:w-1/5 mx-auto mb-10 md:mb-0 min-w-[310px]">
      <schedule-creation
        v-if="schedulesReady"
        :calendars="connectedCalendars"
        :schedule="firstSchedule"
        :active-date="activeDate"
        @created="getFirstSchedule"
        @updated="schedulePreview"
      />
    </div>
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-month
      v-show="tabActive === calendarViews.month"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
      :schedules="schedulesPreviews"
      popup-position="left"
    />
    <calendar-week
      v-show="tabActive === calendarViews.week"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
      popup-position="left"
    />
    <calendar-day
      v-show="tabActive === calendarViews.day"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
      popup-position="top"
    />
  </div>
</template>

<script setup>
import { calendarViews } from '@/definitions';
import { ref, inject, computed, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import ScheduleCreation from '@/components/ScheduleCreation';
import CalendarDay from '@/components/CalendarDay';
import CalendarMonth from '@/components/CalendarMonth';
import CalendarWeek from '@/components/CalendarWeek';
import TabBar from '@/components/TabBar';

// icons
import { IconChevronLeft, IconChevronRight } from "@tabler/icons-vue";
// stores
import { useAppointmentStore } from '@/stores/appointment-store';
import { useCalendarStore } from '@/stores/calendar-store';

const { t } = useI18n();
const route = useRoute();
const dj = inject('dayjs');
const call = inject('call');
const refresh = inject('refresh');

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();
const { pendingAppointments } = storeToRefs(appointmentStore);
const { connectedCalendars } = storeToRefs(calendarStore);

// current selected date, if not in route: defaults to now
const activeDate = ref(route.params.date ? dj(route.params.date) : dj());
const selectDate = (d) => {
  activeDate.value = dj(d);
};

// date calculations
const startOfActiveWeek = computed(() => activeDate.value.startOf('week'));
const endOfActiveWeek = computed(() => activeDate.value.endOf('week'));

// active menu item for tab navigation of calendar views
const tabActive = ref(calendarViews.month);
const updateTab = (view) => {
  tabActive.value = calendarViews[view];
};

// calculate page title
const pageTitle = computed(() => {
  switch (tabActive.value) {
    case calendarViews.day:
      return activeDate.value.format('dddd Do');
    case calendarViews.week:
      return `${startOfActiveWeek.value.format('ddd Do')} - ${endOfActiveWeek.value.format('ddd Do')}`;
    case calendarViews.month:
    default:
      return '';
  }
});

// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(calendarViews).find((key) => calendarViews[key] === tabActive.value);
  }
  if (forward) {
    selectDate(activeDate.value.add(1, unit));
  } else {
    selectDate(activeDate.value.subtract(1, unit));
  }
};

// get remote calendar data for current year
const calendarEvents = ref([]);
const getRemoteEvents = async (from, to) => {
  // Most calendar impl are non-inclusive of the last day, so just add one to the day.
  const inclusiveTo = dj(to).add(1, 'day').format('YYYY-MM-DD');

  calendarEvents.value = [];
  await Promise.all(connectedCalendars.value.map(async (calendar) => {
    const { data } = await call(`rmt/cal/${calendar.id}/${from}/${inclusiveTo}`).get().json();
    if (Array.isArray(data.value)) {
      calendarEvents.value.push(...data.value.map((e) => ({ ...e, duration: dj(e.end).diff(dj(e.start), 'minutes') })));
    }
  }));
};

// user configured schedules from db (only the first for now, later multiple schedules will be available)
const schedules = ref([]);
const firstSchedule = computed(() => schedules.value?.length > 0 ? schedules.value[0] : null);
const schedulesReady = ref(false);
const getFirstSchedule = async () => {
  calendarEvents.value = [];
  // trailing slash to prevent fast api redirect which doesn't work great on our container setup
  const { data } = await call('schedule/').get().json();
  schedules.value = data.value;
};

// schedule previews for showing corresponding placeholders in calendar views
const schedulesPreviews = ref([]);
const schedulePreview = (schedule) => {
  schedulesPreviews.value = schedule ? [schedule] : [];
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
  await getFirstSchedule();
  schedulesReady.value = true;
  const eventsFrom = dj(activeDate.value).startOf('month').format('YYYY-MM-DD');
  const eventsTo = dj(activeDate.value).endOf('month').format('YYYY-MM-DD');
  await getRemoteEvents(eventsFrom, eventsTo);
});

// react to user calendar navigation
watch(
  () => activeDate.value,
  (newValue, oldValue) => {
    // remote data is retrieved per month, so a data request happens as soon as the user navigates to a different month
    if (dj(oldValue).format('YYYYMM') !== dj(newValue).format('YYYYMM')) {
      getRemoteEvents(
        dj(newValue).startOf('month').format('YYYY-MM-DD'),
        dj(newValue).endOf('month').format('YYYY-MM-DD'),
      );
    }
  },
);
</script>
