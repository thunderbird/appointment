<template>
  <div class="rounded-2xl bg-gray-200 dark:bg-gray-600">
    <nav class="flex">
      <ul class="flex justify-between w-full md:gap-4 p-1">
        <li
          v-for="(item, key) in tabItems"
          :key="item"
          class="flex whitespace-nowrap leading-8 px-8 transition-all ease-in-out hover:rounded-xl"
          :class="{
            'cursor-pointer': !disabled,
            'rounded-xl shadow dark:bg-gray-500': item == active,
            'text-gray-900 dark:text-white bg-white': item == active && !disabled,
            'text-gray-600 dark:text-gray-300 bg-gray-100': item == active && disabled,
            'text-gray-500 dark:text-gray-300': item != active,
            'hover:bg-gray-100 dark:hover:bg-gray-700': item != active && !disabled,
          }"
          @click="!disabled ? activate(key) : null"
        >
          {{ t('label.' + key) }}
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// component properties
defineProps({
  tabItems: Object, // list of tab items. Keys are used as lang keys (label.<key>), values as index
  active: Number, // value of active tab
  disabled: Boolean, // flag for making toggle non changable
});

// component emits
const emit = defineEmits(['update']);

// handle click events
const activate = (key) => {
  emit('update', key);
};
</script>
