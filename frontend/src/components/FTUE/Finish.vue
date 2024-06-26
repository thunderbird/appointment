<template>
  <div class="content">
    <img src="@/assets/svg/ftue-finish.svg" :alt="t('ftue.finishAltText')"/>
    <div class="copy">
      <p>{{ t('ftue.finishScreenText') }}</p>
      <text-button class="link" :copy="myLink" :label="myLink"/>
    </div>
  </div>
  <div class="buttons">
    <primary-button
      class="btn-finish"
      :title="t('ftue.finish')"
      @click="onSubmit()"
      :disabled="isLoading"
    >
      {{ t('ftue.finish') }}
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

  // Can't run async together!
  await userStore.finishFTUE(call);
  await userStore.profile(call);

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

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .copy {
    width: 60%;
  }

  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
