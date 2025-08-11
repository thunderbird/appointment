<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { callKey, dayjsKey } from '@/keys';
import { LinkButton, PrimaryButton } from '@thunderbirdops/services-ui';
import { createAvailabilityStore } from '@/stores/availability-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { useUserStore } from '@/stores/user-store';
import { deepClone } from '@/utils';
import { Alert, Availability } from '@/models';
import { DateFormatStrings, AlertSchemes } from '@/definitions';
import AlertBox from '@/elements/AlertBox.vue';

import AvailabilitySettings from './components/AvailabilitySettings/index.vue';
import BookingPageDetails from './components/BookingPageDetails/index.vue';
import BookingPageLink from './components/BookingPageLink/index.vue';

const { t } = useI18n();
const dj = inject(dayjsKey);
const call = inject(callKey);

const userStore = useUserStore();
const scheduleStore = createScheduleStore(call);
const availabilityStore = createAvailabilityStore(call);
const { currentState, isDirty } = storeToRefs(availabilityStore)

const savingInProgress = ref(false);
const validationError = ref<Alert>(null);
const saveSuccess = ref<Alert>(null);

function validateSchedule(schedule) {
  // Schedule name is empty
  if (schedule.name === '') {
    return t('error.fieldIsRequired', { field: t('label.pageName') });
  }

  // All good
  return null;
}

async function onSaveChanges() {
  savingInProgress.value = true;

  // build data object for post requestz
  const obj = deepClone({ ...currentState.value, timezone: userStore.data.settings.timezone });

  // convert local input times to utc times
  obj.start_time = scheduleStore.timeToBackendTime(obj.start_time);
  obj.end_time = scheduleStore.timeToBackendTime(obj.end_time);
  obj.availabilities?.forEach((a: Availability, i: number) => {
    obj.availabilities[i].start_time = scheduleStore.timeToBackendTime(a.start_time);
    obj.availabilities[i].end_time = scheduleStore.timeToBackendTime(a.end_time);
  });

  // Update the start_date with the current date
  obj.start_date = dj().format(DateFormatStrings.QalendarFullDay);

  // remove unwanted properties
  delete obj.time_created;
  delete obj.time_updated;

  // validate schedule data
  const validationErrorMessage = validateSchedule(obj);
  if (validationErrorMessage) {
    validationError.value = { title: validationErrorMessage };
    savingInProgress.value = false;
    window.scrollTo(0, 0);
    return;
  }

  // save schedule data
  const response = await scheduleStore.updateSchedule(obj.id, obj);

  if (Object.prototype.hasOwnProperty.call(response, 'error')) {
    // error message is in data
    validationError.value = { title: (response as unknown as Error).message };

    // go back to the start
    savingInProgress.value = false;
    window.scrollTo(0, 0);
    return;
  }

  savingInProgress.value = false;
  validationError.value = null;
  saveSuccess.value = { title: t('info.availabilitySavedSuccessfully') };

  // Reload data form backend to reset currentState vs initialState
  availabilityStore.$reset();
}

function onRevertChanges() {
  availabilityStore.revertChanges();
}
</script>

<script lang="ts">
export default {
  name: 'AvailabilityView'
}
</script>

<template>
  <h1 class="page-title">{{ t('label.availability') }}</h1>

  <alert-box
    class="alert-box"
    v-if="validationError"
    :alert="validationError"
    @close="validationError = null"
  />

  <alert-box
    class="alert-box"
    v-else-if="saveSuccess"
    :alert="saveSuccess"
    :scheme="AlertSchemes.Success"
    @close="saveSuccess = null"
  />

  <form @submit.prevent>
    <div class="page-content" :class="{ 'is-dirty': isDirty }">
      <section>
        <availability-settings />
      </section>
  
      <div class="page-content-right">
        <section>
          <booking-page-details />
        </section>
  
        <section>
          <booking-page-link />
        </section>
      </div>
    </div>

    <div class="footer-save-panel" v-if="isDirty">
      <link-button
        @click="onRevertChanges"
        :disabled="savingInProgress"
      >
        {{ t('label.revertChanges') }}
      </link-button>
      <primary-button
        @click="onSaveChanges"
        :disabled="savingInProgress"
      >
        {{ t('label.save') }}
      </primary-button>
    </div>
  </form>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-title {
  margin-block-end: 2rem;
  font-size: 2.25rem;
  font-weight: 300;
}

.page-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-block-end: 2rem;

  &.is-dirty {
    margin-block-end: 6rem;
  }
}

.alert-box {
  margin-block-end: 2rem;
}

.page-content-right {
  display: grid;
  gap: 2rem;
  align-self: start;
}

.footer-save-panel {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: flex-end;
  gap: 2rem;
  margin-inline-start: auto;
  padding: 1rem 1.5rem;
  margin: 0 0.5rem 0.5rem 0.5rem;
  border-radius: 8px;
  background-color: var(--colour-neutral-lower);
  z-index: 99;
}

section {
  border: 1px solid var(--colour-neutral-border);
  border-radius: 8px;
  padding: 1.5rem;
  align-self: flex-start;
  background-color: var(--colour-neutral-lower);
}

@media (--md) {
  .page-content {
    grid-template-columns: 1fr 1fr;
  }
}
</style>