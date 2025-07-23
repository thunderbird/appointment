<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { vOnClickOutside } from '@vueuse/components';
import { useI18n } from 'vue-i18n';
import { IconChevronDown } from '@tabler/icons-vue';
import { SelectOption } from '@/models';
import { BookingStatus } from '@/definitions';
import FadeInOutTransition from '@/components/FadeInOutTransition.vue';
import { CheckboxInput } from '@thunderbirdops/services-ui';

import {
  BOOKING_STATUS_TO_FILTER_QUERY_PARAM,
  FILTER_QUERY_PARAM_TO_BOOKING_STATUS
} from "../constants"

interface Props {
  selected: string[];
}

const { t } = useI18n();
const props = defineProps<Props>();
const emit = defineEmits(['update:selected']);

const filterOptions = [
  { value: BookingStatus.Requested, label: t('label.pending') },
  { value: BookingStatus.Booked, label: t('label.confirmed') },
  { value: BookingStatus.Declined, label: t('label.declined') },
  { value: BookingStatus.Cancelled, label: t('label.cancelled') },
];

const isOpen = ref(false);
const checkboxStates = ref<Record<string, boolean>>({});

// Initialize checkbox states based on selected props
const initializeCheckboxStates = () => {
  const states: Record<string | number, boolean> = {};

  filterOptions.forEach(option => {
    const filterQueryParam = BOOKING_STATUS_TO_FILTER_QUERY_PARAM[option.value]
    states[option.value] = props.selected.includes(filterQueryParam);
  });

  checkboxStates.value = states;
};

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
};

const toggleOption = (option: SelectOption<number>) => {
  const newSelected = props.selected.map((option) => FILTER_QUERY_PARAM_TO_BOOKING_STATUS[option]);

  const index = newSelected.indexOf(option.value);

  if (index > -1) {
    newSelected.splice(index, 1);
  } else {
    newSelected.push(option.value);
  }

  // Update the checkbox state to match
  checkboxStates.value[option.value] = newSelected.includes(option.value);

  const filterQueryParams = newSelected.map((option) => BOOKING_STATUS_TO_FILTER_QUERY_PARAM[option])

  emit('update:selected', filterQueryParams);
};

// Display text for the pill
const displayText = computed(() => {
  if (props.selected.length === 0) {
    return t('label.all');
  }

  const selectedLabels = props.selected.map(value => {
    const bookingStatus = FILTER_QUERY_PARAM_TO_BOOKING_STATUS[value];
    const option = filterOptions.find(opt => opt.value === bookingStatus);

    return option ? option.label : String(value);
  });

  return selectedLabels.join(', ');
});

/*
*  Filters are defined in query params with router.replace
*  this happens _after_ the component has been mounted so we need
*  to listen to changes instead of using onMounted
*/
watch(
  () => props.selected,
  () => initializeCheckboxStates(),
  { immediate: true }
)
</script>

<template>
  <div class="filter-container" v-on-click-outside="closeDropdown">
    <!-- Pill trigger -->
    <button @click="toggleDropdown" class="filter-trigger" type="button">
      <span>{{ displayText }}</span>
      <icon-chevron-down class="chevron-icon" :class="{ 'rotated': isOpen }" />
    </button>

    <!-- Dropdown -->
    <fade-in-out-transition>
      <div v-show="isOpen" class="dropdown-menu">
        <div class="options-list">
          <div v-for="option in filterOptions" :key="option.value" class="option-item">
            <checkbox-input
              :name="`filter-${option.value}`"
              :label="option.label"
              v-model="checkboxStates[option.value]"
              @change="toggleOption(option)"
            />
          </div>
        </div>
      </div>
    </fade-in-out-transition>
  </div>
</template>

<style scoped>
.filter-container {
  position: relative;
}

.filter-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  background-color: var(--colour-neutral-lower);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--colour-ti-base);
  border: none;
  cursor: pointer;

  &:hover {
    background-color: var(--colour-neutral-border);
  }
}

.chevron-icon {
  height: 1rem;
  width: 1rem;

  &.rotated {
    transform: rotate(180deg);
  }
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  z-index: 50;
  margin-top: 0.5rem;
  min-width: 10rem;
  border-radius: 0.375rem;
  border: 1px solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-raised);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--colour-ti-muted);
  margin-bottom: 0.5rem;
  padding-left: 0.5rem;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
}

.option-item {
  padding: 0.375rem 0.5rem;
}

@media (prefers-reduced-motion: no-preference) {
  .filter-trigger {
    transition: background-color 0.2s;
  }

  .chevron-icon {
    transition: transform 0.2s;
  }
}
</style>
