<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';

// component constants
const { t } = useI18n();

// component emits
const emit = defineEmits(['changed']);

// component properties
interface Props {
  name: string;
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

// Update state if parent changes active prop
// e.g. after initializing async data
watch(
  () => props.active,
  () => {
    state.value = props.active;
  }
);
</script>

<template>
  <div class="component-container" @click.prevent="toggleState">
    <div v-if="label" class="input-label">{{ label }}</div>
    <div class="toggle-container">
      <div v-if="!noLegend" class="toggle-label">{{ t('label.off') }}</div>
      <div class="toggle">
        <input class="toggle-input" type="checkbox" :name="name" :checked="state" :disabled="disabled" />
        <div class="toggle-handle"></div>
      </div>
      <div v-if="!noLegend" class="toggle-label">{{ t('label.on') }}</div>
    </div>
  </div>
</template>

<style scoped>
.component-container {
  /* Colour definitions */
  --colour-base: #E4E4E7;
  --colour-active: #008080;
  --colour-inactive: #FEFFFF;
  --colour-highlight: #FEFFFF;
  --colour-border-intense: #777580;
  
  html.dark & {
    --colour-base: #737584;
    --colour-active: #A3ECE3;
    --colour-inactive: #FEFFFF;
    --colour-highlight: #1A202C;
    --colour-border-intense: #777580;
  }

  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;

  &:has(.toggle-input:disabled) {
    cursor: not-allowed;
  }
}

.input-label {
  color: var(--colour-ti-base);
  font-family: var(--font-sans);
  font-size: var(--txt-input);
  line-height: var(--line-height-input);
  width: 100%;
  font-weight: 500;  
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: .375rem;
}

.toggle-label {
  font-size: .75rem;
  line-height: 1rem;
  color: var(--colour-secondary);
}

.toggle {
  background: var(--colour-base);
  width: 2rem;
  height: 1rem;
  flex-shrink: 0;
  border-radius: 9999px;

  &:has(.toggle-input:checked) {
    background: var(--colour-active);
  }

  &:has(.toggle-input:disabled) {
    opacity: 70%;
  }

  .toggle-input {
    display: none;

    &:checked ~ .toggle-handle {
      background-color: var(--colour-highlight);
      transform: translateX(1rem);
      border-color: var(--colour-active);
    }
  }

  .toggle-handle {
    background-color: var(--colour-inactive);
    width: 1rem;
    height: 1rem;
    box-sizing: border-box;
    border-radius: 9999px;
    transition: var(--transition-transform);
    border: 1px solid var(--colour-border-intense);
  }
}
</style>
