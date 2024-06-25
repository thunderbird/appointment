<template>
  <div class="content">
    <img src="@/assets/svg/ftue-finish.svg" alt="A user icon in front of two calendars."/>
    <div class="copy">
    <p>Before you close this screen, copy your shareable schedule link to start receiving appointments.</p>
    <text-button class="link" :copy="myLink" :label="myLink"/>
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
  onMounted, inject, ref,
} from 'vue';
import { useFTUEStore } from '@/stores/ftue-store';
import { useScheduleStore } from '@/stores/schedule-store';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import { useUserStore } from '@/stores/user-store';
import TextButton from '@/elements/TextButton.vue';

const { t } = useI18n();
const call = inject('call');

const scheduleStore = useScheduleStore();
const userStore = useUserStore();
const ftueStore = useFTUEStore();
const { nextStep } = ftueStore;

const isLoading = ref(false);
const myLink = ref('');

onMounted(async () => {
  await Promise.all([
    scheduleStore.fetch(call),
    userStore.profile(call),
  ]);
  myLink.value = userStore.myLink;
});

const onSubmit = async () => {
  isLoading.value = true;

  await userStore.finishFTUE(call);
  await nextStep();
  // Yeet them to calendar!
  window.location = '/calendar';
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
  border: none;
  &:hover {
    background-color: initial !important;
    box-shadow: none !important;
  }
}
</style>
