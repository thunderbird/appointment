<template>
  <div class="m-8 mt-0 flex w-full flex-col justify-center lg:flex-row">
    <alert-box
      title="Calendar Setup"
      :scheme="AlertSchemes.Warning"
      v-if="connectedCalendars.length === 0 && !hideUntilRefreshed"
    >
      <i18n-t keypath="error.noConnectedCalendars" tag="label" for="error.noConnectedCalendars">
        <a class="underline" href="/settings/calendar" target="_blank">{{ t('error.noConnectedCalendarsLink') }}</a>
      </i18n-t>
    </alert-box>
  </div>
  <!-- page content -->
  <div
    class="mt-8 flex flex-col-reverse justify-between gap-4 md:flex-row lg:gap-8 lg:mt-10"
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
    <div class="mx-auto mb-10 w-full min-w-[310px] sm:w-1/2 md:mb-0 md:w-1/5">
      <div class="flex flex-col gap-8">
        <!-- monthly mini calendar -->
        <calendar-mini-month
          :selected="activeDate"
          :nav="true"
          :events="calendarEvents"
          @prev="dateNav('month', false)"
          @next="dateNav('month', true)"
          @day-selected="selectDate"
        />
        <!-- appointments and events list -->
        <div>
          <div class="flex items-center justify-between">
            <div class="text-lg font-semibold">
              {{ t("heading.pendingAppointments") }}
            </div>
            <router-link
              class="rounded-full border-r bg-teal-500 px-2 py-1 text-xs uppercase text-white"
              :to="{ name: 'appointments' }"
            >
              {{ t("label.viewAll") }}
            </router-link>
          </div>
          <div
            v-if="appointmentStore.pendingFutureAppointments.length === 0"
            class="mt-4 flex flex-col items-center justify-center gap-8 text-gray-500"
          >
            <div class="mt-4 text-center">
              {{ t("info.noPendingAppointmentsInList") }}
            </div>
          </div>
          <div v-else class="mt-4 flex flex-col gap-8">
            <appointment-list-item
              v-for="a in appointmentStore.pendingFutureAppointments"
              :key="a.id"
              :appointment="a"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertSchemes } from '@/definitions';
import {
  ref, inject, computed, onMounted,
} from 'vue';
import { ManipulateType } from 'dayjs';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import AppointmentListItem from '@/elements/AppointmentListItem.vue';
import AlertBox from '@/elements/AlertBox.vue';
import CalendarMiniMonth from '@/components/CalendarMiniMonth.vue';
import CalendarQalendar from '@/components/CalendarQalendar.vue';
import { useCalendarStore } from '@/stores/calendar-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { storeToRefs } from 'pinia';
import { dayjsKey, callKey, refreshKey } from "@/keys";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject(dayjsKey);
const call = inject(callKey);
const refresh = inject(refreshKey);

const appointmentStore = useAppointmentStore();
const calendarStore = useCalendarStore();
const { connectedCalendars } = storeToRefs(calendarStore);

// current selected date, if not in route: defaults to now
const activeDate = ref(route.params.date ? dj(route.params.date as string) : dj());
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('month'),
  end: activeDate.value.endOf('month'),
}));

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
    params: { date: date.format('YYYY-MM-DD') },
  });
  // Check if we need to pull remote events
  await onDateChange({ start: date.startOf('month'), end: date.endOf('month') });

  // Update our activeDate
  activeDate.value = date;
};

// date navigation
const dateNav = (unit: ManipulateType = 'month', forward = true) => {
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
