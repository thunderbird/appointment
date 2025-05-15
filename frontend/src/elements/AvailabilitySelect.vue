<script setup lang="ts">
import { inject, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { Availability, AvailabilitySet, SelectOption } from '@/models';
import TextInput from '@/tbpro/elements/TextInput.vue';
import { isoWeekdaysKey } from '@/keys';

const { t } = useI18n();
const isoWeekdays = inject(isoWeekdaysKey);

// component properties
interface Props {
  options: SelectOption[];
  availabilities: Availability[];
  required: boolean;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
});

const emit = defineEmits(['update']);

// Model for weekday selection
const model = defineModel<(string | number)[]>({ default: [] });

// We create a set of availabilities, grouped by day of week. This ensures that we have every day of week available
// and that existing availabilities are prefilled for the corresponding day.
const defaultAvailabilities = Object.fromEntries(isoWeekdays.map((d) => {
  const existingAvailability = props.availabilities.find((a) => a.day_of_week === d.iso);
  return [d.iso, [existingAvailability ?? { day_of_week: d.iso, start_time: '', end_time: '' } as Availability]];
})) as AvailabilitySet;

// Model for availability data
const customAvailabilities = ref(defaultAvailabilities);

/**
 * True if the given option is currently selected/active
 */
const isSelectedOption = (option: SelectOption): boolean => {
  return model.value.indexOf(option.value) > -1;
};

/**
 * Adds or removes the option value from the model.
 * There's probably a better way to do this lol!
 * @param option
 */
const toggleBubble = (option: SelectOption) => {
  // Detect what our current state is
  const val = model.value.indexOf(option.value);

  if (val > -1) {
    // We have the value, so filter it out
    model.value = model.value.filter((value) => option.value !== value);
  } else {
    // We don't have the value, so mix it in
    model.value = [
      ...model.value,
      option.value,
    ];
  }

  // Sort for niceness
  model.value.sort();
};

const update = () => {
  emit('update', customAvailabilities.value);
};
</script>

<template>
  <div class="wrapper">
    <label>
      <span class="label">
        <slot/>
        <span v-if="required && model?.length === 0" class="required">*</span>
      </span>
    </label>
    <div class="bubble-list">
      <template v-for="option in options" :key="option.value">
        <button
          class="tbpro-bubble"
          :aria-pressed="isSelectedOption(option)"
          :class="{
            'selected': isSelectedOption(option),
            disabled,
          }"
          :title="option.label ?? String(option.value)"
          type="button"
          @click="() => !disabled ? toggleBubble(option) : null"
        >
          {{ option.label }}
        </button>
        <div v-if="isSelectedOption(option)" class="bubble-content">
          <text-input
            type="time"
            :name="`start_time_${option.value}`"
            v-model="customAvailabilities[option.value][0].start_time"
            :disabled="disabled"
            @blur="update"
          />
          <span>&ndash;</span>
          <text-input
            type="time"
            :name="`end_time_${option.value}`"
            v-model="customAvailabilities[option.value][0].end_time"
            :disabled="disabled"
            @blur="update"
          />
        </div>
        <div v-else>{{ t('label.unavailable') }}</div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  color: var(--colour-ti-base);
  font-family: 'Inter', 'sans-serif';
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  font-weight: 400;
}

.bubble-list {
  padding: 0;
  display: grid;
  grid-template-columns: 2rem auto;
  row-gap: .25rem;
  column-gap: .5rem;
  align-items: center;
}

.label {
  width: 100%;
  font-weight: 600;
}

.tbpro-bubble {
  transition: all 250ms ease-out;

  display: flex;
  justify-content: center;
  align-items: center;
  align-self: flex-start;

  width: 2rem;
  height: 2rem;
  border: 0.0625rem solid var(--colour-neutral-border);
  border-radius: 100%;
  background-color: var(--colour-neutral-subtle);
  font-weight: 700;
  line-height: 150%;
  color: var(--colour-ti-muted);
}
.selected {
  background-color: var(--colour-service-primary);
  border-color: var(--colour-service-primary-pressed);
  color: var(--colour-neutral-base);
}
.required {
  color: var(--colour-ti-critical);
}
.disabled {
  cursor: default;
}
.selected.disabled {
  background-color: var(--colour-neutral-border);
  border-color: var(--colour-ti-muted);
  color: var(--colour-ti-muted);
}

.bubble-content {
  display: flex;
  align-items: center;
  gap: .5rem;
}
</style>
