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
      <tab-bar :tab-items="calendarViews" :active="tabActive" @update="updateTab" class="text-xl" />
      <primary-button
        :label="t('label.createAppointments')"
        :disabled="creationStatus !== creationState.hidden"
        @click="creationStatus = creationState.details"
      />
    </div>
  </div>
  <!-- page content -->
  <div class="flex justify-between gap-24 mt-8 min-h-[767px] items-stretch" :class="{ 'mt-[60px]': tabActive === calendarViews.month }">
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-month
      v-show="tabActive === calendarViews.month"
      class="w-4/5"
      :selected="activeDate"
      :appointments="appointments"
      :events="calendarEvents"
    />
    <calendar-week
      v-show="tabActive === calendarViews.week"
      class="w-4/5"
      :selected="activeDate"
      :appointments="appointments"
      :events="calendarEvents"
    />
    <calendar-day
      v-show="tabActive === calendarViews.day"
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
        @create="creationStatus = creationState.finished; refreshAppointments();"
        @cancel="creationStatus = creationState.hidden"
      />
    </div>
  </div>

</template>

<script setup>
import { ref, inject, computed, watch, onMounted } from 'vue';
import { creationState, calendarViews } from '@/definitions';
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
const refreshAppointments = inject('refreshAppointments');

// view properties
const props = defineProps({
  calendars: Array,    // list of calendars from db
  appointments: Array, // list of appointments from db
});

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

// active menu item for tab navigation of calendar views
const tabActive = ref(calendarViews[route.params.view]);
const updateTab = view => {
  router.replace({ name: route.name, params: { view: view, date: route.params.date ?? dj().format('YYYY-MM-DD') } });
  tabActive.value = calendarViews[view];
};

// calculate page title
const pageTitle = computed(() => {
  switch (tabActive.value) {
    case calendarViews.day:
      return activeDate.value.format('dddd Do');
    case calendarViews.week:
      return startOfActiveWeek.value.format('ddd Do') + ' - ' + endOfActiveWeek.value.format('ddd Do');
    case calendarViews.month:
    default:
      return ''
  }
});

// date navigation
const dateNav = (unit = 'auto', forward = true) => {
  if (unit === 'auto') {
    unit = Object.keys(calendarViews).find(key => calendarViews[key] === tabActive.value);
  }
  if (forward) {
    selectDate(activeDate.value.add(1, unit));
  } else {
    selectDate(activeDate.value.subtract(1, unit));
  }
};

// appointment creation state
const creationStatus = ref(creationState.hidden);

// list of all pending appointments
const pendingAppointments = computed(() => {
  const pending = [];
  props.appointments.filter(a => a.status === 2).forEach(event => {
    event.slots.forEach(slot => {
      const extendedEvent = {...event, ...slot };
      delete extendedEvent.slots;
      pending.push(extendedEvent);
    });
  });
  return pending.filter(a => dj(a.start) > dj()).slice(0, 4);
});

// get remote calendar data for current month
const calendarId     = 5; // TODO: retrieve all configured calendars
const eventsFrom     = dj(activeDate.value).startOf('month').format('YYYY-MM-DD');
const eventsTo       = dj(activeDate.value).endOf('month').format('YYYY-MM-DD');
const calendarEvents = ref([]);

const getRemoteEvents = async (calendar, from, to) => {
  const { data } = await call("rmt/cal/" + calendar + "/" + from + "/" + to).get().json();
  calendarEvents.value = data.value.map(e => ({ ...e, duration: dj(e.end).diff(dj(e.start), 'minutes') }));
};

onMounted(() => {
  refreshAppointments();
  getRemoteEvents(calendarId, eventsFrom, eventsTo);
});

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
