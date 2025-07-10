<script setup lang="ts">
import { ref, computed } from 'vue';
import { vOnClickOutside } from '@vueuse/components';
import { useI18n } from 'vue-i18n';
import { IconChevronDown } from '@tabler/icons-vue';

interface FilterOption {
  value: string | number;
  label: string;
}

interface Props {
  options: FilterOption[];
  selected: (string | number)[];
}

const { t } = useI18n();
const props = defineProps<Props>();
const emit = defineEmits(['update:selected']);

const isOpen = ref(false);

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
};

const toggleOption = (option: FilterOption) => {
  const newSelected = [...props.selected];
  const index = newSelected.indexOf(option.value);

  if (index > -1) {
    newSelected.splice(index, 1);
  } else {
    newSelected.push(option.value);
  }

  emit('update:selected', newSelected);
};

const isSelected = (option: FilterOption) => {
  return props.selected.includes(option.value);
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
</script>

<template>
  <div class="filter-container" v-on-click-outside="closeDropdown">
    <!-- Pill trigger -->
    <button @click="toggleDropdown" class="filter-trigger" type="button">
      <span>{{ displayText }}</span>
      <IconChevronDown class="chevron-icon" :class="{ 'rotated': isOpen }" />
    </button>

    <!-- Dropdown -->
    <transition enter-active-class="dropdown-enter-active" enter-from-class="dropdown-enter-from"
      enter-to-class="dropdown-enter-to" leave-active-class="dropdown-leave-active"
      leave-from-class="dropdown-leave-from" leave-to-class="dropdown-leave-to">
      <div v-show="isOpen" class="dropdown-menu">
        <div class="dropdown-content">
          <div class="filter-label">
            {{ t('label.filter') }}
          </div>
          <div class="options-list">
            <label v-for="option in options" :key="option.value" class="option-item">
              <input type="checkbox" :checked="isSelected(option)" @change="toggleOption(option)"
                class="option-checkbox" />
              <span class="option-label">{{ option.label }}</span>
            </label>
          </div>
        </div>
      </div>
    </transition>
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
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--colour-neutral-border);
  }
}

.chevron-icon {
  height: 1rem;
  width: 1rem;
  transition: transform 0.2s;
}

.chevron-icon.rotated {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  z-index: 50;
  margin-top: 0.5rem;
  min-width: 12rem;
  border-radius: 0.375rem;
  border: 1px solid var(--colour-neutral-border);
  background-color: var(--colour-neutral-raised);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.dropdown-content {
  padding: 0.5rem;
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
}

.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 0.25rem;
  padding: 0.375rem 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--colour-neutral-subtle);
  }
}

.option-checkbox {
  height: 1rem;
  width: 1rem;
  border-radius: 0.25rem;
  border: 1px solid var(--colour-neutral-border);
  color: var(--colour-primary-default);
  cursor: pointer;

  &:focus {
    outline: 2px solid var(--colour-primary-default);
    outline-offset: 2px;
  }
}

.option-label {
  flex: 1;
  color: var(--colour-ti-base);
}

/* Transition classes */
.dropdown-enter-active {
  transition: all 0.2s ease-out;
}

.dropdown-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.dropdown-enter-to {
  opacity: 1;
  transform: scale(1);
}

.dropdown-leave-active {
  transition: all 0.15s ease-in;
}

.dropdown-leave-from {
  opacity: 1;
  transform: scale(1);
}

.dropdown-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>