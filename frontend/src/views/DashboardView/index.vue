<script setup lang="ts">
import { Dismissibles } from '@/definitions';
import {
  ref, inject, onMounted, computed,
} from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { dayjsKey, callKey, refreshKey } from '@/keys';
import { TimeFormatted } from '@/models';
import CalendarQalendar from '@/components/CalendarQalendar.vue';
import { PrimaryButton, NoticeBar, NoticeBarTypes } from '@thunderbirdops/services-ui';
import QuickActionsSideBar from './components/QuickActionsSideBar.vue';
import WeekPicker from './components/WeekPicker.vue';
import UserCalendarSync from './components/UserCalendarSync.vue';

// stores
import { useAppointmentStore } from '@/stores/appointment-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { useUserActivityStore } from '@/stores/user-activity-store';

const { t } = useI18n({ useScope: 'global' });
const route = useRoute();
const dj = inject(dayjsKey);
const call = inject(callKey);
const refresh = inject(refreshKey);

const appointmentStore = useAppointmentStore();
const calendarStore = createCalendarStore(call);
const userActivityStore = useUserActivityStore();
const { pendingAppointments } = storeToRefs(appointmentStore);
const { remoteEvents } = storeToRefs(calendarStore);
const { data: userActivityData } = storeToRefs(userActivityStore);

// current selected date, defaults to now
const activeDate = ref(dj());
const activeDateRange = computed(() => ({
  start: activeDate.value.startOf('week').format('L'),
  end: activeDate.value.endOf('week').format('L'),
}));

// schedule previews for showing corresponding placeholders in calendar views
const schedulesPreviews = ref([]);

/**
 * Retrieve new events if a user navigates to a different month
 * @param dateObj
 */
const onDateChange = async (dateObj: TimeFormatted) => {
  const start = dj(dateObj.start);
  const end = dj(dateObj.end);

  activeDate.value = start.add(end.diff(start, 'minutes') / 2, 'minutes');

  // remote data is retrieved per month, so a data request happens as soon as the user navigates to a different month
  // if (
  //   !dj(activeDateRange.value.end).isSame(dj(end), 'month')
  //   || !dj(activeDateRange.value.start).isSame(dj(start), 'month')
  // ) {
  //   await calendarStore.getRemoteEvents(activeDate.value);
  // }
};

// initially load data when component gets remounted
onMounted(async () => {
  // Don't actually load anything during the FTUE
  if (route.name === 'setup') {
    return;
  }

  await refresh();
  await calendarStore.getRemoteEvents(activeDate.value);
});

const dismiss = () => {
  userActivityStore.dismiss(Dismissibles.BetaWarning);
};
</script>

<script lang="ts">
export default {
  name: 'DashboardView'
}
</script>

<template>
  <notice-bar :type="NoticeBarTypes.Info" id="beta-warning" v-if="!userActivityData.dismissedBetaWarning">
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

  <div class="main-container">
    <quick-actions-side-bar />
  
    <div class="w-full">
      <div class="calendar-header-container">
        <week-picker
          :active-date-range="activeDateRange"
          :onDateChange="onDateChange"
        />

        <user-calendar-sync />
      </div>

      <!-- main section: big calendar showing active month, week or day -->
      <calendar-qalendar
        :appointments="pendingAppointments"
        :events="remoteEvents"
        :schedules="schedulesPreviews"
        @date-change="onDateChange"
      />
    </div>
  </div>
</template>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.main-container {
  display: flex;
  flex-direction: column;
  gap: 2.25rem;
}

.calendar-header-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  margin-block-end: 1rem;
  gap: 2rem;
}

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

    .underline {
      text-decoration-line: underline;
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

  .main-container {
    flex-direction: row;
    gap: 2rem;
  }

  .calendar-header-container {
    flex-direction: row;
    justify-content: space-between;
    margin-block-end: 1rem;
    gap: 0;
  }
}
</style>
