<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

// icons
import { IconCircleDotFilled } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component emits
const emit = defineEmits(['changed']);

// component properties
interface Props {
  active: boolean; // initial toggle state
  disabled: boolean; // flag for making toggle non changable
  label: string; // input label
  noLegend: boolean; // hide "on" and "off" labels
};
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
  <div
    class="relative flex items-center justify-between"
    :class="{
      'cursor-pointer': !disabled,
      'cursor-not-allowed': disabled,
    }"
    @click.prevent="toggleState"
  >
    <div v-if="label">{{ label }}</div>
    <div class="flex items-center gap-1.5">
      <div v-if="!noLegend" class="text-xs text-gray-500">{{ t('label.off') }}</div>
      <div
        class="h-4 w-8 shrink-0 rounded-full bg-gray-300 ease-in-out dark:bg-gray-700"
        :class="{ 'opacity-70': disabled }"
      >
        <input type="checkbox" class="peer hidden" :checked="state" />
        <icon-circle-dot-filled
          class="size-4 rounded-full text-gray-400 duration-300 peer-checked:translate-x-4 dark:text-gray-300"
          :class="{
            'peer-checked:text-teal-500': !disabled,
            'peer-checked:text-gray-400': disabled,
          }"
        />
      </div>
      <div v-if="!noLegend" class="text-xs text-gray-500">{{ t('label.on') }}</div>
    </div>
  </div>
</template>
