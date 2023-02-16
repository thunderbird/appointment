<template>
  <div
    class="relative flex justify-between items-center w-full"
    :class="{
      'cursor-pointer': !disabled,
    }"
    @click="!disabled ? state = !state : null"
  >
    <div v-if="label">{{ label }}</div>
    <div class="flex gap-2">
      <div class="text-gray-500">{{ t('label.off') }}</div>
      <div class="w-10 h-5 shrink-0 bg-gray-300 rounded-full ease-in-out">
        <input type="checkbox" class="hidden peer" :checked="state" />
        <icon-circle-dot-filled class="w-5 h-5 rounded-full text-gray-400 peer-checked:text-teal-500 duration-300 peer-checked:translate-x-5" />
      </div>
      <div class="text-gray-500">{{ t('label.on') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

// icons
import { IconCircleDotFilled } from '@tabler/icons-vue';

// component constants
const { t } = useI18n();

// component properties
const props = defineProps({
  active:   Boolean, // toggle state
  disabled: Boolean, // flag for making toggle non changable
  label:    String,  // input label
});

// current state
const state = ref(props.active);
</script>
