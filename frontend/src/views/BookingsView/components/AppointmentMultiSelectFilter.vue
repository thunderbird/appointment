<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { vOnClickOutside } from '@vueuse/components';
import { useI18n } from 'vue-i18n';
import { IconChevronDown } from '@tabler/icons-vue';
import CheckboxInput from '@/tbpro/elements/CheckboxInput.vue';
import { SelectOption } from '@/models';
import FadeInOutTransition from '@/components/FadeInOutTransition.vue';

interface Props {
  options: SelectOption<string | number>[];
  selected: (string | number)[];
}

const { t } = useI18n();
const props = defineProps<Props>();
const emit = defineEmits(['update:selected']);

const isOpen = ref(false);

// Create a reactive object to track checkbox states
const checkboxStates = ref<Record<string | number, boolean>>({});

// Initialize checkbox states based on selected props
const initializeCheckboxStates = () => {
  const states: Record<string | number, boolean> = {};
  props.options.forEach(option => {
    states[option.value] = props.selected.includes(option.value);
  });
  checkboxStates.value = states;
};

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
};

const toggleOption = (option: SelectOption<string | number>) => {
  const newSelected = [...props.selected];
  const index = newSelected.indexOf(option.value);

  if (index > -1) {
    newSelected.splice(index, 1);
  } else {
    newSelected.push(option.value);
  }

  // Update the checkbox state to match
  checkboxStates.value[option.value] = newSelected.includes(option.value);

  emit('update:selected', newSelected);
};

// Display text for the pill
const displayText = computed(() => {
  if (props.selected.length === 0) {
    return t('label.all');
  }

  const selectedLabels = props.selected.map(value => {
    const option = props.options.find(opt => opt.value === value);
    return option ? option.label : String(value);
  });

  return selectedLabels.join(', ');
});

onMounted(() => {
  initializeCheckboxStates();
});
</script>

<template>
  <div class="filter-container" v-on-click-outside="closeDropdown">
    <!-- Pill trigger -->
    <button @click="toggleDropdown" class="filter-trigger" type="button">
      <span>{{ displayText }}</span>
      <IconChevronDown class="chevron-icon" :class="{ 'rotated': isOpen }" />
    </button>

    <!-- Dropdown -->
    <fade-in-out-transition>
      <div v-show="isOpen" class="dropdown-menu">
        <div class="options-list">
          <div v-for="option in options" :key="option.value" class="option-item">
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