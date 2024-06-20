<template>
  <div class="content">
    <img src="@/assets/svg/ftue-finish.svg" alt="A user icon in front of two calendars."/>
    <p>Before you close this screen, copy your shareable schedule link to start receiving appointments.</p>
    <a href="">A link goes here :)</a>
  </div>
  <div class="absolute bottom-[5.75rem] flex w-full justify-end gap-4">
    <primary-button
      class="btn-finish"
      title="Finish"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      Finish
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
const selected = computed(() => calendars.value.filter((item) => item.checked).length);
const continueTitle = computed(() => (selected.value ? 'Continue' : 'Please enable one calendar to continue'));

onMounted(async () => {
  await calendarStore.fetch(call);
  calendars.value = calendarStore.calendars.map((calendar) => ({
    key: calendar.title,
    label: calendar.title,
    checked: calendar.connected,
  }));
});

const onSubmit = async () => {
  isLoading.value = true;
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
