<script setup lang="ts">
import { Dismissibles } from '@/definitions';
import {
  ref, inject, onMounted, computed,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { dayjsKey, callKey, refreshKey } from '@/keys';
import { ScheduleAppointment, TimeFormatted } from '@/models';
import ScheduleCreation from '@/components/ScheduleCreation.vue';
import CalendarQalendar from '@/components/CalendarQalendar.vue';
import NoticeBar from '@/tbpro/elements/NoticeBar.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';

// stores
import { createScheduleStore } from '@/stores/schedule-store';
import { useAppointmentStore } from '@/stores/appointment-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { useUserActivityStore } from '@/stores/user-activity-store';

const { t } = useI18n();
const route = useRoute();
const dj = inject(dayjsKey);
const call = inject(callKey);
const refresh = inject(refreshKey);

const scheduleStore = createScheduleStore(call);
const appointmentStore = useAppointmentStore();
const calendarStore = createCalendarStore(call);
const userActivityStore = useUserActivityStore();
const { schedules, firstSchedule } = storeToRefs(scheduleStore);
const { pendingAppointments } = storeToRefs(appointmentStore);
const { connectedCalendars, remoteEvents } = storeToRefs(calendarStore);
const { data: userActivityData } = storeToRefs(userActivityStore);

// current selected date, defaults to now
const activeDate = ref(dj());
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('month'),
  end: activeDate.value.endOf('month'),
}));

// user configured schedules from db (only the first for now, later multiple schedules will be available)
const schedulesReady = ref(false);

// schedule previews for showing corresponding placeholders in calendar views
const schedulesPreviews = ref([]);
const schedulePreview = (schedule: ScheduleAppointment) => {
  schedulesPreviews.value = schedule ? [schedule] : [];
};

/**
 * Retrieve new events if a user navigates to a different month
 * @param dateObj
 */
const onDateChange = async (dateObj: TimeFormatted) => {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  activeDate.value = start.add(end.diff(start, 'minutes') / 2, 'minutes');

  // remote data is retrieved per month, so a data request happens as soon as the user navigates to a different month
  if (
    !dj(activeDateRange.value.end).isSame(dj(end), 'month')
    || !dj(activeDateRange.value.start).isSame(dj(start), 'month')
  ) {
    await calendarStore.getRemoteEvents(activeDate.value);
  }
};

// initially load data when component gets remounted
onMounted(async () => {
  // Don't actually load anything during the FTUE
  if (route.name === 'setup') {
    // Setup a default schedule so the schedule creation bar works correctly...
    schedules.value = [scheduleStore.defaultSchedule];
    schedulesReady.value = true;
    return;
  }
  await refresh();
  scheduleStore.fetch();
  schedulesReady.value = true;
  await calendarStore.getRemoteEvents(activeDate.value);
});

const dismiss = () => {
  userActivityStore.dismiss(Dismissibles.BetaWarning);
};
</script>

<template>
  <notice-bar type="info" id="beta-warning" v-if="!userActivityData.dismissedBetaWarning">
    <p>{{ t('notices.betaWarning.heading') }}</p>
    <ul>
      <li>{{ t('notices.betaWarning.list.0') }}</li>
      <li>
        <i18n-t keypath="notices.betaWarning.list.1">
          <template v-slot:connectedAccounts>
            <router-link class="underline" :to="{ path: '/settings/connectedAccounts' }" target="_blank">
              {{ t('notices.betaWarning.linkText.connectedAccounts') }}
            </router-link>
          </template>
        </i18n-t>
      </li>
      <li>
        <i18n-t keypath="notices.betaWarning.list.2">
          <template v-slot:contactUs>
            <router-link class="underline" :to="{ name: 'contact' }" target="_blank">
              {{ t('notices.betaWarning.linkText.contactUs') }}
            </router-link>
          </template>
          <template v-slot:matrixChannel>
            <a class="underline" href="https://matrix.to/#/#tb-services:mozilla.org" target="_blank">
              {{ t('notices.betaWarning.linkText.matrixChannel') }}
            </a>
          </template>
        </i18n-t>
      </li>
    </ul>
    <primary-button class="dismiss" size="small" @click="dismiss">Dismiss</primary-button>
  </notice-bar>
  <!-- page title area -->
  <div class="flex select-none flex-col items-start justify-between lg:flex-row">
    <div class="text-4xl font-light">{{ t('label.dashboard') }}</div>
  </div>
  <!-- page content -->
  <div class="mt-8 flex flex-col-reverse items-stretch gap-2 md:flex-row-reverse lg:gap-4">
    <!-- schedule creation dialog -->
    <div class="z-10 mx-auto mb-10 w-3/4 min-w-80 sm:w-1/4 md:mb-0 xl:w-1/6">
      <schedule-creation
        v-if="schedulesReady"
        :calendars="connectedCalendars"
        :schedule="firstSchedule"
        :active-date="activeDate"
        @created="scheduleStore.fetch(true)"
        @updated="schedulePreview"
      />
    </div>
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-qalendar
      class="w-full md:w-9/12 xl:w-10/12"
      :appointments="pendingAppointments"
      :events="remoteEvents"
      :schedules="schedulesPreviews"
      @date-change="onDateChange"
    />
  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

#beta-warning {
  position: relative;
  /* The navbar provides margin already */
  margin: 0 0 2rem;

  :deep(.icon) {
    top: 0.75rem;
  }

  :deep(.body) {
    text-align: left;
    margin-left: 0.5rem;
    line-height: 1.5;

    a {
      text-decoration: underline;
    }

    ul {
      list-style: circle;
      margin-left: 1rem;
      font-weight: 400;
    }

    .dismiss {
      margin: 1rem auto;
    }
  }
}

@media (--md) {
  #beta-warning {
    position: relative;
    margin: 0 1rem 2rem;

    :deep(.body) {
      .dismiss {
        position: absolute;
        top: 0.75rem;
        right: 1rem;
        margin: 0;
      }
    }
  }
}
</style>
