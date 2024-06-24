<template>
  <div class="content">
    <img src="@/assets/svg/ftue-finish.svg" alt="A user icon in front of two calendars."/>
    <div class="copy">
    <p>Before you close this screen, copy your shareable schedule link to start receiving appointments.</p>
    <a class="link" :href="myLink">{{ myLink }}</a>
    </div>
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
import { useFTUEStore } from '@/stores/ftue-store';
import { useCalendarStore } from '@/stores/calendar-store';
import { useScheduleStore } from '@/stores/schedule-store';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import { useUserStore } from '@/stores/user-store';

const { t } = useI18n();

const call = inject('call');

const isLoading = ref(false);

const userStore = useUserStore();

const ftueStore = useFTUEStore();

const myLink = ref('');
const { nextStep } = ftueStore;

const scheduleStore = useScheduleStore();

onMounted(async () => {
  await scheduleStore.fetch(call);
  myLink.value = userStore.myLink;
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

.copy {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 60%;
  font-size: 0.8125rem;
  text-align: center;
}

.link {
  color: var(--tbpro-primary);
  text-decoration: underline;
}
</style>
