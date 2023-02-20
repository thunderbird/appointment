<template>
  <div
    class="relative flex justify-between items-center w-full"
    :class="{
      'cursor-pointer': !disabled,
    }"
    @click.prevent="toggleState"
  >
    <div v-if="label">{{ label }}</div>
    <div class="flex gap-2">
      <div class="text-gray-500">{{ t('label.off') }}</div>
      <div class="w-10 h-5 shrink-0 rounded-full ease-in-out bg-gray-300 dark:bg-gray-600">
        <input type="checkbox" class="hidden peer" :checked="state" />
        <icon-circle-dot-filled
          class="w-5 h-5 rounded-full duration-300 peer-checked:translate-x-5 text-gray-400 dark:text-gray-300 peer-checked:text-teal-500"
        />
      </div>
      <div class="text-gray-500">{{ t('label.on') }}</div>
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

// component properties
const props = defineProps({
  active:   Boolean, // initial toggle state
  disabled: Boolean, // flag for making toggle non changable
  label:    String,  // input label
});

// current state
const state = ref(false);
onMounted(() => {
  state.value = props.active
});
const toggleState = () => {
  if (!props.disabled) {
    state.value = !state.value;
  }
}
</script>
