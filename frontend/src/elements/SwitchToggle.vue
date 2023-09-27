<template>
  <div
    class="relative flex justify-between items-center"
    :class="{
      'cursor-pointer': !disabled,
    }"
    @click.prevent="toggleState"
  >
    <div v-if="label">{{ label }}</div>
    <div class="flex gap-1.5 items-center">
      <div v-if="!noLegend" class="text-gray-500 text-xs">{{ t('label.off') }}</div>
      <div class="w-8 h-4 shrink-0 rounded-full ease-in-out bg-gray-300 dark:bg-gray-600">
        <input type="checkbox" class="hidden peer" :checked="state" />
        <icon-circle-dot-filled
          class="
            w-4 h-4 rounded-full duration-300 peer-checked:translate-x-4
            text-gray-400 dark:text-gray-300 peer-checked:text-teal-500
          "
        />
      </div>
      <div v-if="!noLegend" class="text-gray-500 text-xs">{{ t('label.on') }}</div>
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
const emit = defineEmits(["changed"]);

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
    emit("changed", state.value);
  }
};
</script>
