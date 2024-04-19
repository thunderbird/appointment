<template>
  <div
    class="relative flex items-center justify-between"
    :class="{
      'cursor-pointer': !disabled,
    }"
    @click.prevent="toggleState"
  >
    <div v-if="label">{{ label }}</div>
    <div class="flex items-center gap-1.5">
      <div v-if="!noLegend" class="text-xs text-gray-500">{{ t('label.off') }}</div>
      <div class="h-4 w-8 shrink-0 rounded-full bg-gray-300 ease-in-out dark:bg-gray-700">
        <input type="checkbox" class="peer hidden" :checked="state" />
        <icon-circle-dot-filled
          class="size-4 rounded-full text-gray-400 duration-300 peer-checked:translate-x-4 peer-checked:text-teal-500 dark:text-gray-300"
        />
      </div>
      <div v-if="!noLegend" class="text-xs text-gray-500">{{ t('label.on') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

// icons
import { IconCircleDotFilled } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component emits
const emit = defineEmits(['changed']);

// component properties
const props = defineProps({
  active: Boolean, // initial toggle state
  disabled: Boolean, // flag for making toggle non changable
  label: String, // input label
  noLegend: Boolean, // hide "on" and "off" labels
});

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
