<template>
  <!-- page title area -->
  <div class="flex justify-between items-start select-none">
    <calendar-page-heading
      :nav="true"
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
      <tab-bar :tab-items="tabItems" :active="tabActive" @update="updateTab" class="text-xl" />
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="creationStatus !== creationState.hidden"
        @click="creationStatus = creationState.details"
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
      :appointments="appointments"
      :events="calendarEvents"
    />
    <calendar-week
      v-show="tabActive === tabItems.week"
      class="w-4/5"
      :selected="activeDate"
      :appointments="appointments"
      :events="calendarEvents"
    />
    <calendar-day
      v-show="tabActive === tabItems.day"
      class="w-4/5"
      :selected="activeDate"
      :appointments="appointments"
      :events="calendarEvents"
    />
    <!-- page side bar -->
    <div class="w-1/5 min-w-[310px]">
      <div v-if="creationStatus === creationState.hidden" class="flex flex-col gap-8">
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
            <div class="font-semibold text-lg">{{ t('heading.pendingAppointments') }}</div>
            <router-link class="px-2 py-1 border-r rounded-full bg-teal-500 text-white text-xs uppercase" :to="{ name: 'appointments' }">
              {{ t('label.viewAll') }}
            </router-link>
          </div>
          <div v-if="pendingAppointments.length === 0" class="text-slate-500 mt-4 flex flex-col gap-8 justify-center items-center">
            <div class="text-center mt-4">{{ t('info.noPendingAppointmentsInList') }}</div>
            <primary-button
              :label="t('label.createAppointments')"
              :disabled="creationStatus !== creationState.hidden"
              @click="creationStatus = creationState.details"
            />
          </div>
          <div v-else class="flex flex-col gap-8 mt-4">
            <appointment-list-item v-for="a in pendingAppointments" :key="a.id" :appointment="a" />
          </div>
        </div>
      </div>
      <!-- appointment creation dialog -->
      <appointment-creation
        v-else
        :status="creationStatus"
        :calendars="calendars"
        @start="creationStatus = creationState.details"
        @next="creationStatus = creationState.availability"
        @create="creationStatus = creationState.finished; getDbAppointments();"
        @cancel="creationStatus = creationState.hidden"
      />
    </div>
  </div>

</template>

<script setup>
import { ref, inject, computed, watch } from 'vue';
import CalendarPageHeading from '@/elements/CalendarPageHeading.vue';
import PrimaryButton from '@/elements/PrimaryButton.vue';
import AppointmentListItem from '@/elements/AppointmentListItem.vue';
import TabBar from '@/components/TabBar.vue';
import CalendarMonth from '@/components/CalendarMonth.vue';
import CalendarWeek from '@/components/CalendarWeek.vue';
import CalendarDay from '@/components/CalendarDay.vue';
import AppointmentCreation from '@/components/AppointmentCreation.vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject('dayjs');
const call = inject('call');

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

// get list of calendars from db
const calendars = ref([]);
const getDbCalendars = async () => {
  const { data } = await call("me/calendars").get().json();
  calendars.value = data.value;
};
const calendarsById = computed(() => {
  const calendarsObj = {};
  calendars.value.forEach(c => { calendarsObj[c.id] = c });
  return calendarsObj;
});

// appointment creation state
const creationState = {
  hidden: 0,
  details: 1,
  availability: 2,
  finished: 3
}
const creationStatus = ref(creationState.hidden);

// get list of appointments from db
const appointments = ref([]);
const getDbAppointments = async () => {
  const { data } = await call("me/appointments").get().json();
  appointments.value = data.value;
  // extend appointments data with calendar title and color
  appointments.value.forEach(a => {
    a.calendar_title = calendarsById.value[a.calendar_id]?.title;
    a.calendar_color = calendarsById.value[a.calendar_id]?.color;
  });
};

// get all calendar and appointments data from db
const getDbData = async () => {
  await getDbCalendars();
  await getDbAppointments();
}
getDbData();

const pendingAppointments = computed(() => {
  const pending = [];
  appointments.value.filter(a => a.status === 2).forEach(event => {
    event.slots.forEach(slot => {
      const extendedEvent = {...event, ...slot };
      delete extendedEvent.slots;
      pending.push(extendedEvent);
    });
  });
  return pending.slice(0, 4);
});

// get remote calendar data for current month
const calendarId = 5; // TODO: retrieve all configured calendars
const eventsFrom = dj(activeDate.value).startOf('month').format('YYYY-MM-DD');
const eventsTo = dj(activeDate.value).endOf('month').format('YYYY-MM-DD');
const calendarEvents = ref([]);

const getRemoteEvents = async (calendar, from, to) => {
  const { data } = await call("rmt/cal/" + calendar + "/" + from + "/" + to).get().json();
  calendarEvents.value = data.value.map(e => ({ ...e, duration: dj(e.end).diff(dj(e.start), 'minutes') }));
};
getRemoteEvents(calendarId, eventsFrom, eventsTo);

// react to user calendar navigation
watch(() => activeDate.value, (newValue, oldValue) => {
  // remote data is retrieved per month, so data request happens only if the user navigates to a different month
  if (dj(oldValue).format('M') !== dj(newValue).format('M')) {
    getRemoteEvents(
      calendarId,
      dj(newValue).startOf('month').format('YYYY-MM-DD'),
      dj(newValue).endOf('month').format('YYYY-MM-DD')
    );
  }
});
</script>
