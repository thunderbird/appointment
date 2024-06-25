<template>
  <div class="content">
    <notice-bar>
      Connect your calendars to manage your availability
    </notice-bar>
    <form autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
    <sync-card class="sync-card" v-model="calendars" title="Calendars">
      <template v-slot:icon>
        <span class="icon-calendar">
          <img src="@/assets/svg/icons/calendar.svg" alt="calendar icon" title="calendar icon"/>
        </span>
      </template>
    </sync-card>
    </form>
  </div>
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <secondary-button
      class="btn-back"
      title="Back"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="previousStep()"
    >Back
    </secondary-button>
    <primary-button
      class="btn-continue"
      :title="continueTitle"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading || !selected"
    >
      Continue
    </primary-button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import {
  onMounted, inject, ref, computed,
} from 'vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SyncCard from '@/tbpro/elements/SyncCard.vue';
import NoticeBar from '@/tbpro/elements/NoticeBar.vue';

const { t } = useI18n();

const call = inject('call');

const isLoading = ref(false);

const ftueStore = useFTUEStore();
const {
  hasNextStep, hasPreviousStep,
} = storeToRefs(ftueStore);
const { previousStep, nextStep } = ftueStore;

const calendarStore = useCalendarStore();
const calendars = ref([]);
const selected = computed(() => calendars.value.filter((item) => item.checked).length);
const continueTitle = computed(() => (selected.value ? 'Continue' : 'Please enable one calendar to continue'));

onMounted(async () => {
  isLoading.value = true;
  await calendarStore.fetch(call, true);
  calendars.value = calendarStore.calendars.map((calendar) => ({
    key: calendar.id,
    label: calendar.title,
    checked: calendar.connected,
  }));
  isLoading.value = false;
});

const onSubmit = async () => {
  isLoading.value = true;

  // FIXME: This is just lazy, we should be checking for checkbox dirty state but no one really should have a calendar connected here!
  const calendarKeysConnect = calendars.value.filter((calendar) => calendar.checked).map((calendar) => calendar.key);
  const calendarKeysDisconnect = calendars.value.filter((calendar) => !calendar.checked).map((calendar) => calendar.key);
  await Promise.all(calendarKeysDisconnect.map((id) => calendarStore.disconnectCalendar(call, id)));
  await Promise.all(calendarKeysConnect.map((id) => calendarStore.connectCalendar(call, id)));

  await nextStep();
};

</script>
<style scoped>
@import '@/assets/styles/custom-media.pcss';

.content {
  display: flex;
  flex-direction: column;
  gap: 3.125rem;
  width: 100%;
  justify-content: center;
  align-items: center;

}
.sync-card {
  width: 100%;
}

@media (--md) {
  .sync-card {
    width: 27.5rem;
  }
}
</style>
