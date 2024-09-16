<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

// component constants
const { t } = useI18n();

// component emits
const emit = defineEmits(['changed']);

// component properties
interface Props {
  active: boolean; // initial toggle state
  disabled?: boolean; // flag for making toggle non changable
  label?: string; // input label
  noLegend?: boolean; // hide "on" and "off" labels
}
const props = defineProps<Props>();

// current state
const state = ref(false);
onMounted(() => {
  state.value = props.active;
});
const toggleState = () => {
  if (!props.disabled) {
    state.value = !state.value;
    emit('changed', state.value);
  }
};
</script>

<template>
  <div class="component-container" @click.prevent="toggleState">
    <div v-if="label">{{ label }}</div>
    <div class="toggle-container">
      <div v-if="!noLegend" class="toggle-label">{{ t('label.off') }}</div>
      <div class="toggle">
        <input class="toggle-input" type="checkbox" :checked="state" :disabled="disabled" />
        <div class="toggle-handle"></div>
      </div>
      <div v-if="!noLegend" class="toggle-label">{{ t('label.on') }}</div>
    </div>
  </div>
</template>

<style scoped>
.component-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;

  &:has(.toggle-input:disabled) {
    cursor: not-allowed;
  }
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: .375rem;
}

.toggle-label {
  font-size: .75rem;
  line-height: 1rem;
  color: var(--colour-ti-secondary);
}

.toggle {
  background: var(--colour-form-base);
  width: 2rem;
  height: 1rem;
  flex-shrink: 0;
  border-radius: 9999px;

  &:has(.toggle-input:checked) {
    background: var(--colour-form-active);
  }

  &:has(.toggle-input:disabled) {
    opacity: 70%;
  }

  .toggle-input {
    display: none;

    &:checked ~ .toggle-handle {
      background-color: var(--colour-form-highlight);
      transform: translateX(1rem);
      border-color: var(--colour-form-active);
    }
  }

  .toggle-handle {
    background-color: var(--colour-form-inactive);
    width: 1rem;
    height: 1rem;
    box-sizing: border-box;
    border-radius: 9999px;
    transition: var(--transition-transform);
    border: 1px solid var(--colour-form-border-intense);
  }
}
</style>
