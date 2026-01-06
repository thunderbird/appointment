<script setup lang="ts">
import { inject, ref, useTemplateRef } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { callKey, dayjsKey } from '@/keys';
import { IconButton, LinkButton, NoticeBar, NoticeBarTypes, PrimaryButton } from '@thunderbirdops/services-ui';
import { PhX } from '@phosphor-icons/vue';
import { createAvailabilityStore } from '@/stores/availability-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { useUserStore } from '@/stores/user-store';
import { deepClone } from '@/utils';
import { Alert, Availability } from '@/models';
import { DateFormatStrings } from '@/definitions';

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
const availabilityPageForm = useTemplateRef('availability-form');

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

  // build data object for post request
  const obj = deepClone({ ...currentState.value });

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

  // Use built-in form field validations
  if (!availabilityPageForm.value.checkValidity()) {
    availabilityPageForm.value.reportValidity();
    savingInProgress.value = false;
    window.scrollTo(0, 0);
    return;
  }

  // create or update schedule data
  const response = obj.id
    ? await scheduleStore.updateSchedule(obj.id, obj)
    : await scheduleStore.createSchedule(obj);

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
  window.scrollTo(0, 0);
  saveSuccess.value = { title: t('info.availabilitySavedSuccessfully') };

  // Reload data form backend to reset currentState vs initialState
  availabilityStore.$reset();

  // Need to refresh the booking page link schedule slug
  await userStore.profile();

  availabilityStore.$patch({
    initialState: { slug: userStore.mySlug },
    currentState: { slug: userStore.mySlug }
  })
}

function clearNotices() {
  validationError.value = null;
  saveSuccess.value = null;
}

function onRevertChanges() {
  clearNotices();
  availabilityStore.revertChanges();
}
</script>

<script lang="ts">
export default {
  name: 'AvailabilityView'
}
</script>

<template>
  <div class="availability-page-container">
    <h1
      class="page-title"
      :class="{ 'isDirty': isDirty }"
    >
      {{ t('label.availability') }}
    </h1>
  
    <notice-bar
      v-if="isDirty"
      :type="NoticeBarTypes.Warning"
      class="notice-bar"
    >
      {{ t('label.youHaveUnsavedChanges') }}

      <template #cta>
        <link-button
          @click="onRevertChanges"
          :disabled="savingInProgress"
        >
          {{ t('label.revertChanges') }}
        </link-button>
        <primary-button
          @click="onSaveChanges"
          :disabled="savingInProgress"
          size="small"
        >
          {{ t('label.saveChanges') }}
        </primary-button>
      </template>
    </notice-bar>

    <notice-bar
      v-else-if="validationError"
      :type="NoticeBarTypes.Critical"
      class="notice-bar"
    >
      {{ validationError.title }}

      <template #cta>
        <icon-button
          @click="clearNotices"
          :title="t('label.close')"
          class="btn-close"
        >
          <ph-x />
        </icon-button>
      </template>
    </notice-bar>
  
    <notice-bar
      v-else-if="saveSuccess"
      :type="NoticeBarTypes.Success"
      class="notice-bar"
    >
      {{ saveSuccess.title }}

      <template #cta>
        <icon-button
          @click="clearNotices"
          :title="t('label.close')"
          class="btn-close"
        >
          <ph-x />
        </icon-button>
      </template>
    </notice-bar>
  
    <form ref="availability-form" @submit.prevent>
      <div class="page-content">
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
    </form>

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
        {{ t('label.saveChanges') }}
      </primary-button>
    </div>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.page-title {
  margin-block-end: 2rem;
  font-family: metropolis;
  font-size: 2.25rem;
  color: var(--colour-ti-base);

  &.isDirty {
    margin-block-end: 1.5rem;
  }
}

.notice-bar {
  margin-block-end: 2rem;
  position: sticky;
  top: 5rem;
  z-index: 50;

  .btn-close {
    height: 2.375rem;
    width: 2.375rem;
  }
}

.page-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-block-end: 2rem;
}

.page-content-right {
  display: grid;
  gap: 2rem;
  align-self: start;
}

.footer-save-panel {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  margin-block-end: 2rem;
}

section {
  border-radius: 8px;
  padding: 2rem 1.5rem;
  align-self: flex-start;
  background-color: var(--colour-neutral-base);
  box-shadow: 4px 4px 16px 0 rgba(0, 0, 0, 0.04);
  border-radius: 1.5rem;
}

@media (--md) {
  .availability-page-container {
    width: 100%;
    max-width: 969px;
    margin: 0 auto;
  }
}
</style>