<template>
  <!-- page title area -->
  <div class="flex select-none flex-col items-start justify-between lg:flex-row">
    <div class="text-4xl font-light">{{ t('label.schedule') }}</div>
  </div>
  <!-- page content -->
  <div
    class="mt-8 flex flex-col-reverse items-stretch justify-between gap-4 md:flex-row"
    :class="{ 'lg:mt-10': tabActive === calendarViews.month }"
  >
    <!-- schedule creation dialog -->
    <div class="mx-auto mb-10 w-full min-w-[360px] sm:w-1/2 md:mb-0 md:w-1/4">
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
    <calendar-qalendar
      class="w-full"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
      :schedules="schedulesPreviews"
      @date-change="onDateChange"
    />
  </div>
</template>

<script setup>
import { calendarViews } from '@/definitions';
import {
  ref, inject, computed, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import ScheduleCreation from '@/components/ScheduleCreation';

// stores
import { useAppointmentStore } from '@/stores/appointment-store';
import { useCalendarStore } from '@/stores/calendar-store';
import CalendarQalendar from '@/components/CalendarQalendar.vue';

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
const activeDateRange = ref({
  start: activeDate.value.startOf('month'),
  end: activeDate.value.endOf('month'),
});

// active menu item for tab navigation of calendar views
const tabActive = ref(calendarViews.month);

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
const firstSchedule = computed(() => (schedules.value?.length > 0 ? schedules.value[0] : null));
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

/**
 * Retrieve new events if a user navigates to a different month
 * @param dateObj
 */
const onDateChange = (dateObj) => {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  // remote data is retrieved per month, so a data request happens as soon as the user navigates to a different month
  if (
    dj(activeDateRange.value.end).format('YYYYMM') !== dj(end).format('YYYYMM')
      || dj(activeDateRange.value.start).format('YYYYMM') !== dj(start).format('YYYYMM')
  ) {
    getRemoteEvents(
      dj(start).format('YYYY-MM-DD'),
      dj(end).format('YYYY-MM-DD'),
    );
  }
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
</script>
