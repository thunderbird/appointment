<script setup lang="ts">
import { inject, ref, onMounted, watch, nextTick, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { Alert, Availability, AvailabilitySet, CopyTemplate, SelectOption } from '@/models';
import { isoWeekdaysKey, dayjsKey } from '@/keys';
import { compareAvailabilityStart, deepClone, hhmmToMinutes } from '@/utils';
import { DEFAULT_SLOT_DURATION } from '@/definitions';
import AlertBox from '@/elements/AlertBox.vue';
import AvailabilityCopyDropdown from '@/elements/AvailabilityCopyDropdown.vue';
import TextInput from '@/tbpro/elements/TextInput.vue';
import LinkButton from '@/tbpro/elements/LinkButton.vue';

// icons
import { IconPlus, IconX } from '@tabler/icons-vue';

const { t } = useI18n();
const isoWeekdays = inject(isoWeekdaysKey);
const dj = inject(dayjsKey);

// component properties
interface Props {
  options: SelectOption[];
  availabilities: Availability[]; // Existing availability entries to prefill
  startTime: string; // Default start time for new availability
  endTime: string; // Default end time for new availability
  slotDuration: number;
  required: boolean;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  slotDuration: DEFAULT_SLOT_DURATION,
  required: false,
  disabled: false,
});

const emit = defineEmits(['update']);

// Model for weekday selection
const model = defineModel<number[]>({ default: [] });

// Model for availability data
const defaultAvailability = (dayOfWeek: number) => (
  { day_of_week: dayOfWeek, start_time: props.startTime, end_time: props.endTime } as Availability
);
const initialAvailabilitySet = Object.fromEntries(
  isoWeekdays.map((d) => [d.iso, [defaultAvailability(d.iso)]]
));
const availabilitySet = ref<AvailabilitySet>(initialAvailabilitySet);
const validationErrors = ref<string[]>(Array.from({length: props.options.length}, () => null));
const validationErrorsExist = computed(() => validationErrors.value.some(e => e === ''));
const durationHumanized = computed(() => dj.duration(props.slotDuration, "minutes").humanize());
const validationAlert = { title: t('error.endAfterStartTime', { value: durationHumanized.value }) } as Alert;
/**
 * We create a set of availabilities, grouped by day of week. This ensures that we have every day of week available
 * and that existing availabilities are prefilled for the corresponding day.
 */
const defaultAvailabilitySet = () => Object.fromEntries(isoWeekdays.map((d) => {
  const existing = props.availabilities.filter((a) => a.day_of_week === d.iso);
  return [d.iso, existing.length ? existing.sort(compareAvailabilityStart) : [defaultAvailability(d.iso)]];
})) as AvailabilitySet;

// Prefill existing availabilities from schedule
onMounted(() => {
  availabilitySet.value = defaultAvailabilitySet();
});

// Track schedule reset
watch(
  () => props.availabilities,
  () => {
    availabilitySet.value = defaultAvailabilitySet();
  },
);

/**
 * Returns true, if validation was successful.
 */
const validateInput = () => {
  let success = true;
  Object.values(availabilitySet.value).forEach((s) => {
    // Validate each availability entry on each set
    s.forEach((a) => {
      // Only validate active weekdays
      if (model.value.includes(a.day_of_week)) {
        const diff = hhmmToMinutes(a.end_time) - hhmmToMinutes(a.start_time);
        if (diff < props.slotDuration) {
          // We just use an empty string here to indicate an error on the input field
          // without adding an error message beneath it.
          validationErrors.value[a.day_of_week] = '';
          success = false;
        } else {
          validationErrors.value[a.day_of_week] = null;
        }
      }
    });
  });
  return success;
};

/**
 * Send a list of valid availabilities from our input AvailabilitySet
 * Update is only emitted if input data is successfully validated
 */
const update = () => {
  if (validateInput()) {
    const list = Object.values(availabilitySet.value).flat().filter((a) => model.value.includes(a.day_of_week));
    emit('update', list);
  }
};

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

  // Send availability update
  nextTick(() => update());
};

/**
 * Initializes a new availability entry on given day of week
 * @param option The weekday the availability should be added to
 */
const addAvailability = (option: SelectOption) => {
  availabilitySet.value[option.value].push(defaultAvailability(option.value));
  update();
};

/**
 * Copies all availability entries on given day of week to selected days
 * @param option The weekday's availability that should be used as copy source
 * @param template The weekdays that should receive the copied availability
 */
const copyAvailability = (option: SelectOption, template: CopyTemplate) => {
  const sourceAvailabilities = availabilitySet.value[option.value];
  const targetWeekdays = Object.entries(template).reduce((p, c) => {
    if (c[1]) p.push(Number(c[0]));
    return p;
  }, [] as number[]);
  
  targetWeekdays.forEach((d) => {
    const targetAvailabilities = [] as Availability[];
    sourceAvailabilities.forEach((sa) => {
      const ta = deepClone(sa) as Availability;
      ta.day_of_week = d;
      delete ta.id;
      targetAvailabilities.push(ta);
    });
    
    availabilitySet.value[d] = targetAvailabilities;
  });
  update();
};

/**
 * Initializes a new availability entry on given day of week
 * @param option The weekday the availability should be added to
 * @param index The index of the availability on that weekday
 */
const removeAvailability = (option: SelectOption, index: number) => {
  if (availabilitySet.value[option.value].length <= 1) {
    // There is only one entry left, so disable the whole day
    toggleBubble(option);
  } else {
    // We have more than one entry, so just remove the element at the given index
    availabilitySet.value[option.value].splice(index, 1);
    update();
  }
};


</script>

<template>
  <div class="wrapper">
    <alert-box v-if="validationErrorsExist" :alert="validationAlert" :can-close="false" />
    <div class="bubble-list">
      <template v-for="option in options" :key="option.value">
        <button
          class="tbpro-bubble"
          type="button"
          :aria-pressed="isSelectedOption(option)"
          :class="{ 'selected': isSelectedOption(option), disabled }"
          :title="option.label ?? String(option.value)"
          @click="() => !disabled ? toggleBubble(option) : null"
        >
          {{ option.label }}
        </button>
        <div v-if="isSelectedOption(option)" class="bubble-content">
          <div v-for="(availability, i) in availabilitySet[option.value]" :key="availability.start_time">
            <text-input
              type="time"
              :name="`start_time_${option.value}`"
              v-model="availability.start_time"
              :error="validationErrors[option.value]"
              :disabled="disabled"
              :small-input="true"
              @blur="update"
            />
            <span>&ndash;</span>
            <text-input
              type="time"
              :name="`end_time_${option.value}`"
              v-model="availability.end_time"
              :error="validationErrors[option.value]"
              :disabled="disabled"
              :small-input="true"
              @blur="update"
            />
            <span>
              <link-button v-if="i === 0" size="small" class="action-btn" @click="addAvailability(option)">
                <icon-plus class="w-5" aria-hidden="true"/>
              </link-button>
            </span>
            <span>
              <availability-copy-dropdown
                v-if="i === 0"
                :disabled-weekdays="[option.value]"
                @copy="event => copyAvailability(option, event)"
              />
            </span>
            <span>
              <link-button size="small" class="action-btn action-remove" @click="removeAvailability(option, i)">
                <icon-x class="w-4" aria-hidden="true"/>
              </link-button>
            </span>
          </div>
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

.alert {
  margin-bottom: .5rem;
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
  flex-direction: column;
  gap: .25rem;

  & > div {
    display: grid;
    grid-template-columns: 1fr auto 1fr repeat(3, 20px);
    align-items: center;
    gap: .5rem;
  
    .action-btn {
      padding: .25rem .125rem;
    }
    .action-remove {
      opacity: 0;
      color: var(--colour-danger-default);
      transition: var(--transition-opacity);
    }
    &:hover .action-remove {
      opacity: 1;
    }
  }
}
</style>
