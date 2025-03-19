<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { onMounted, inject, ref } from 'vue';
import { createFTUEStore } from '@/stores/ftue-store';
import { createScheduleStore } from '@/stores/schedule-store';
import { createUserStore } from '@/stores/user-store';
import { callKey } from '@/keys';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import LinkButton from '@/tbpro/elements/LinkButton.vue';
import CopyIcon from '@/tbpro/icons/CopyIcon.vue';

const { t } = useI18n();
const call = inject(callKey);

const scheduleStore = createScheduleStore(call);
const userStore = createUserStore(call);
const ftueStore = createFTUEStore(call);

const isLoading = ref(false);
const myLink = ref('');
const myLinkTooltip = ref(t('label.copyLink'));
const myLinkShow = ref(false);

onMounted(async () => {
  await Promise.all([
    scheduleStore.fetch(),
    userStore.profile(),
  ]);
  myLink.value = userStore.myLink;
});

const onSubmit = async () => {
  isLoading.value = true;

  // Can't run async together!
  await userStore.finishFTUE();
  await userStore.profile();

  // Clear the FTUE flow
  window.localStorage?.removeItem('tba/ftue');

  await ftueStore.nextStep();
  // Yeet them to calendar!
  window.location.href = '/calendar';
};

const copyLink = async () => {
  await navigator.clipboard.writeText(myLink.value);

  myLinkShow.value = true;
  myLinkTooltip.value = t('info.copiedToClipboard');

  // Fade out after a bit
  setTimeout(() => {
    myLinkShow.value = false;

    // After the animation fades...
    setTimeout(() => {
      myLinkTooltip.value = t('label.copyLink');
    }, 500);
  }, 4000);
};
</script>

<template>
  <div class="content">
    <img class="is-dark-mode" src="@/assets/svg/ftue-finish-dark.svg" :alt="t('ftue.finishAltText')"/>
    <img class="is-light-mode" src="@/assets/svg/ftue-finish.svg" :alt="t('ftue.finishAltText')"/>
    <div class="copy">
      <p>{{ t('ftue.finishScreenText') }}</p>
      <link-button class="my-link-btn" @click="copyLink" :tooltip="myLinkTooltip" :force-tooltip="myLinkShow">
        <template v-slot:icon>
          <copy-icon/>
        </template>
        {{ myLink }}
      </link-button>
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

.my-link-btn {
  flex-direction: row-reverse;
}

.link {
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
  .content {
    margin-top: -6rem;
    gap: 0;
  }
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
