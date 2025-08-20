<script setup lang="ts">
import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { IconArrowLeft, IconArrowRight } from '@tabler/icons-vue';
import { TimeFormatted } from '@/models';

const dj = inject(dayjsKey);

const props = defineProps<{
  onDateChange: (dateObj: TimeFormatted) => void,
  activeDateRange: {
    start: string,
    end: string
  }
}>();

const { t } = useI18n();

function onPreviousWeekButtonClicked() {
  props.onDateChange({
    start: dj(props.activeDateRange.start).subtract(7, 'day').toString(),
    end: props.activeDateRange.start,
  });
}

function onNextWeekButtonClicked() {
  props.onDateChange({
    start: props.activeDateRange.end,
    end: dj(props.activeDateRange.end).add(7, 'day').toString(),
  });
}

function onWeekPickerClicked() {
  // Not implemented, should open mini-calendar with weekly picker
}
</script>

<template>
  <div class="week-picker-container">
    <button @click="onPreviousWeekButtonClicked">
      <icon-arrow-left size="20" />
    </button>

    <button class="week-picker-button" @click="onWeekPickerClicked">
      {{ t('label.weekOf') }} {{ dj(activeDateRange.start).format('L') }} – {{ dj(activeDateRange.end).format('L') }}
    </button>

    <button @click="onNextWeekButtonClicked">
      <icon-arrow-right size="20" />
    </button>
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.week-picker-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;

  .week-picker-button {
    background-color: var(--colour-neutral-lower);
    padding: 0.25rem 1rem;
    border-radius: 18px;

    &:hover {
      background-color: var(--colour-primary-soft);
    }
  }
}

@media (--md) {
  .week-picker-container {
    justify-content: initial;
  }
}
</style>