<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  onMounted, inject, ref, computed, watch,
} from 'vue';
import { storeToRefs } from 'pinia';
import PrimaryButton from '@/tbpro/elements/PrimaryButton.vue';
import SecondaryButton from '@/tbpro/elements/SecondaryButton.vue';
import SyncCard from '@/tbpro/elements/SyncCard.vue';
import { createFTUEStore } from '@/stores/ftue-store';
import { createCalendarStore } from '@/stores/calendar-store';
import { callKey } from '@/keys';
import { CalendarItem } from '@/models';

const { t } = useI18n();

const call = inject(callKey);

const isLoading = ref(false);

const ftueStore = createFTUEStore(call);
const {
  hasNextStep, hasPreviousStep, infoMessage, warningMessage,
} = storeToRefs(ftueStore);

const calendarStore = createCalendarStore(call);
const calendars = ref<CalendarItem[]>([]);
const selectedCount = computed(() => calendars.value.filter((item) => item.checked).length);
const continueTitle = computed(() => (selectedCount.value ? t('label.continue') : t('ftue.oneCalendarRequired')));

watch(selectedCount, (val) => {
  if (val === 0) {
    warningMessage.value = {
      title: t('ftue.oneCalendarRequired'),
      details: null,
    };
  } else {
    warningMessage.value = null;
  }
});

onMounted(async () => {
  isLoading.value = true;

  infoMessage.value = {
    title: t('ftue.connectCalendarInfo'),
    details: null,
  };

  await calendarStore.fetch(true);
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
  await Promise.all(calendarKeysDisconnect.map((id) => calendarStore.disconnectCalendar(id)));
  await Promise.all(calendarKeysConnect.map((id) => calendarStore.connectCalendar(id)));

  await ftueStore.nextStep();
};

</script>

<template>
  <div class="content">
    <form class="form" autocomplete="off" autofocus @submit.prevent @keyup.enter="onSubmit">
      <sync-card class="sync-card" v-model="calendars" :title="t('label.calendar', 2)">
        <template v-slot:icon>
        <span class="icon-calendar">
          <img src="@/assets/svg/icons/calendar.svg" :alt="t('ftue.calendarIcon')" :title="t('ftue.calendarIcon')"/>
        </span>
        </template>
      </sync-card>
    </form>
  </div>
  <div class="buttons">
    <secondary-button
      class="btn-back"
      :title="t('label.back')"
      v-if="hasPreviousStep"
      :disabled="isLoading"
      @click="ftueStore.previousStep()"
    >
      {{ t('label.back') }}
    </secondary-button>
    <primary-button
      class="btn-continue"
      :aria-label="continueTitle"
      v-if="hasNextStep"
      @click="onSubmit()"
      :tooltip="!selectedCount ? t('ftue.oneCalendarRequired') : null"
      :disabled="isLoading || !selectedCount"
    >
      {{ t('label.continue') }}
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

.sync-card {
  width: 100%;
}

.form {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.buttons {
  display: flex;
  width: 100%;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
}

@media (--md) {
  .sync-card {
    width: 27.5rem;
  }

  .buttons {
    justify-content: flex-end;
    position: absolute;
    bottom: 5.75rem;
    margin: 0;
  }
}
</style>
