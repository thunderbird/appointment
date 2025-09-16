<script setup lang="ts">
import { inject, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { dayjsKey } from '@/keys';
import { PhCaretLeft, PhCaretRight } from '@phosphor-icons/vue';
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

// Hidden date input ref
const dateInputRef = ref<HTMLInputElement>();

// Computed values for accessibility
const currentWeekLabel = computed(() => {
  const startDate = dj(props.activeDateRange.start).format('L');
  const endDate = dj(props.activeDateRange.end).format('L');
  return startDate + ' – ' + endDate;
});

const previousWeekLabel = computed(() => {
  const prevStart = dj(props.activeDateRange.start).subtract(7, 'day').format('L');
  const prevEnd = dj(props.activeDateRange.start).subtract(1, 'day').format('L');
  return t('label.previousWeek') + ': ' + prevStart + ' – ' + prevEnd;
});

const nextWeekLabel = computed(() => {
  const nextStart = dj(props.activeDateRange.end).add(1, 'day').format('L');
  const nextEnd = dj(props.activeDateRange.end).add(7, 'day').format('L');
  return t('label.nextWeek') + ': ' + nextStart + ' – ' + nextEnd;
});

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
  // Trigger the native date picker
  dateInputRef.value?.showPicker();
}

function onDateSelected(event: Event) {
  const target = event.target as HTMLInputElement;

  if (target.value) {
    const selectedDate = dj(target.value);
    const startOfWeek = selectedDate.startOf('week');
    const endOfWeek = selectedDate.endOf('week');

    props.onDateChange({
      start: startOfWeek.format('YYYY-MM-DD'),
      end: endOfWeek.format('YYYY-MM-DD'),
    });
  }
}

// Handle keyboard navigation
function onKeyDown(event: KeyboardEvent) {
  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault();
      onPreviousWeekButtonClicked();
      break;
    case 'ArrowRight':
      event.preventDefault();
      onNextWeekButtonClicked();
      break;
    case 'Enter':
    case ' ':
      event.preventDefault();
      onWeekPickerClicked();
      break;
  }
}
</script>

<template>
  <div
    class="week-picker-container"
    role="group"
    :aria-label="t('label.weekPicker')"
    tabindex="0"
    @keydown="onKeyDown"
  >
    <button
      @click="onPreviousWeekButtonClicked"
      :aria-label="previousWeekLabel"
      :title="previousWeekLabel"
    >
      <ph-caret-left size="24" />
      <span class="screen-reader-only">{{ t('label.previousWeek') }}</span>
    </button>

    <button
      class="week-picker-button" 
      @click="onWeekPickerClicked"
      :aria-label="t('label.selectWeek') + ': ' + currentWeekLabel"
      :title="t('label.selectWeek')"
    >
      {{ dj(activeDateRange.start).format('MMMM DD') }} – {{ dj(activeDateRange.end).format('MMMM DD') }}
    </button>

    <button
      @click="onNextWeekButtonClicked"
      :aria-label="nextWeekLabel"
      :title="nextWeekLabel"
    >
      <ph-caret-right size="24" />
      <span class="screen-reader-only">{{ t('label.nextWeek') }}</span>
    </button>

    <!-- Date input for native date picker -->
    <input
      ref="dateInputRef"
      type="date"
      :value="activeDateRange.start"
      @change="onDateSelected"
      class="screen-reader-only"
      :aria-label="t('label.selectDateForWeek')"
      :title="t('label.selectDateForWeek')"
    />
  </div>
</template>

<style scoped>
@import '@/assets/styles/custom-media.pcss';

.week-picker-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  width: auto;
  outline: none;
  color: var(--colour-ti-secondary);

  &:focus-visible {
    outline: 2px solid var(--colour-primary);
    outline-offset: 2px;
    border-radius: 8px;
  }

  .week-picker-button {
    font-family: metropolis;
    font-size: 1rem;
    text-wrap: wrap;
    border-radius: 18px;
    padding-inline: 0.5rem;

    &:hover {
      background-color: var(--colour-primary-soft);
    }

    &:focus-visible {
      outline: 2px solid var(--colour-primary);
      outline-offset: 2px;
    }
  }
}

@media (--md) {
  .week-picker-container {
    justify-content: initial;

    .week-picker-button {
      font-size: 1.5rem;
      text-wrap: nowrap;
    }
  }
}
</style>