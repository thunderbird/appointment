<template>
  <div class="content">
    <InfoBar>
      Connect your calendars to manage your availability
    </InfoBar>
    <SyncCard class="sync-card" v-model="calendars" title="Calendars">
      <template v-slot:icon>
        <span class="icon-calendar">
          <img src="@/assets/svg/icons/calendar.svg" alt="calendar"/>
        </span>
      </template>
    </SyncCard>
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
      title="Continue"
      v-if="hasNextStep"
      @click="onSubmit()"
      :disabled="isLoading"
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
import InfoBar from '@/elements/InfoBar.vue';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SyncCard from '@/tbpro/elements/SyncCard.vue';

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

onMounted(async () => {
  await calendarStore.fetch(call);
  calendars.value = calendarStore.calendars.map((calendar) => ({
    key: calendar.title,
    label: calendar.title,
    checked: calendar.connected,
  }));
  console.log(calendarStore.calendars);
});

const onSubmit = async () => {
  // await nextStep();
};

</script>
<style scoped>
.content {
  display: flex;
  flex-direction: column;
  gap: 3.125rem;
  width: 100%;
  justify-content: center;
  align-items: center;

}
.sync-card {
  width: 27.5rem;
}
.google-calendar-logo {
  display: inline-block;
  background-image: url('@/assets/svg/google-calendar-logo.svg');
  width: 1.625rem;
  height: 1.625rem;
}
</style>
