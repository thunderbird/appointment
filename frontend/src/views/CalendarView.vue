<template>
  <div class="flex flex-col lg:flex-row w-full m-8 mt-0 justify-center">
    <alert-box
      title="Calendar Setup"
      :scheme="alertSchemes.warning"
      v-if="connectedCalendars.length === 0 && !hideUntilRefreshed"
    >
      <i18n-t keypath="error.noConnectedCalendars" tag="label" for="error.noConnectedCalendars">
        <a class="underline" href="/settings/calendar" target="_blank">{{ t('error.noConnectedCalendarsLink') }}</a>
      </i18n-t>
    </alert-box>
  </div>
  <!-- page title area -->
  <div class="flex flex-col lg:flex-row justify-between items-start select-none">
    <div class="flex flex-col gap-8 md:flex-row mx-auto md:mr-0 items-center">
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="!connectedCalendars.length || creationStatus !== appointmentCreationState.hidden"
        @click="creationStatus = appointmentCreationState.details"
      />
    </div>
  </div>
  <!-- page content -->
  <div
    class="flex flex-col flex-col-reverse md:flex-row justify-between gap-4 lg:gap-8 mt-8 items-stretch"
    :class="{ 'lg:mt-10': tabActive === calendarViews.month }"
  >
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-qalendar
      class="w-full md:w-4/5"
      :current-date="activeDate"
      :appointments="appointmentStore.pendingAppointments"
      :events="calendarEvents"
      @date-change="onDateChange"
    />
    <!-- page side bar -->
    <div class="w-full sm:w-1/2 md:w-1/5 mx-auto mb-10 md:mb-0 min-w-[310px]">
      <div v-if="creationStatus === appointmentCreationState.hidden" class="flex flex-col gap-8">
        <!-- monthly mini calendar -->
        <calendar-month
          :selected="activeDate"
          :mini="true"
          :nav="true"
          :events="calendarEvents"
          @prev="dateNav('month', false)"
          @next="dateNav('month')"
          @day-selected="selectDate"
        />
        <!-- appointments and events list -->
        <div>
          <div class="flex justify-between items-center">
            <div class="font-semibold text-lg">
              {{ t("heading.pendingAppointments") }}
            </div>
            <router-link
              class="px-2 py-1 border-r rounded-full text-xs uppercase bg-teal-500 text-white"
              :to="{ name: 'appointments' }"
            >
              {{ t("label.viewAll") }}
            </router-link>
          </div>
          <div
            v-if="appointmentStore.pendingAppointments.length === 0"
            class="mt-4 flex flex-col gap-8 justify-center items-center text-gray-500"
          >
            <div class="text-center mt-4">
              {{ t("info.noPendingAppointmentsInList") }}
            </div>
            <primary-button
              :label="t('label.createAppointments')"
              :disabled="!connectedCalendars.length || creationStatus !== appointmentCreationState.hidden"
              @click="creationStatus = appointmentCreationState.details"
            />
          </div>
          <div v-else class="flex flex-col gap-8 mt-4">
            <appointment-list-item
              v-for="a in appointmentStore.pendingAppointments"
              :key="a.id"
              :appointment="a"
            />
          </div>
        </div>
      </div>
      <!-- appointment creation dialog -->
      <appointment-creation
        v-else
        :status="creationStatus"
        :calendars="connectedCalendars"
        @start="creationStatus = appointmentCreationState.details"
        @next="creationStatus = appointmentCreationState.availability"
        @create="
          creationStatus = appointmentCreationState.finished;
          refresh();
        "
        @cancel="creationStatus = appointmentCreationState.hidden"
      />
    </div>
  </div>
</template>

<script setup>
import { appointmentCreationState, calendarViews, alertSchemes } from '@/definitions';
import {
  ref, inject, computed, onMounted,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import AppointmentCreation from '@/components/AppointmentCreation';
import AppointmentListItem from '@/elements/AppointmentListItem';
import CalendarMonth from '@/components/CalendarMonth';
import PrimaryButton from '@/elements/PrimaryButton';
import AlertBox from '@/elements/AlertBox.vue';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { storeToRefs } from 'pinia';
import CalendarQalendar from '@/components/CalendarQalendar.vue';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject('dayjs');
const call = inject('call');
const refresh = inject('refresh');

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();
const { connectedCalendars } = storeToRefs(calendarStore);

// current selected date, if not in route: defaults to now
const activeDate = ref(route.params.date ? dj(route.params.date) : dj());
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('month'),
  end: activeDate.value.endOf('month'),
}));

// date calculations
const startOfActiveWeek = computed(() => activeDate.value.startOf('week'));
const endOfActiveWeek = computed(() => activeDate.value.endOf('week'));

// active menu item for tab navigation of calendar views
const tabActive = ref(calendarViews[route.params.view]);
const updateTab = (view) => {
  router.replace({
    name: route.name,
    params: { view, date: route.params.date ?? dj().format('YYYY-MM-DD') },
  });
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

// appointment creation state
const creationStatus = ref(appointmentCreationState.hidden);

// get remote calendar data for current year
const calendarEvents = ref([]);

// Hides a "No calendars" message until we've called refresh()
const hideUntilRefreshed = ref(true);

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

/**
 * Retrieve new events if a user navigates to a different month
 * @param dateObj
 */
const onDateChange = async (dateObj) => {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  // remote data is retrieved per month, so a data request happens as soon as the user navigates to a different month
  if ((dj(activeDateRange.value.end).format('YYYYMM') !== end.format('YYYYMM')
    || dj(activeDateRange.value.start).format('YYYYMM') !== start.format('YYYYMM'))) {
    await getRemoteEvents(
      start.format('YYYY-MM-DD'),
      end.format('YYYY-MM-DD'),
    );
  }
};

const selectDate = async (d) => {
  const date = dj(d);
  await router.replace({
    name: route.name,
    params: { view: route.params.view, date: date.format('YYYY-MM-DD') },
  });
  // Check if we need to pull remote events
  await onDateChange({ start: date.startOf('month'), end: date.endOf('month') });

  // Update our activeDate
  activeDate.value = date;
};

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

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
  const eventsFrom = dj(activeDate.value).startOf('month').format('YYYY-MM-DD');
  const eventsTo = dj(activeDate.value).endOf('month').format('YYYY-MM-DD');
  await getRemoteEvents(eventsFrom, eventsTo);
  // Okay, if we still have no calendars, show the ugly message
  hideUntilRefreshed.value = false;
});
</script>
